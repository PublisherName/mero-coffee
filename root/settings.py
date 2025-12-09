from pathlib import Path

from django.core.management.utils import get_random_secret_key
from environs import Env
from marshmallow.validate import OneOf

# Set up the environment variables with default types and values
env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SERVER_ENVIRONMENT = env.str(
    "SERVER_ENVIRONMENT",
    validate=OneOf(
        choices=["development", "testing", "staging", "production"],
        error="SERVER_ENVIRONMENT can only be one of {choices}",
    ),
)

# Is server secure server?
IS_SERVER_SECURE = SERVER_ENVIRONMENT in ["staging", "production"]

# Secret key for server
if IS_SERVER_SECURE:
    SECRET_KEY = env.str("DJANGO_SECRET_KEY", validate=lambda n: len(n) > 49)
else:
    SECRET_KEY = env.str(
        "DJANGO_SECRET_KEY",
        validate=lambda n: len(n) > 49,
        default=get_random_secret_key(),
    )

# Debug
if IS_SERVER_SECURE:
    DEBUG = False
else:
    DEBUG = True

# Environment-based settings
SITE_BASE_URL = env.str("SITE_BASE_URL", default="http://127.0.0.1:8000/")

# List of allowed hosts
DJANGO_ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[], subcast=str)
if IS_SERVER_SECURE:
    ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS
else:
    LOCAL_ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1"]
    ALLOWED_HOSTS = LOCAL_ALLOWED_HOSTS + DJANGO_ALLOWED_HOSTS

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
THIRD_PARTY_APPS = [
    "tailwind",
    "theme",
    "defender",
    "admin_honeypot",
    "django_ratelimit",
    "django_viewcomponent",
    "cities_light",
    "django_cleanup.apps.CleanupConfig",
]

# Project Apps
PROJECT_APPS = [
    "components",
    "apps.core",
    "apps.accounts",
    "apps.creators",
    "apps.dashboard",
    "apps.payments",
]

# Combining all app groups
INSTALLED_APPS = ADMIN_APPS + DJANGO_CORE_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# Django-tailwind config
TAILWIND_APP_NAME = "theme"

NPM_BIN_PATH = env.str("NPM_BIN_PATH", default="/usr/bin/npm")

if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]
    # Required for django-browser-reload to work
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
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
    "defender.middleware.FailedLoginMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",
    "root.middleware.FileRenameMiddleware",
]

# Django-tailwind hotreload
if DEBUG:
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = "root.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
            "components",
        ],
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
        "DATABASE_URL",
        default="sqlite:///db.sqlite3",
    )
}

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str("CACHE_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

# Defender config
DEFENDER_REDIS_URL = CACHES["default"]["LOCATION"]
DEFENDER_LOCKOUT_TEMPLATE = "defender_lockout.html"

# Ratelimit config
RATELIMIT_VIEW = "apps.core.views.ratelimit_lockout_view"
RATELIMIT_RATE = env.str("RATELIMIT_RATE", default="3/30m")


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

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

if IS_SERVER_SECURE:
    # Static files storage
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "public"

# Media files (Images)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email verification token settings
TOKEN_SALT = env.str("TOKEN_SALT", default=get_random_secret_key(), validate=lambda n: len(n) > 49)
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

CITIES_LIGHT_INCLUDE_COUNTRIES = ["NP"]
