"""
Configurações para deploy no Railway.
"""
import os

from .base import *  # noqa

# ─── Debug ────────────────────────────────────────────────────────────────────
DEBUG = True  # TEMPORARIO: para diagnosticar erro de admin

# Silencia system checks para diagnostico
SILENCED_SYSTEM_CHECKS = ["*"]

# ─── Hosts permitidos ─────────────────────────────────────────────────────────
ALLOWED_HOSTS = ["*"]

# ─── Banco de dados ───────────────────────────────────────────────────────────
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url and not _db_url.startswith("${"):
    DATABASES = {"default": env.db_url_config(_db_url)}
    DATABASES["default"]["CONN_MAX_AGE"] = 60
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ─── Middleware ───────────────────────────────────────────────────────────────
_EXCLUDED = {
    "apps.clinics.middleware.TenantMiddleware",
    "apps.audit.middleware.AuditMiddleware",
    "apps.lgpd.middleware.SecurityHeadersMiddleware",
}
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + [
    m for m in MIDDLEWARE
    if m not in _EXCLUDED
    and m not in {
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
    }
]

# ─── Arquivos estáticos com WhiteNoise ────────────────────────────────────────
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─── HTTPS / Proxy ────────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ─── Cache ────────────────────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─── Logging ────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
