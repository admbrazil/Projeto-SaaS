"""
Configuracoes para deploy no Railway.
"""
import os
from .base import *  # noqa

DEBUG = env.bool("DEBUG", default=False)

_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
_extra_hosts = [h.strip() for h in os.environ.get("EXTRA_ALLOWED_HOSTS", "").split(",") if h.strip()]

# Aceita qualquer host (Railway usa dominio dinamico)
ALLOWED_HOSTS = ["*"]

# DATABASE_URL: fallback para SQLite se nao definido ou referencia nao resolvida
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url and not _db_url.startswith("${" + "{"):
    DATABASES = {"default": env.db_url_config(_db_url)}
    DATABASES["default"]["CONN_MAX_AGE"] = 60
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Middleware para Railway (sem TenantMiddleware - evita query no banco durante healthcheck)
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

CORS_ALLOW_ALL_ORIGINS = True

# Cache: LocMem quando nao tem Redis
_redis_url = os.environ.get("REDIS_URL", "")
if _redis_url and not _redis_url.startswith("${" + "{"):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging: apenas console (sem arquivo - evita FileNotFoundError em /app/logs/)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[{levelname}] {asctime} {module}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
