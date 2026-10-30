from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .. import services
from ..forms import ConfirmNameForm, ProfileForm, RewardRequestForm, SignupForm
from ..models import (
    AttemptAnswer,
    Certificate,
    Course,
    Enrollment,
    ExamAttempt,
    Lesson,
    LessonProgress,
    Module,
    Question,
    RewardClaim,
)

VERIFY_SALT = "academy.email-verify"


def published_courses():
    return Course.objects.filter(status=Course.Status.PUBLISHED)


def visible_course(request, slug):
    """Les formations non publiées ne sont visibles que de l'équipe."""
    qs = Course.objects.all() if request.user.is_staff else published_courses()
    return get_object_or_404(qs, slug=slug)


# ------------------------------------------------------------------ Public
def home(request):
    courses = published_courses().prefetch_related("modules__lessons")
    cards = []
    for course in courses:
        lessons = course.ordered_lessons()
        cards.append(
            {
                "course": course,
                "modules": course.modules.count(),
                "lessons": len(lessons),
                "progress": services.course_progress(request.user, course) if request.user.is_authenticated else None,
                "offer": services.live_offer_for(course),
            }
        )
    return render(request, "learning/home.html", {"cards": cards})


def course_detail(request, slug):
    course = visible_course(request, slug)
    modules = course.modules.prefetch_related(Prefetch("lessons", queryset=Lesson.objects.order_by("position", "id")))
    progress = services.course_progress(request.user, course)
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).select_related("last_lesson").first()
    first_lesson = progress["lessons"][0] if progress["lessons"] else None
    return render(
        request,
        "learning/course_detail.html",
        {
            "course": course,
            "modules": modules,
            "progress": progress,
            "enrollment": enrollment,
            "first_lesson": first_lesson,
            "question_count": course.questions.count(),
            "offer": services.live_offer_for(course),
            "certificate": Certificate.objects.filter(user=request.user, course=course).first() if request.user.is_authenticated else None,
        },
    )


# ------------------------------------------------------------------ Comptes
def send_verification_email(request, user):
    token = signing.dumps({"u": user.pk, "e": user.email}, salt=VERIFY_SALT)
    link = services.base_url() + reverse("verify_email", args=[token])
    send_mail(
        "Confirmez votre adresse e-mail — Flux Intelligent Academy",
        f"Bonjour {user.profile.full_name},\n\nConfirmez votre adresse e-mail en ouvrant ce lien (valable 3 jours) :\n{link}\n\n"
        "Si vous n'êtes pas à l'origine de cette inscription, ignorez ce message.\n\nFlux Intelligent Academy",
        None,
        [user.email],
    )


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    next_url = request.GET.get("next") or request.POST.get("next") or ""
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="learning.auth.EmailBackend")
        send_verification_email(request, user)
        messages.success(request, "Votre compte est créé. Un lien de confirmation vient d'être envoyé à votre adresse e-mail.")
        if next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form, "next": next_url})


def verify_email(request, token):
    try:
        data = signing.loads(token, salt=VERIFY_SALT, max_age=60 * 60 * 24 * 3)
    except signing.BadSignature:
        messages.error(request, "Ce lien de confirmation est invalide ou a expiré. Demandez-en un nouveau depuis votre profil.")
        return redirect("profile" if request.user.is_authenticated else "login")
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.filter(pk=data.get("u"), email=data.get("e")).first()
    if user is None:
        messages.error(request, "Ce lien ne correspond plus à l'adresse de votre compte.")
        return redirect("home")
    if not user.profile.email_verified:
        user.profile.email_verified_at = timezone.now()
        user.profile.save(update_fields=["email_verified_at"])
    messages.success(request, "Votre adresse e-mail est confirmée.")
    return redirect("dashboard" if request.user.is_authenticated else "login")


@login_required
@require_POST
def resend_verification(request):
    if not request.user.profile.email_verified:
        send_verification_email(request, request.user)
        messages.success(request, "Un nouveau lien de confirmation vient d'être envoyé.")
    return redirect("profile")


@login_required
def profile(request):
    user = request.user
    form = ProfileForm(request.POST or None, user=user, initial={"full_name": user.profile.full_name, "email": user.email})
    if request.method == "POST" and form.is_valid():
        email_changed = form.cleaned_data["email"] != user.email.lower()
        user.profile.full_name = form.cleaned_data["full_name"].strip()
        if email_changed:
            user.email = form.cleaned_data["email"]
            user.username = form.cleaned_data["email"]
            user.save(update_fields=["email", "username"])
            user.profile.email_verified_at = None
        user.profile.save()
        if email_changed:
            send_verification_email(request, user)
            messages.info(request, "Votre adresse a changé : confirmez-la grâce au lien envoyé.")
        messages.success(request, "Profil mis à jour.")
        return redirect("profile")
    return render(request, "learning/profile.html", {"form": form})


# ------------------------------------------------------------------ Espace apprenant
@login_required
def dashboard(request):
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related("course", "last_lesson").order_by("-last_activity_at")
    in_progress, completed = [], []
    for e in enrollments:
        p = services.course_progress(user, e.course)
        cert = Certificate.objects.filter(user=user, course=e.course).first()
        row = {"enrollment": e, "course": e.course, "progress": p, "certificate": cert,
               "passed": ExamAttempt.objects.filter(user=user, course=e.course, passed=True).exists()}
        (completed if row["passed"] else in_progress).append(row)
    attempts = ExamAttempt.objects.filter(user=user, submitted_at__isnull=False).select_related("course")
    certificates = Certificate.objects.filter(user=user).select_related("course")
    claims = RewardClaim.objects.filter(user=user).select_related("course", "offer")
    return render(
        request,
        "learning/dashboard.html",
        {"in_progress": in_progress, "completed": completed, "attempts": attempts, "certificates": certificates, "claims": claims},
    )


@login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(published_courses(), slug=slug)
    enrollment = services.enroll(request.user, course)
    target = enrollment.last_lesson or (course.ordered_lessons() or [None])[0]
    if target is None:
        messages.info(request, "Cette formation ne contient pas encore de leçon.")
        return redirect(course)
    return redirect(target)


@login_required
def resume(request, slug):
    course = visible_course(request, slug)
    enrollment = services.enroll(request.user, course)
    progress = services.course_progress(request.user, course)
    if enrollment.last_lesson_id:
        return redirect(enrollment.last_lesson)
    for lesson in progress["lessons"]:
        if lesson.id not in progress["completed_ids"]:
            return redirect(lesson)
    if progress["lessons"]:
        return redirect(progress["lessons"][0])
    return redirect(course)


@login_required
def lesson_view(request, slug, lesson_slug):
    course = visible_course(request, slug)
    lesson = get_object_or_404(Lesson.objects.select_related("module"), module__course=course, slug=lesson_slug)
    enrollment = services.enroll(request.user, course)
    Enrollment.objects.filter(pk=enrollment.pk).update(last_lesson=lesson, last_activity_at=timezone.now())

    progress = services.course_progress(request.user, course)
    lessons = progress["lessons"]
    index = next(i for i, l in enumerate(lessons) if l.id == lesson.id)
    modules = course.modules.prefetch_related(Prefetch("lessons", queryset=Lesson.objects.order_by("position", "id")))
    exam_allowed, exam_reason = services.can_take_exam(request.user, course)
    return render(
        request,
        "learning/lesson.html",
        {
            "course": course,
            "lesson": lesson,
            "modules": modules,
            "progress": progress,
            "prev_lesson": lessons[index - 1] if index > 0 else None,
            "next_lesson": lessons[index + 1] if index + 1 < len(lessons) else None,
            "position": index + 1,
            "is_done": lesson.id in progress["completed_ids"],
            "exam_allowed": exam_allowed,
            "exam_reason": exam_reason,
        },
    )


@login_required
@require_POST
def lesson_complete(request, slug, lesson_slug):
    course = visible_course(request, slug)
    lesson = get_object_or_404(Lesson, module__course=course, slug=lesson_slug)
    services.enroll(request.user, course)
    if request.POST.get("undo") == "1":
        LessonProgress.objects.filter(user=request.user, lesson=lesson).delete()
        return redirect(lesson)
    LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    progress = services.course_progress(request.user, course)
    lessons = progress["lessons"]
    index = next(i for i, l in enumerate(lessons) if l.id == lesson.id)
    if progress["done"] == progress["total"]:
        messages.success(request, "Bravo, vous avez terminé toutes les leçons. L'examen final est débloqué.")
        return redirect("exam_intro", slug=course.slug)
    if index + 1 < len(lessons):
        return redirect(lessons[index + 1])
    return redirect(lesson)


# ------------------------------------------------------------------ Examen
@login_required
def exam_intro(request, slug):
    course = visible_course(request, slug)
    allowed, reason = services.can_take_exam(request.user, course)
    return render(
        request,
        "learning/exam_intro.html",
        {
            "course": course,
            "allowed": allowed,
            "reason": reason,
            "question_count": course.questions.count(),
            "attempts_used": services.attempts_used(request.user, course),
            "attempts_left": services.attempts_left(request.user, course),
            "last_attempt": ExamAttempt.objects.filter(user=request.user, course=course, submitted_at__isnull=False).first(),
            "progress": services.course_progress(request.user, course),
            "offer": services.live_offer_for(course),
        },
    )


@login_required
def exam_take(request, slug):
    course = visible_course(request, slug)
    if request.method == "POST":
        attempt = get_object_or_404(
            ExamAttempt, pk=request.POST.get("attempt"), user=request.user, course=course
        )
        answers = {}
        for qid in attempt.question_ids:
            raw = request.POST.get(f"q{qid}")
            if raw and raw.isdigit():
                answers[qid] = int(raw)
        attempt, _ = services.submit_attempt(attempt.pk, request.user, answers)
        return redirect("exam_result", slug=course.slug, number=attempt.number)

    try:
        attempt = services.start_attempt(request.user, course)
    except services.ExamNotAllowed as exc:
        messages.error(request, str(exc))
        return redirect("exam_intro", slug=course.slug)
    questions = list(
        Question.objects.filter(id__in=attempt.question_ids).prefetch_related("choices")
    )
    order = {qid: i for i, qid in enumerate(attempt.question_ids)}
    questions.sort(key=lambda q: order.get(q.id, 0))
    # Les choix sont envoyés sans l'information « bonne réponse ».
    payload = [
        {"id": q.id, "text": q.text, "kind": q.get_kind_display(),
         "choices": [{"id": c.id, "text": c.text} for c in q.choices.all()]}
        for q in questions
    ]
    return render(request, "learning/exam_take.html", {"course": course, "attempt": attempt, "questions": payload})


@login_required
def exam_result(request, slug, number):
    course = visible_course(request, slug)
    attempt = get_object_or_404(
        ExamAttempt, user=request.user, course=course, number=number, submitted_at__isnull=False
    )
    answers = {
        a.question_id: a
        for a in AttemptAnswer.objects.filter(attempt=attempt).select_related("choice", "question__related_lesson__module")
    }
    questions = list(Question.objects.filter(id__in=attempt.question_ids).prefetch_related("choices").select_related("related_lesson"))
    order = {qid: i for i, qid in enumerate(attempt.question_ids)}
    questions.sort(key=lambda q: order.get(q.id, 0))
    correction, review = [], {}
    for q in questions:
        a = answers.get(q.id)
        right = q.correct_choice()
        ok = bool(a and a.is_correct)
        correction.append({"question": q, "given": a.choice if a else None, "right": right, "ok": ok})
        if not ok and q.related_lesson:
            review[q.related_lesson.id] = q.related_lesson
    certificate = Certificate.objects.filter(user=request.user, course=course).first()
    claim = services.eligible_claim_for(request.user, course) if attempt.is_perfect else None
    allowed, reason = services.can_take_exam(request.user, course)
    return render(
        request,
        "learning/exam_result.html",
        {
            "course": course,
            "attempt": attempt,
            "correction": correction,
            "review_lessons": list(review.values()),
            "certificate": certificate,
            "can_retry": allowed,
            "retry_reason": reason,
            "claim": claim,
            "offer": services.live_offer_for(course),
            "reward_missing": services.reward_conditions(request.user, attempt) if attempt.is_perfect else [],
        },
    )


# ------------------------------------------------------------------ Certificats
@login_required
def certificate_claim(request, slug):
    """Confirmation du nom avant la première émission, puis délivrance."""
    course = visible_course(request, slug)
    existing = Certificate.objects.filter(user=request.user, course=course).first()
    if existing:
        return redirect("certificate_download", number=existing.number)
    if services.best_passing_attempt(request.user, course) is None:
        messages.error(request, "Le certificat est délivré après la réussite de l'examen final.")
        return redirect("exam_intro", slug=course.slug)
    form = ConfirmNameForm(request.POST or None, initial={"full_name": request.user.profile.full_name})
    if request.method == "POST" and form.is_valid():
        try:
            cert, _ = services.issue_certificate(request.user, course, form.cleaned_data["full_name"])
        except services.CertificateNotAllowed as exc:
            messages.error(request, str(exc))
            return redirect("exam_intro", slug=course.slug)
        messages.success(request, f"Votre certificat n° {cert.number} est prêt.")
        return redirect("certificate_ready", number=cert.number)
    return render(request, "learning/certificate_confirm.html", {"course": course, "form": form})


@login_required
def certificate_ready(request, number):
    cert = get_object_or_404(Certificate, number=number, user=request.user)
    return render(request, "learning/certificate_ready.html", {"cert": cert, "claim": RewardClaim.objects.filter(user=request.user, course=cert.course).first()})


@login_required
def certificate_download(request, number):
    # Filtrer par propriétaire : un autre apprenant (ou un numéro deviné) obtient un 404.
    qs = Certificate.objects.all() if request.user.is_staff else Certificate.objects.filter(user=request.user)
    cert = get_object_or_404(qs, number=number)
    path = Path(settings.PRIVATE_ROOT) / cert.pdf_path if cert.pdf_path else None
    if not path or not path.exists():
        from ..models import SiteSettings
        from ..pdf import render_certificate_pdf

        cert.pdf_path = render_certificate_pdf(cert, SiteSettings.load())
        cert.save(update_fields=["pdf_path"])
        path = Path(settings.PRIVATE_ROOT) / cert.pdf_path
    inline = request.GET.get("inline") == "1"
    return FileResponse(
        open(path, "rb"),
        as_attachment=not inline,
        filename=f"Certificat-{cert.number}.pdf",
        content_type="application/pdf",
    )


def certificate_verify(request, verify_id):
    cert = Certificate.objects.filter(verify_id=verify_id).select_related("course").first()
    if cert is None:
        return render(request, "learning/certificate_verify.html", {"cert": None}, status=404)
    parts = cert.full_name.split()
    holder = parts[0] + (" " + parts[-1][0] + "." if len(parts) > 1 else "")
    return render(request, "learning/certificate_verify.html", {"cert": cert, "holder": holder})


# ------------------------------------------------------------------ Récompense Claude Pro
@login_required
def reward_claim(request, claim_id):
    claim = get_object_or_404(RewardClaim, pk=claim_id, user=request.user)
    if claim.status != RewardClaim.Status.ELIGIBLE:
        return redirect("reward_status", claim_id=claim.pk)
    form = RewardRequestForm(
        request.POST or None, initial={"full_name": request.user.profile.full_name, "email": request.user.email}
    )
    if request.method == "POST" and form.is_valid():
        services.request_reward(request.user, claim.pk, form.cleaned_data["full_name"], form.cleaned_data["email"])
        messages.success(request, "Votre demande est enregistrée. Retrouvez son avancement dans votre espace personnel.")
        return redirect("reward_status", claim_id=claim.pk)
    return render(request, "learning/reward_claim.html", {"claim": claim, "form": form, "offer": claim.offer})


@login_required
def reward_status(request, claim_id):
    claim = get_object_or_404(RewardClaim.objects.select_related("offer", "course"), pk=claim_id, user=request.user)
    certificate = Certificate.objects.filter(user=request.user, course=claim.course).first()
    return render(request, "learning/reward_status.html", {"claim": claim, "offer": claim.offer, "certificate": certificate})


def offer_terms(request, slug):
    course = visible_course(request, slug)
    offer = services.live_offer_for(course)
    if offer is None and not request.user.is_staff:
        raise Http404
    from ..models import RewardOffer

    offer = offer or RewardOffer.objects.filter(course=course).first()
    if offer is None:
        raise Http404
    return render(request, "learning/offer_terms.html", {"course": course, "offer": offer})
