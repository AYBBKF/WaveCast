"""
Modèle de données de Flux Intelligent Academy.

Formation (Course) → Modules → Leçons, plus un examen final (Questions/Choix).
Progression, tentatives, certificats et récompenses sont enregistrés en base.
"""
import secrets
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def unique_slug(model, value, instance_pk=None, field="slug", **scope):
    base = slugify(value)[:70] or "element"
    slug, n = base, 2
    qs = model.objects.filter(**scope)
    while qs.filter(**{field: slug}).exclude(pk=instance_pk).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


class SiteSettings(models.Model):
    """Réglages de marque, modifiables depuis l'administration (une seule ligne)."""

    platform_name = models.CharField("Nom de la plateforme", max_length=120, default="Flux Intelligent Academy")
    organization_name = models.CharField("Nom de l'organisme", max_length=120, default="Flux Intelligent")
    primary_color = models.CharField("Couleur principale", max_length=7, default="#673DE6")
    accent_color = models.CharField("Couleur secondaire", max_length=7, default="#111014")
    logo = models.ImageField("Logo", upload_to="branding/", blank=True)
    certificate_signature = models.ImageField("Signature (certificat)", upload_to="branding/", blank=True)
    certificate_signatory = models.CharField("Nom du signataire", max_length=120, blank=True)
    certificate_signatory_title = models.CharField("Fonction du signataire", max_length=120, blank=True)
    certificate_text = models.TextField(
        "Texte du certificat",
        default=(
            "{organisme} atteste que {nom} a suivi la formation « {formation} » "
            "et a réussi son évaluation finale avec une note de {note}/20."
        ),
        help_text="Variables disponibles : {organisme}, {nom}, {formation}, {note}.",
    )
    support_email = models.EmailField("E-mail de contact", blank=True)

    class Meta:
        verbose_name = "Réglages de la plateforme"
        verbose_name_plural = "Réglages de la plateforme"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.platform_name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField("Nom complet", max_length=150)
    email_verified_at = models.DateTimeField("E-mail vérifié le", null=True, blank=True)

    @property
    def email_verified(self):
        return self.email_verified_at is not None

    def __str__(self):
        return self.full_name or self.user.get_username()


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PUBLISHED = "published", "Publiée"
        ARCHIVED = "archived", "Archivée"

    class Level(models.TextChoices):
        BEGINNER = "debutant", "Débutant"
        INTERMEDIATE = "intermediaire", "Intermédiaire"
        ADVANCED = "avance", "Avancé"

    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    summary = models.CharField("Accroche", max_length=300, blank=True)
    description = models.TextField("Description")
    cover = models.ImageField("Image de couverture", upload_to="covers/", blank=True)
    objectives = models.TextField("Objectifs pédagogiques", help_text="Un objectif par ligne.", blank=True)
    level = models.CharField("Niveau", max_length=20, choices=Level.choices, default=Level.BEGINNER)
    duration = models.CharField("Durée estimée", max_length=60, default="2 heures")
    status = models.CharField("Statut", max_length=12, choices=Status.choices, default=Status.DRAFT)
    pass_threshold = models.DecimalField(
        "Seuil de réussite (%)",
        max_digits=5,
        decimal_places=2,
        default=Decimal("70.00"),
        validators=[MinValueValidator(Decimal("1")), MaxValueValidator(Decimal("100"))],
    )
    max_attempts = models.PositiveIntegerField(
        "Tentatives autorisées", default=0, help_text="0 = tentatives illimitées."
    )
    is_demo = models.BooleanField("Formation de démonstration", default=False)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "title"]
        verbose_name = "Formation"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Course, self.title, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", args=[self.slug])

    @property
    def objectives_list(self):
        return [line.strip(" -•\t") for line in self.objectives.splitlines() if line.strip()]

    def ordered_lessons(self):
        return list(
            Lesson.objects.filter(module__course=self).select_related("module").order_by("module__position", "module__id", "position", "id")
        )

    @property
    def threshold_on_20(self):
        return (self.pass_threshold * 20 / 100).quantize(Decimal("0.01"))


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField("Titre du module", max_length=200)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField("Titre de la leçon", max_length=200)
    slug = models.SlugField(max_length=80, blank=True)
    content = models.TextField("Contenu", blank=True)
    key_takeaway = models.TextField("À retenir", blank=True)
    reading_minutes = models.PositiveIntegerField("Temps de lecture (min)", default=5)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Lesson, self.title, self.pk, module__course=self.module.course)
        super().save(*args, **kwargs)

    @property
    def course(self):
        return self.module.course

    def get_absolute_url(self):
        return reverse("lesson", args=[self.module.course.slug, self.slug])

    def __str__(self):
        return self.title


class Question(models.Model):
    class Kind(models.TextChoices):
        MCQ = "mcq", "QCM (réponse unique)"
        TRUE_FALSE = "tf", "Vrai / Faux"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField("Énoncé")
    kind = models.CharField("Type", max_length=4, choices=Kind.choices, default=Kind.MCQ)
    explanation = models.TextField("Explication de la correction")
    related_lesson = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions", verbose_name="Leçon liée"
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text[:80]

    def correct_choice(self):
        return self.choices.filter(is_correct=True).first()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField("Réponse", max_length=400)
    is_correct = models.BooleanField("Bonne réponse", default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.text


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    last_activity_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("user", "course")]

    def __str__(self):
        return f"{self.user} → {self.course}"


class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("user", "lesson")]


class ExamAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attempts")
    number = models.PositiveIntegerField("Numéro de tentative")
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    threshold = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("70.00"))
    passed = models.BooleanField(default=False)
    # Ordre des questions servi à l'apprenant (identifiants), figé au démarrage.
    question_ids = models.JSONField(default=list)

    class Meta:
        ordering = ["-started_at"]
        unique_together = [("user", "course", "number")]

    def __str__(self):
        return f"Tentative {self.number} — {self.user} — {self.course}"

    @property
    def is_submitted(self):
        return self.submitted_at is not None

    @property
    def is_perfect(self):
        return self.is_submitted and self.total_questions > 0 and self.correct_answers == self.total_questions

    @property
    def score20(self):
        """Note exacte sur 20 (fraction décimale non arrondie)."""
        if not self.total_questions:
            return Decimal("0")
        return Decimal(self.correct_answers) * 20 / Decimal(self.total_questions)

    @property
    def percent(self):
        if not self.total_questions:
            return Decimal("0")
        return Decimal(self.correct_answers) * 100 / Decimal(self.total_questions)

    @property
    def score20_display(self):
        return f"{self.score20.quantize(Decimal('0.01')).normalize():f}".replace(".", ",")

    @property
    def percent_display(self):
        return f"{self.percent.quantize(Decimal('0.1')).normalize():f}".replace(".", ",")


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = [("attempt", "question")]


def new_verify_id():
    return secrets.token_urlsafe(18)


class Certificate(models.Model):
    class Status(models.TextChoices):
        VALID = "valid", "Valide"
        REVOKED = "revoked", "Révoqué"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="certificates")
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.PROTECT, related_name="certificates")
    number = models.CharField("Numéro", max_length=40, unique=True)
    verify_id = models.CharField(max_length=40, unique=True, default=new_verify_id)
    # Informations figées à la date de délivrance.
    full_name = models.CharField("Nom sur le certificat", max_length=150)
    course_title = models.CharField("Titre de la formation", max_length=200)
    score20 = models.DecimalField(max_digits=5, decimal_places=2)
    issued_at = models.DateTimeField(default=timezone.now)
    issuer = models.CharField(max_length=120, default="Flux Intelligent")
    verify_url = models.URLField(max_length=300)
    pdf_path = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.VALID)

    class Meta:
        unique_together = [("user", "course")]
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.number} — {self.full_name}"

    @property
    def score20_display(self):
        return f"{self.score20.normalize():f}".replace(".", ",")


class RewardOffer(models.Model):
    """Offre « Claude Pro offert par Flux Intelligent » pour un 100 % à l'examen."""

    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="reward_offer", verbose_name="Formation concernée")
    duration_label = models.CharField(
        "Durée offerte", max_length=60, blank=True, help_text="Ex. : 1 mois. Obligatoire avant l'activation."
    )
    delivery_method = models.TextField(
        "Modalités de remise",
        blank=True,
        help_text="Décrivez concrètement comment l'abonnement est remis (ex. : lien cadeau officiel Claude à activer sur claude.ai/gift/redeem).",
    )
    delivery_delay = models.CharField("Délai de remise annoncé", max_length=120, blank=True, help_text="Ex. : sous 7 jours ouvrés.")
    funding_confirmed = models.BooleanField(
        "Financement confirmé par Flux Intelligent", default=False
    )
    is_active = models.BooleanField("Offre activée (visible publiquement)", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offre Claude Pro"

    def __str__(self):
        return f"Claude Pro — {self.course}"

    @property
    def is_configured(self):
        return bool(self.duration_label.strip() and self.delivery_method.strip() and self.delivery_delay.strip() and self.funding_confirmed)

    @property
    def is_live(self):
        return self.is_active and self.is_configured

    @property
    def status_label(self):
        if self.is_live:
            return "Active"
        return "Brouillon"

    def clean(self):
        if self.is_active and not self.is_configured:
            raise ValidationError(
                "Renseignez la durée, les modalités, le délai de remise et confirmez le financement avant d'activer l'offre."
            )


class RewardClaim(models.Model):
    class Status(models.TextChoices):
        ELIGIBLE = "eligible", "Éligible"
        REQUESTED = "requested", "Demande enregistrée"
        IN_PROGRESS = "in_progress", "En cours de remise"
        DELIVERED = "delivered", "Remis"

    offer = models.ForeignKey(RewardOffer, on_delete=models.PROTECT, related_name="claims")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reward_claims")
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="reward_claims")
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.PROTECT, related_name="reward_claims")
    eligible_at = models.DateTimeField(default=timezone.now)
    duration_label = models.CharField(max_length=60)
    delivery_delay = models.CharField(max_length=120, blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    requested_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ELIGIBLE)
    gift_link = models.URLField("Lien cadeau officiel", max_length=500, blank=True)
    delivery_method_used = models.CharField("Modalité de remise utilisée", max_length=255, blank=True)
    delivery_reference = models.CharField("Référence de livraison", max_length=255, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField("Notes internes", blank=True)

    class Meta:
        unique_together = [("offer", "user")]
        ordering = ["-eligible_at"]
        verbose_name = "Récompense Claude Pro"

    def __str__(self):
        return f"{self.user} — {self.get_status_display()}"


class AdminAuditLog(models.Model):
    """Trace simple des actions sensibles réalisées dans l'administration."""

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
