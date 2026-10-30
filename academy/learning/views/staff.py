"""
Espace administrateur (« /gestion/ »). Chaque vue exige un compte membre de
l'équipe (is_staff), vérifié côté serveur par le décorateur staff_required.
"""
import secrets
from functools import wraps
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .. import services
from ..forms import (
    ChoiceForm,
    CourseForm,
    LessonForm,
    ModuleForm,
    QuestionForm,
    RewardClaimAdminForm,
    RewardOfferForm,
    SiteSettingsForm,
)
from ..models import (
    AdminAuditLog,
    Certificate,
    Choice,
    Course,
    Enrollment,
    ExamAttempt,
    Lesson,
    Module,
    Question,
    RewardClaim,
    RewardOffer,
    SiteSettings,
)


def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_active and request.user.is_staff):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


def audit(request, action, target=""):
    AdminAuditLog.objects.create(actor=request.user, action=action, target=str(target)[:200])


# ------------------------------------------------------------------ Tableau de bord
@staff_required
def overview(request):
    User = get_user_model()
    stats = {
        "courses": Course.objects.count(),
        "published": Course.objects.filter(status=Course.Status.PUBLISHED).count(),
        "learners": User.objects.filter(is_staff=False).count(),
        "attempts": ExamAttempt.objects.filter(submitted_at__isnull=False).count(),
        "certificates": Certificate.objects.count(),
        "rewards_pending": RewardClaim.objects.exclude(status=RewardClaim.Status.DELIVERED).count(),
    }
    recent = ExamAttempt.objects.filter(submitted_at__isnull=False).select_related("user__profile", "course")[:10]
    return render(request, "staff/overview.html", {"stats": stats, "recent": recent})


# ------------------------------------------------------------------ Formations
@staff_required
def course_list(request):
    courses = Course.objects.annotate(
        n_modules=Count("modules", distinct=True),
        n_questions=Count("questions", distinct=True),
        n_enrolled=Count("enrollments", distinct=True),
    )
    return render(request, "staff/course_list.html", {"courses": courses})


@staff_required
def course_edit(request, pk=None):
    course = get_object_or_404(Course, pk=pk) if pk else None
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == "POST" and form.is_valid():
        course = form.save()
        audit(request, "Formation enregistrée", course)
        messages.success(request, "Formation enregistrée.")
        return redirect("staff_course_content", pk=course.pk)
    return render(request, "staff/course_form.html", {"form": form, "course": course})


@staff_required
@require_POST
def course_status(request, pk):
    course = get_object_or_404(Course, pk=pk)
    status = request.POST.get("status")
    if status in Course.Status.values:
        if status == Course.Status.PUBLISHED and not course.ordered_lessons():
            messages.error(request, "Ajoutez au moins une leçon avant de publier.")
        else:
            course.status = status
            course.save(update_fields=["status", "updated_at"])
            audit(request, f"Statut → {course.get_status_display()}", course)
            messages.success(request, f"Formation « {course.title} » : {course.get_status_display().lower()}.")
    return redirect(request.POST.get("next") or "staff_courses")


@staff_required
def course_content(request, pk):
    course = get_object_or_404(Course, pk=pk)
    modules = course.modules.prefetch_related("lessons")
    module_form = ModuleForm()
    return render(
        request,
        "staff/course_content.html",
        {"course": course, "modules": modules, "module_form": module_form, "questions": course.questions.count()},
    )


@staff_required
@require_POST
def module_save(request, course_pk, pk=None):
    course = get_object_or_404(Course, pk=course_pk)
    module = get_object_or_404(Module, pk=pk, course=course) if pk else Module(course=course)
    form = ModuleForm(request.POST, instance=module)
    if form.is_valid():
        if not pk:
            module.position = (course.modules.order_by("-position").values_list("position", flat=True).first() or 0) + 1
        form.save()
        messages.success(request, "Module enregistré.")
    return redirect("staff_course_content", pk=course.pk)


@staff_required
@require_POST
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    course = module.course
    if module.lessons.filter(progress__isnull=False).exists():
        messages.error(request, "Ce module contient des leçons déjà suivies par des apprenants : déplacez-les ou archivez la formation.")
    else:
        audit(request, "Module supprimé", module)
        module.delete()
        messages.success(request, "Module supprimé.")
    return redirect("staff_course_content", pk=course.pk)


def _move(obj, siblings, direction):
    items = list(siblings)
    for i, item in enumerate(items):
        item.position = i
    idx = next(i for i, it in enumerate(items) if it.pk == obj.pk)
    swap = idx - 1 if direction == "up" else idx + 1
    if 0 <= swap < len(items):
        items[idx].position, items[swap].position = items[swap].position, items[idx].position
    with transaction.atomic():
        for it in items:
            type(it).objects.filter(pk=it.pk).update(position=it.position)


@staff_required
@require_POST
def module_move(request, pk, direction):
    module = get_object_or_404(Module, pk=pk)
    _move(module, module.course.modules.order_by("position", "id"), direction)
    return redirect("staff_course_content", pk=module.course_id)


@staff_required
def lesson_edit(request, course_pk, pk=None):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=pk, module__course=course) if pk else None
    initial = {}
    if lesson is None and request.GET.get("module"):
        initial["module"] = request.GET.get("module")
    form = LessonForm(request.POST or None, instance=lesson, course=course, initial=initial)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        if lesson is None:
            obj.position = (obj.module.lessons.order_by("-position").values_list("position", flat=True).first() or 0) + 1
        obj.save()
        audit(request, "Leçon enregistrée", obj)
        messages.success(request, "Leçon enregistrée.")
        if "continue" in request.POST:
            return redirect("staff_lesson_edit", course_pk=course.pk, pk=obj.pk)
        return redirect("staff_course_content", pk=course.pk)
    return render(request, "staff/lesson_form.html", {"course": course, "lesson": lesson, "form": form})


@staff_required
@require_POST
def lesson_move(request, pk, direction):
    lesson = get_object_or_404(Lesson, pk=pk)
    _move(lesson, lesson.module.lessons.order_by("position", "id"), direction)
    return redirect("staff_course_content", pk=lesson.module.course_id)


@staff_required
@require_POST
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course_pk = lesson.module.course_id
    if lesson.progress.exists():
        messages.error(request, "Cette leçon a déjà été suivie : elle ne peut pas être supprimée (archivez plutôt la formation).")
    else:
        audit(request, "Leçon supprimée", lesson)
        lesson.delete()
        messages.success(request, "Leçon supprimée.")
    return redirect("staff_course_content", pk=course_pk)


ALLOWED_IMAGE_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}


@staff_required
@require_POST
def editor_upload(request):
    """Téléversement d'une image depuis l'éditeur de leçon (images uniquement, 5 Mo max)."""
    f = request.FILES.get("image")
    if not f or f.content_type not in ALLOWED_IMAGE_TYPES or f.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "Image PNG, JPG, WEBP ou GIF de 5 Mo maximum."}, status=400)
    try:
        from PIL import Image

        Image.open(f).verify()
        f.seek(0)
    except Exception:
        return JsonResponse({"error": "Fichier image illisible."}, status=400)
    folder = Path(settings.MEDIA_ROOT) / "lessons"
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{timezone.now():%Y%m}-{secrets.token_hex(6)}{ALLOWED_IMAGE_TYPES[f.content_type]}"
    with open(folder / name, "wb") as out:
        for chunk in f.chunks():
            out.write(chunk)
    return JsonResponse({"url": f"{settings.MEDIA_URL}lessons/{name}"})


# ------------------------------------------------------------------ Examen
@staff_required
def question_list(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    questions = course.questions.prefetch_related("choices").select_related("related_lesson")
    return render(request, "staff/question_list.html", {"course": course, "questions": questions})


@staff_required
def question_edit(request, course_pk, pk=None):
    course = get_object_or_404(Course, pk=course_pk)
    question = get_object_or_404(Question, pk=pk, course=course) if pk else None
    existing = list(question.choices.all()) if question else []
    n_slots = max(4, len(existing))
    form = QuestionForm(request.POST or None, instance=question, course=course)
    choice_forms = []
    for i in range(n_slots):
        init = {"text": existing[i].text} if i < len(existing) else {}
        choice_forms.append(ChoiceForm(request.POST or None, prefix=f"c{i}", initial=init))
    correct_index = next((i for i, c in enumerate(existing) if c.is_correct), None)
    error = None

    if request.method == "POST" and form.is_valid() and all(cf.is_valid() for cf in choice_forms):
        kind = form.cleaned_data["kind"]
        if kind == Question.Kind.TRUE_FALSE:
            texts = ["Vrai", "Faux"]
        else:
            texts = [cf.cleaned_data["text"].strip() for cf in choice_forms if cf.cleaned_data["text"].strip()]
        raw_correct = request.POST.get("correct", "")
        if kind == Question.Kind.TRUE_FALSE:
            correct = 0 if raw_correct in ("0", "true") else 1 if raw_correct in ("1", "false") else None
        else:
            filled = [i for i, cf in enumerate(choice_forms) if cf.cleaned_data["text"].strip()]
            correct = filled.index(int(raw_correct)) if raw_correct.isdigit() and int(raw_correct) in filled else None
        if len(texts) < 2:
            error = "Saisissez au moins deux réponses."
        elif correct is None:
            error = "Indiquez la bonne réponse."
        else:
            with transaction.atomic():
                q = form.save(commit=False)
                q.course = course
                if question is None:
                    q.position = (course.questions.order_by("-position").values_list("position", flat=True).first() or 0) + 1
                q.save()
                # Les réponses existantes sont mises à jour en place pour garder l'historique des tentatives.
                current = list(q.choices.all())
                for i, text in enumerate(texts):
                    if i < len(current):
                        Choice.objects.filter(pk=current[i].pk).update(text=text, is_correct=(i == correct), position=i)
                    else:
                        Choice.objects.create(question=q, text=text, is_correct=(i == correct), position=i)
                for extra in current[len(texts):]:
                    extra.delete()
            audit(request, "Question enregistrée", q)
            messages.success(request, "Question enregistrée.")
            if "add_another" in request.POST:
                return redirect("staff_question_new", course_pk=course.pk)
            return redirect("staff_questions", course_pk=course.pk)
    return render(
        request,
        "staff/question_form.html",
        {"course": course, "question": question, "form": form, "choice_forms": choice_forms,
         "correct_index": correct_index, "error": error},
    )


@staff_required
@require_POST
def question_delete(request, pk):
    q = get_object_or_404(Question, pk=pk)
    course_pk = q.course_id
    audit(request, "Question supprimée", q)
    q.delete()
    messages.success(request, "Question supprimée. Les tentatives passées conservent leur note.")
    return redirect("staff_questions", course_pk=course_pk)


@staff_required
@require_POST
def question_move(request, pk, direction):
    q = get_object_or_404(Question, pk=pk)
    _move(q, q.course.questions.order_by("position", "id"), direction)
    return redirect("staff_questions", course_pk=q.course_id)


# ------------------------------------------------------------------ Apprenants et résultats
@staff_required
def learner_list(request):
    query = request.GET.get("q", "").strip()
    enrollments = Enrollment.objects.select_related("user__profile", "course").order_by("-last_activity_at")
    if query:
        enrollments = enrollments.filter(
            Q(user__email__icontains=query) | Q(user__profile__full_name__icontains=query) | Q(course__title__icontains=query)
        )
    rows = []
    for e in enrollments[:300]:
        p = services.course_progress(e.user, e.course)
        attempts = ExamAttempt.objects.filter(user=e.user, course=e.course, submitted_at__isnull=False)
        best = max(attempts, key=lambda a: a.score20, default=None)
        rows.append({"e": e, "progress": p, "attempts": attempts.count(), "best": best,
                     "cert": Certificate.objects.filter(user=e.user, course=e.course).first()})
    return render(request, "staff/learner_list.html", {"rows": rows, "query": query})


@staff_required
def result_list(request):
    attempts = ExamAttempt.objects.filter(submitted_at__isnull=False).select_related("user__profile", "course")[:500]
    return render(request, "staff/result_list.html", {"attempts": attempts})


@staff_required
def certificate_list(request):
    certs = Certificate.objects.select_related("user", "course")
    return render(request, "staff/certificate_list.html", {"certs": certs})


@staff_required
@require_POST
def certificate_toggle(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    cert.status = Certificate.Status.REVOKED if cert.status == Certificate.Status.VALID else Certificate.Status.VALID
    cert.save(update_fields=["status"])
    audit(request, f"Certificat → {cert.get_status_display()}", cert.number)
    messages.success(request, f"Certificat {cert.number} : {cert.get_status_display().lower()}.")
    return redirect("staff_certificates")


# ------------------------------------------------------------------ Réglages
@staff_required
def settings_edit(request):
    site = SiteSettings.load()
    form = SiteSettingsForm(request.POST or None, request.FILES or None, instance=site)
    if request.method == "POST" and form.is_valid():
        form.save()
        audit(request, "Réglages de la plateforme modifiés")
        messages.success(request, "Réglages enregistrés. Ils s'appliquent aux prochains certificats délivrés.")
        return redirect("staff_settings")
    return render(request, "staff/settings.html", {"form": form, "base_url": services.base_url()})


@staff_required
def certificate_preview(request):
    """Aperçu PDF du certificat avec des données fictives (rien n'est enregistré)."""
    from decimal import Decimal

    from django.http import HttpResponse

    from ..pdf import build_pdf_bytes

    class Demo:
        number = "FI-APERCU-0000"
        full_name = "Prénom Nom"
        course_title = "Titre de la formation"
        score20 = Decimal("18")
        score20_display = "18"
        issued_at = timezone.now()
        issuer = SiteSettings.load().organization_name
        verify_url = services.base_url() + "/verifier/exemple/"

    pdf = build_pdf_bytes(Demo(), SiteSettings.load())
    return HttpResponse(pdf, content_type="application/pdf")


# ------------------------------------------------------------------ Récompenses Claude Pro
@staff_required
def reward_list(request):
    offers = RewardOffer.objects.select_related("course")
    claims = RewardClaim.objects.select_related("user__profile", "course", "attempt")
    status = request.GET.get("status")
    if status in RewardClaim.Status.values:
        claims = claims.filter(status=status)
    return render(
        request,
        "staff/reward_list.html",
        {"offers": offers, "claims": claims, "statuses": RewardClaim.Status.choices, "current": status},
    )


@staff_required
def reward_offer_edit(request, pk=None):
    offer = get_object_or_404(RewardOffer, pk=pk) if pk else None
    form = RewardOfferForm(request.POST or None, instance=offer)
    if request.method == "POST" and form.is_valid():
        offer = form.save()
        audit(request, f"Offre Claude Pro enregistrée ({offer.status_label})", offer.course)
        messages.success(request, f"Offre enregistrée — statut : {offer.status_label}.")
        return redirect("staff_rewards")
    return render(request, "staff/reward_offer_form.html", {"form": form, "offer": offer})


@staff_required
def reward_claim_edit(request, pk):
    claim = get_object_or_404(RewardClaim.objects.select_related("user__profile", "course", "attempt", "offer"), pk=pk)
    form = RewardClaimAdminForm(request.POST or None, instance=claim)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        if obj.status == RewardClaim.Status.DELIVERED and not obj.delivered_at:
            obj.delivered_at = timezone.now()
        if obj.status != RewardClaim.Status.DELIVERED:
            obj.delivered_at = None
        obj.save()
        audit(request, f"Récompense → {obj.get_status_display()}", f"{claim.user.email} / {claim.course}")
        messages.success(request, "Récompense mise à jour.")
        return redirect("staff_rewards")
    return render(request, "staff/reward_claim_form.html", {"claim": claim, "form": form})
