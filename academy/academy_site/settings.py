"""
Réglages Django de Flux Intelligent Academy.

Tout ce qui change entre la machine locale et la production passe par des
variables d'environnement (voir .env.example) : clé secrète, base de données,
URL publique, e-mail.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEBUG = env_bool("ACADEMY_DEBUG", False)

SECRET_KEY = env("ACADEMY_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-insecure-key-change-me"
    else:
        raise RuntimeError("ACADEMY_SECRET_KEY doit être défini en production.")

# URL publique réelle de la plateforme (utilisée par les QR codes des certificats
# et les liens envoyés par e-mail). Exemple : https://academy.fluxintelligent.com
ACADEMY_BASE_URL = env("ACADEMY_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

ALLOWED_HOSTS = [h.strip() for h in env("ACADEMY_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env("ACADEMY_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "learning",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "academy_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "learning.context_processors.platform",
            ],
        },
    },
]

WSGI_APPLICATION = "academy_site.wsgi.application"

# Base de données : SQLite par défaut, PostgreSQL via DATABASE_URL en production.
DATABASE_URL = env("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = ["learning.auth.EmailBackend"]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Casablanca"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Fichiers téléversés (logo, images de cours) et certificats PDF.
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("ACADEMY_MEDIA_ROOT", BASE_DIR / "media"))
# Les certificats ne sont jamais servis directement : ils passent par une vue
# qui vérifie le propriétaire. Ils sont stockés hors du dossier média public.
PRIVATE_ROOT = Path(env("ACADEMY_PRIVATE_ROOT", BASE_DIR / "private"))

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# E-mail : console en local, SMTP en production.
EMAIL_BACKEND = env("ACADEMY_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("ACADEMY_EMAIL_HOST", "")
EMAIL_PORT = int(env("ACADEMY_EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("ACADEMY_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = env("ACADEMY_EMAIL_PASSWORD", "")
EMAIL_USE_TLS = env_bool("ACADEMY_EMAIL_TLS", True)
DEFAULT_FROM_EMAIL = env("ACADEMY_FROM_EMAIL", "Flux Intelligent Academy <no-reply@fluxintelligent.com>")

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("ACADEMY_SSL_REDIRECT", True)
    SECURE_REDIRECT_EXEMPT = [r"^sante/$"]
    SECURE_HSTS_SECONDS = int(env("ACADEMY_HSTS_SECONDS", "0"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
