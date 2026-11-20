import os

from cryptography.hazmat.primitives import serialization
from django.core.exceptions import ImproperlyConfigured

# See config/settings/base.py's comment on DEBUG: it must be set via the
# environment *before* `from .base import *` runs, not only as the
# `DEBUG = True` literal below, or debug_toolbar never gets added to
# INSTALLED_APPS/MIDDLEWARE.
os.environ.setdefault("DEBUG", "True")

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# Mirrors common.py's own DEBUG parsing (line 44) so docker-compose's
# DEBUG env var (from DJANGO_DEBUG) isn't silently overridden by a literal here.
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")

# The insecure fallback is for local development only: with DEBUG off the server refuses to start
# until SECRET_KEY is set (a long random value; `python -c "import secrets; print(secrets.token_urlsafe(64))"`).
SECRET_KEY = os.environ.get("SECRET_KEY") or ("django-insecure-key" if DEBUG else "")
if not SECRET_KEY:
    raise ImproperlyConfigured("Set the SECRET_KEY environment variable when DEBUG is off.")

# Comma-separated host names, e.g. ALLOWED_HOSTS=api.example.com. With DEBUG on and nothing set,
# any host is accepted; with DEBUG off an empty list refuses every request.
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS") or (["*"] if DEBUG else [])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "DB_NAME",
        "USER": "DB_USERNAME",
        "PASSWORD": "DB_PASSWORD",
        "HOST": "localhost",
        "PORT": "5432",
        "CONN_MAX_AGE": 600,
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
]

# JWT signing keys. Both are mandatory — load_jwt_key raises
# ImproperlyConfigured if a PEM file is missing. Create them with
# `python manage.py generate_rsa_keys`.
SIMPLE_JWT["SIGNING_KEY"] = load_jwt_key(
    "private_key.pem",
    lambda data: serialization.load_pem_private_key(data, password=None),
)
SIMPLE_JWT["VERIFYING_KEY"] = load_jwt_key(
    "public_key.pem",
    serialization.load_pem_public_key,
)
if DEBUG:
    # a day-long access token saves logging in again while developing; production keeps base.py's 10 minutes
    SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=1)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=15)


# Any origin may call the API while developing. Outside DEBUG only the allow-list in base.py applies
# (the origin of FRONTEND_BASE_URL plus CORS_ALLOWED_ORIGINS).
CORS_ALLOW_ALL_ORIGINS = DEBUG
