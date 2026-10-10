import os
import sys
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "apps")

# DEBUG must be decided here, not in config/settings/env.py, even though
# env.py is where every other environment already sets DEBUG = True: this
# module (base.py) is imported first - env.py does `from .base import *`
# - so by the time env.py's own `DEBUG = True` line runs, INSTALLED_APPS/
# MIDDLEWARE below have already been built. A DEBUG assigned only in env.py
# would arrive one import too late to gate debug_toolbar here. Reading it
# from the environment instead means env.py (or any settings module built
# on top of base.py) just needs to set the DEBUG env var *before*
# `from .base import *` - see config/settings/env.py, which does exactly
# that via os.environ.setdefault(). Defaults to False (secure by default -
# a deploy that forgets to set it does not accidentally ship the toolbar
# or dev-relaxed security headers).
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "corsheaders",
    # Background task queue. Pinned in requirements/base.txt since the start but only
    # Requires a separate `python manage.py qcluster` process alongside the web server.
    "django_q",
]

if DEBUG:
    # Unconditional in prod otherwise - the toolbar is a dev-only tool and
    # its middleware/panels have no business running against real traffic.
    THIRD_PARTY_APPS.append("debug_toolbar")
    # Dev-only, like the toolbar (requirements/dev.txt): gives `manage.py show_urls`.
    THIRD_PARTY_APPS.append("django_extensions")


LOCAL_APPS = [
    "apps.app_key",
    "apps.common",
    "apps.institutes",
    "apps.training",
    "apps.users",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(APPS_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kathmandu"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "static/"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.users.authentication.ActiveAccountJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    # Maps django.core.exceptions.ValidationError to a 400 instead of a 500.
    "EXCEPTION_HANDLER": "config.exception_handlers.api_exception_handler",
    # Views opt in with `throttle_scope`; views that don't set one are unaffected.
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.ScopedRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        # Password guessing.
        "login": "5/min",
        "token_refresh": "10/min",
        "otp": "50/min",
        "password_reset": "5/min",
        # Anonymous enquiry submission (also limited per phone number in the view).
        "enquiry": "10/hour",
        "institute_register": "5/hour",
        # Registration email codes, per submitted address (the cache also allows one code a minute).
        "register_otp": "5/hour",
        "register_otp_verify": "30/hour",
        "invitation_accept": "10/hour",
    },
}

LOGIN_URL = "rest_framework:login"
LOGOUT_URL = "rest_framework:logout"

# CORS Settings
CORS_ALLOW_CREDENTIALS = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "RS256",
    # SIGNING_KEY / VERIFYING_KEY are loaded from PEM files in env.py.
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

# RSA key pair used to sign and verify JWTs. Generated by
# `python manage.py generate_rsa_keys`;
JWT_KEY_DIR = BASE_DIR.parent / "keys"

# Verification documents are private: outside MEDIA_ROOT and never served by URL.
# BASE_DIR is config/, so .parent is the project root (next to keys/).
PRIVATE_MEDIA_ROOT = BASE_DIR.parent / "private_media"

# True only while the key-generation command itself is running, so a fresh
# checkout can create the keys that settings otherwise refuse to start without.
_GENERATING_JWT_KEYS = "generate_rsa_keys" in sys.argv


def load_jwt_key(filename, loader):
    """Load a PEM key, or refuse to start if it is missing.

    Returning a weaker default here (e.g. falling back to HS256 with
    SECRET_KEY) would let a deploy with an unmounted secret come up with
    forgeable tokens, so a missing key is a hard failure instead.
    """
    path = JWT_KEY_DIR / filename
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        if _GENERATING_JWT_KEYS:
            return None
        raise ImproperlyConfigured(
            f"JWT key {path} not found. Run: python manage.py generate_rsa_keys"
        ) from None
    return loader(data)


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# The tests clear one-time codes and throttle counters (cache.delete_pattern), so `manage.py test`
# gets its own Redis database for the cache. Sharing REDIS_URL's would wipe the codes someone just
# requested from the dev server. Only the cache moves: the django-q broker stays on REDIS_URL.
if "test" in sys.argv:
    CACHE_REDIS_URL = os.environ.get("REDIS_TEST_URL") or (
        urlsplit(REDIS_URL)._replace(path="/15").geturl()
    )
else:
    CACHE_REDIS_URL = REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Background tasks (email dispatch etc.). Needs its own long-running process:
# `python manage.py qcluster`.
Q_CLUSTER = {
    "name": "training-hub",
    "workers": 2,
    "recycle": 500,
    "timeout": 60,
    # Must exceed `timeout`, or django-q re-queues a task that is still running.
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "redis": REDIS_URL,
    "save_limit": 250,
    "catch_up": False,
}

# Email (SMTP)
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "TrainingHub <no-reply@traininghub.com.np>"
)

# Google reCAPTCHA, verified server-side on public submit endpoints.
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "")

# Institute constant terms
INSTITUTE_INVITATION_TTL_DAYS = 7
INSTITUTE_UPLOAD_MAX_BYTES = 5 * 1024 * 1024
INSTITUTE_DOCUMENT_EXTENSIONS = ("pdf", "jpg", "jpeg", "png")
INSTITUTE_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")

# Image file
ATTACHMENT_MAX_UPLOAD_SIZE = 5 * 1024 * 1024
