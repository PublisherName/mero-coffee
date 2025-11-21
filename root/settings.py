from pathlib import Path

from django.core.management.utils import get_random_secret_key
from environs import Env

from root.validators import validate_production_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Set up the environment variables with default types and values
env = Env()
env.read_env()

# Environment-based settings
SITE_BASE_URL = env.str("SITE_BASE_URL", default="http://127.0.0.1:8000/")

DEBUG = env.bool("DEBUG", default=False)

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default=get_random_secret_key())

# Hosts that are allowed to communicate
DJANGO_ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[], subcast=str)
if DEBUG:
    LOCAL_ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1"]
    ALLOWED_HOSTS = LOCAL_ALLOWED_HOSTS + DJANGO_ALLOWED_HOSTS
else:
    ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS


# Admin Interface
ADMIN_APPS = [
    "jazzmin",
    "django.contrib.admin",
]

# Django Core Apps
DJANGO_CORE_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Third-Party Apps
THIRD_PARTY_APPS = []

# Project Apps
PROJECT_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.creators",
    "apps.dashboard",
    "apps.payments",
]

# Combining all app groups
INSTALLED_APPS = ADMIN_APPS + DJANGO_CORE_APPS + THIRD_PARTY_APPS + PROJECT_APPS

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

ROOT_URLCONF = "root.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "root.wsgi.application"

# Database settings
DATABASES = {
    "default": env.dj_db_url(
        "DATABSE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600 if not DEBUG else 0,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/login/"

# Security Settings for Production
if not DEBUG:
    # HTTPS/SSL Settings
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Security Headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

    # Proxy Headers
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "public"

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Media files (Images)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email verification token settings
TOKEN_SALT = env.str("TOKEN_SALT", default=get_random_secret_key())
TOKEN_EXPIRATION_HOURS = env.int("TOKEN_EXPIRATION_HOURS", default=48)

# Email settings
email_config = env.dj_email_url(
    "SMTP_URL",
    default="console://user:password@localhost?_default_from_email=root@localhost",
)
EMAIL_HOST_USER = email_config["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = email_config["EMAIL_HOST_PASSWORD"]
EMAIL_HOST = email_config["EMAIL_HOST"]
EMAIL_PORT = email_config["EMAIL_PORT"]
EMAIL_BACKEND = email_config["EMAIL_BACKEND"]
EMAIL_USE_TLS = email_config["EMAIL_USE_TLS"]
if "DEFAULT_FROM_EMAIL" in email_config:
    DEFAULT_FROM_EMAIL = email_config["DEFAULT_FROM_EMAIL"]

# Logging Settings
LOG_DIR = BASE_DIR / env.path("LOG_DIR", default="logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file_sync": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "custom.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_sql": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "sql.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_django_error": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "django_error.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 5,
            "formatter": "django.server",
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
    },
    "loggers": {
        "CUSTOM_LOG": {
            "handlers": ["file_sync", "console"] if DEBUG else ["file_sync"],
            "level": "INFO" if DEBUG else "CRITICAL",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["file_sql"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file_django_error"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Validate Production Settings
validate_production_settings(DEBUG, SECRET_KEY, ALLOWED_HOSTS, TOKEN_SALT)
