from django.apps import AppConfig


class LearningConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "learning"
    verbose_name = "Flux Intelligent Academy"

    def ready(self):
        from . import signals  # noqa: F401
