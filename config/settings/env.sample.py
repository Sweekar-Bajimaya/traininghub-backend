import os

from cryptography.hazmat.primitives import serialization

# See config/settings/base.py's comment on DEBUG: it must be set via the
# environment *before* `from .base import *` runs, not only as the
# `DEBUG = True` literal below, or debug_toolbar never gets added to
# INSTALLED_APPS/MIDDLEWARE.
os.environ.setdefault("DEBUG", "True")

from .base import *

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-key")

# SECURITY WARNING: don't run with debug turned on in production!
# Mirrors common.py's own DEBUG parsing (line 44) so docker-compose's
# DEBUG env var (from DJANGO_DEBUG) isn't silently overridden by a literal here.
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["*"]

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
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=1)
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=15)


CORS_ORIGIN_ALLOW_ALL = True
