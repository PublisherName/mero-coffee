from pathlib import Path

import sentry_sdk
from django.core.management.utils import get_random_secret_key
from environs import Env
from marshmallow.validate import OneOf
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

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
SITE_NAME = env.str("SITE_NAME", default="MeroCoffee")

CSRF_TRUSTED_ORIGINS = [SITE_BASE_URL]

# List of allowed hosts
DJANGO_ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[], subcast=str)
if IS_SERVER_SECURE:
    ALLOWED_HOSTS = DJANGO_ALLOWED_HOSTS
    ALLOWED_CIDR_NETS = env.list("ALLOWED_CIDR_NETS", default=[], subcast=str)
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
    "turnstile",
    "django_celery_results",
]

# Project Apps
PROJECT_APPS = [
    "components",
    "apps.core",
    "apps.accounts",
    "apps.creators",
    "apps.dashboard",
    "apps.payments",
    "apps.newsletter",
    "apps.emails",
]

# Combining all app groups
INSTALLED_APPS = ADMIN_APPS + DJANGO_CORE_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# Django-tailwind config
TAILWIND_APP_NAME = "theme"

NPM_BIN_PATH = env.str("NPM_BIN_PATH", default="/usr/bin/npm")

if DEBUG:
    INSTALLED_APPS += ["django_browser_reload", "debug_toolbar"]
    # Required for django-browser-reload to work
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

MIDDLEWARE = [
    "allow_cidr.middleware.AllowCIDRMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "defender.middleware.FailedLoginMiddleware",
    "root.middleware.FileRenameMiddleware",
]

# Add rate limiting middleware only in secure environments
if IS_SERVER_SECURE:
    MIDDLEWARE.insert(-1, "django_ratelimit.middleware.RatelimitMiddleware")

# Django-tailwind hotreload
if DEBUG:
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
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
DEFENDER_BEHIND_REVERSE_PROXY = True
DEFENDER_LOCK_OUT_BY_IP_AND_USERNAME = True
DEFENDER_COOLOFF_TIME = 60 * 60

# Ratelimit config
RATELIMIT_VIEW = "apps.core.views.ratelimit_lockout_view"
RATELIMIT_USE_CACHE = "default"

if IS_SERVER_SECURE:
    RATELIMIT_RATE = env.str("RATELIMIT_RATE", default="3/30m")
    RATELIMIT_IP_META_KEY = "HTTP_X_FORWARDED_FOR"
    RATELIMIT_IP_SPLIT_CHARS = [","]
else:
    RATELIMIT_RATE = None

# Test runner
TEST_RUNNER = "root.test_runner.CustomTestRunner"


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
TIME_ZONE = "Asia/Kathmandu"
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

# Private media files
PRIVATE_MEDIA_ROOT = BASE_DIR / "private" / "media"
PRIVATE_MEDIA_URL = "/private-media/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email verification token settings
TOKEN_SALT = env.str("TOKEN_SALT", default=get_random_secret_key(), validate=lambda n: len(n) > 49)
TOKEN_EXPIRATION_HOURS = env.int("TOKEN_EXPIRATION_HOURS", default=48)
PASSWORD_RESET_TIMEOUT = TOKEN_EXPIRATION_HOURS * 60 * 60

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

# Payment Configuration
MINIMUM_DONATION_AMOUNT = env.int("MINIMUM_DONATION_AMOUNT", default=100)
MIN_WITHDRAWAL_AMOUNT = env.int("MIN_WITHDRAWAL_AMOUNT", default=100)

# Turnstile Configuration
TURNSTILE_SITEKEY = env.str("TURNSTILE_SITEKEY", default="1x00000000000000000000AA")
TURNSTILE_SECRET = env.str("TURNSTILE_SECRET", default="1x0000000000000000000000000000000AA")
TURNSTILE_TIMEOUT = 5
TURNSTILE_DEFAULT_CONFIG = {
    "render": "always",
    "theme": "auto",
    "size": "flexible",
}

if IS_SERVER_SECURE:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True


# Celery Settings
USE_CELERY = env.bool("USE_CELERY", default=False)
if USE_CELERY:
    CELERY_BROKER_URL = CACHES["default"]["LOCATION"]
    CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default="django-db")
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_ENABLE_UTC = False
    CELERY_WORKER_CONCURRENCY = 4
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Sentry Settings
ENABLE_SENTRY = env.bool("ENABLE_SENTRY", default=False)
if ENABLE_SENTRY:
    sentry_sdk.init(
        dsn=env.str("SENTRY_DSN"),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
        environment=SERVER_ENVIRONMENT,
    )

# Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "MeroCoffee Admin",
    "site_header": "MeroCoffee",
    "site_brand": "MeroCoffee",
    "welcome_sign": "Welcome to MeroCoffee Admin",
    "copyright": "MeroCoffee",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.User": "fas fa-user-circle",
        "accounts.KYC": "fas fa-id-card",
        "creators.CreatorProfile": "fas fa-user-tie",
        "payments.PaymentGateway": "fas fa-credit-card",
        "payments.SupportTransaction": "fas fa-exchange-alt",
        "payments.PaymentLog": "fas fa-file-invoice",
        "defender.AccessAttempt": "fas fa-shield-alt",
        "admin_honeypot.LoginAttempt": "fas fa-bug",
        "cities_light.Country": "fas fa-globe",
        "cities_light.Region": "fas fa-map",
        "cities_light.City": "fas fa-city",
        "cities_light.Subregion": "fas fa-map-marker-alt",
        "payments.Withdrawal": "fas fa-money-bill-wave",
        "payments.Membership": "fas fa-crown",
        "payments.Subscription": "fas fa-calendar-check",
        "newsletter.NewsletterSubscriber": "fas fa-envelope",
        "django_celery_results.TaskResult": "fas fa-tasks",
        "django_celery_results.GroupResult": "fas fa-layer-group",
        "django_celery_results.ChordResult": "fas fa-project-diagram",
    },
    "order_with_respect_to": [
        "accounts",
        "creators",
        "payments",
        "django_celery_results",
        "defender",
        "admin_honeypot",
        "cities_light",
    ],
}
