"""Administration technique Django (réservée aux superutilisateurs)."""
from django.contrib import admin

from .models import (
    AdminAuditLog,
    Certificate,
    Choice,
    Course,
    Enrollment,
    ExamAttempt,
    Lesson,
    Module,
    Profile,
    Question,
    RewardClaim,
    RewardOffer,
    SiteSettings,
)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "course", "kind")
    list_filter = ("course",)
    inlines = [ChoiceInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "pass_threshold", "max_attempts", "is_demo")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("number", "full_name", "course_title", "score20", "issued_at", "status")
    search_fields = ("number", "full_name")
    readonly_fields = ("verify_id", "verify_url", "pdf_path")


@admin.register(RewardClaim)
class RewardClaimAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "eligible_at", "requested_at", "delivered_at")
    list_filter = ("status",)


for model in (SiteSettings, Profile, Module, Lesson, Enrollment, ExamAttempt, RewardOffer, AdminAuditLog):
    admin.site.register(model)
