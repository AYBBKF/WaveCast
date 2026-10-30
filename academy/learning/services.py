"""
Règles métier côté serveur : progression, examen, certificat et récompense.

Aucune de ces décisions n'est laissée au navigateur : la note est calculée ici à
partir des réponses enregistrées, et le certificat comme la récompense ne sont
accordés qu'après vérification des données en base.
"""
import secrets
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from .models import (
    AttemptAnswer,
    Certificate,
    Choice,
    Course,
    Enrollment,
    ExamAttempt,
    LessonProgress,
    Question,
    RewardClaim,
    RewardOffer,
    SiteSettings,
)


# --------------------------------------------------------------------------
# Progression
# --------------------------------------------------------------------------
def course_progress(user, course):
    lessons = course.ordered_lessons()
    total = len(lessons)
    if not user.is_authenticated or not total:
        return {"total": total, "done": 0, "percent": 0, "completed_ids": set(), "lessons": lessons}
    done_ids = set(
        LessonProgress.objects.filter(user=user, lesson__module__course=course).values_list("lesson_id", flat=True)
    )
    done = sum(1 for l in lessons if l.id in done_ids)
    return {
        "total": total,
        "done": done,
        "percent": round(done * 100 / total),
        "completed_ids": done_ids,
        "lessons": lessons,
    }


def all_lessons_completed(user, course):
    p = course_progress(user, course)
    return p["total"] > 0 and p["done"] == p["total"]


def enroll(user, course):
    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
    return enrollment


# --------------------------------------------------------------------------
# Examen
# --------------------------------------------------------------------------
class ExamNotAllowed(Exception):
    pass


def attempts_used(user, course):
    return ExamAttempt.objects.filter(user=user, course=course, submitted_at__isnull=False).count()


def attempts_left(user, course):
    if course.max_attempts == 0:
        return None  # illimité
    return max(course.max_attempts - attempts_used(user, course), 0)


def can_take_exam(user, course):
    if not course.questions.exists():
        return False, "L'examen de cette formation n'est pas encore disponible."
    if not all_lessons_completed(user, course):
        return False, "Terminez toutes les leçons pour débloquer l'examen final."
    left = attempts_left(user, course)
    if left is not None and left <= 0:
        return False, "Vous avez utilisé toutes les tentatives autorisées pour cet examen."
    return True, ""


@transaction.atomic
def start_attempt(user, course):
    """Renvoie la tentative en cours (non soumise) ou en crée une nouvelle."""
    allowed, reason = can_take_exam(user, course)
    if not allowed:
        raise ExamNotAllowed(reason)
    open_attempt = (
        ExamAttempt.objects.select_for_update().filter(user=user, course=course, submitted_at__isnull=True).first()
    )
    if open_attempt:
        return open_attempt
    number = ExamAttempt.objects.filter(user=user, course=course).count() + 1
    ids = list(course.questions.order_by("position", "id").values_list("id", flat=True))
    return ExamAttempt.objects.create(
        user=user, course=course, number=number, threshold=course.pass_threshold, question_ids=ids
    )


def is_passing(correct, total, threshold):
    """Comparaison exacte en entiers/décimaux : correct/total × 100 ≥ seuil."""
    if not total:
        return False
    return Decimal(correct) * 100 >= Decimal(threshold) * Decimal(total)


@transaction.atomic
def submit_attempt(attempt_id, user, raw_answers):
    """
    Corrige une tentative. raw_answers : {question_id: choice_id}.
    Un second envoi (double clic, retour arrière) ne recalcule rien.
    """
    attempt = ExamAttempt.objects.select_for_update().get(pk=attempt_id, user=user)
    if attempt.is_submitted:
        return attempt, False

    questions = {q.id: q for q in Question.objects.filter(id__in=attempt.question_ids)}
    valid_choices = {
        c.id: c for c in Choice.objects.filter(question_id__in=questions.keys())
    }
    correct = 0
    for qid in attempt.question_ids:
        question = questions.get(qid)
        if question is None:
            continue
        choice = None
        cid = raw_answers.get(qid)
        if cid is not None:
            candidate = valid_choices.get(cid)
            if candidate and candidate.question_id == qid:
                choice = candidate
        ok = bool(choice and choice.is_correct)
        correct += int(ok)
        AttemptAnswer.objects.create(attempt=attempt, question=question, choice=choice, is_correct=ok)

    attempt.total_questions = len(questions)
    attempt.correct_answers = correct
    attempt.passed = is_passing(correct, attempt.total_questions, attempt.threshold)
    attempt.submitted_at = timezone.now()
    attempt.save()

    if attempt.passed:
        Enrollment.objects.filter(user=user, course=attempt.course).update(last_activity_at=timezone.now())
    record_reward_eligibility(attempt)
    return attempt, True


def best_passing_attempt(user, course):
    attempts = [a for a in ExamAttempt.objects.filter(user=user, course=course, passed=True)]
    if not attempts:
        return None
    return max(attempts, key=lambda a: (a.score20, -a.number))


# --------------------------------------------------------------------------
# Certificat
# --------------------------------------------------------------------------
class CertificateNotAllowed(Exception):
    pass


def certificate_number(course):
    year = timezone.now().year
    return f"FI-{year}-{secrets.token_hex(4).upper()}"


def base_url():
    return settings.ACADEMY_BASE_URL.rstrip("/")


def issue_certificate(user, course, full_name):
    """
    Délivre le certificat si (et seulement si) une tentative réussie existe.
    Idempotent : renvoie le certificat existant s'il a déjà été délivré.
    """
    existing = Certificate.objects.filter(user=user, course=course).first()
    if existing:
        return existing, False
    attempt = best_passing_attempt(user, course)
    if attempt is None:
        raise CertificateNotAllowed("Aucune tentative réussie pour cette formation.")
    full_name = (full_name or "").strip()
    if len(full_name) < 3:
        raise CertificateNotAllowed("Le nom complet est obligatoire.")

    site = SiteSettings.load()
    from .pdf import render_certificate_pdf  # import local : ReportLab n'est chargé qu'ici

    for _ in range(5):
        try:
            with transaction.atomic():
                cert = Certificate(
                    user=user,
                    course=course,
                    attempt=attempt,
                    number=certificate_number(course),
                    full_name=full_name,
                    course_title=course.title,
                    score20=attempt.score20.quantize(Decimal("0.01")),
                    issuer=site.organization_name,
                )
                cert.verify_url = base_url() + reverse("certificate_verify", args=[cert.verify_id])
                cert.save()
                cert.pdf_path = render_certificate_pdf(cert, site)
                cert.save(update_fields=["pdf_path"])
                return cert, True
        except IntegrityError:
            existing = Certificate.objects.filter(user=user, course=course).first()
            if existing:
                return existing, False
            continue  # collision de numéro : on réessaie
    raise CertificateNotAllowed("Impossible de générer un numéro de certificat unique.")


# --------------------------------------------------------------------------
# Récompense Claude Pro
# --------------------------------------------------------------------------
def live_offer_for(course):
    offer = RewardOffer.objects.filter(course=course).first()
    return offer if offer and offer.is_live else None


def reward_conditions(user, attempt):
    """Liste des conditions non remplies (vide = éligible)."""
    missing = []
    profile = getattr(user, "profile", None)
    if not (profile and profile.email_verified):
        missing.append("adresse e-mail vérifiée")
    if not all_lessons_completed(user, attempt.course):
        missing.append("toutes les leçons terminées")
    if not attempt.is_perfect:
        missing.append("100 % de bonnes réponses")
    return missing


def record_reward_eligibility(attempt):
    """Crée au plus une ligne d'éligibilité par bénéficiaire et par offre."""
    offer = live_offer_for(attempt.course)
    if offer is None or not attempt.is_perfect:
        return None
    if reward_conditions(attempt.user, attempt):
        return None
    claim, _ = RewardClaim.objects.get_or_create(
        offer=offer,
        user=attempt.user,
        defaults={
            "course": attempt.course,
            "attempt": attempt,
            "duration_label": offer.duration_label,
            "delivery_delay": offer.delivery_delay,
        },
    )
    return claim


def eligible_claim_for(user, course):
    """Rattrapage : un 100 % obtenu avant la vérification de l'e-mail devient éligible ensuite."""
    claim = RewardClaim.objects.filter(user=user, course=course).first()
    if claim:
        return claim
    perfect = ExamAttempt.objects.filter(user=user, course=course, submitted_at__isnull=False).order_by("submitted_at")
    for attempt in perfect:
        if attempt.is_perfect:
            return record_reward_eligibility(attempt)
    return None


@transaction.atomic
def request_reward(user, claim_id, full_name, email):
    claim = RewardClaim.objects.select_for_update().get(pk=claim_id, user=user)
    if claim.status != RewardClaim.Status.ELIGIBLE:
        return claim, False
    claim.full_name = full_name.strip()
    claim.email = email.strip()
    claim.requested_at = timezone.now()
    claim.status = RewardClaim.Status.REQUESTED
    claim.save()
    return claim, True
