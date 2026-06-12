"""
Configurações para deploy no Railway.
Herda base.py e adapta para o ambiente Railway.

Variáveis obrigatórias no Railway:
  DJANGO_SETTINGS_MODULE=config.settings.railway
  SECRET_KEY=<valor>
  DATABASE_URL=<injetado automaticamente pelo plugin PostgreSQL>
"""
import os

from .base import *  # noqa

# ─── Debug ────────────────────────────────────────────────────────────────────
DEBUG = env.bool("DEBUG", default=False)

# ─── Hosts permitidos ─────────────────────────────────────────────────────────
ALLOWED_HOSTS = ["*"]

# ─── Banco de dados ───────────────────────────────────────────────────────────
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url and not _db_url.startswith("${"):
    DATABASES = {"default": env.db_url_config(_db_url)}
    DATABASES["default"]["CONN_MAX_AGE"] = 60
else:
    # Fallback SQLite (nunca deveria acontecer em produção Railway)
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
# CompressedStaticFilesStorage não requer manifesto (collectstatic pode ser feito no start)
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─── HTTPS / Proxy ────────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # Railway já faz o redirect via proxy
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ─── Sentry (opcional) ────────────────────────────────────────────────────────
_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# ─── Cache (Redis opcional) ───────────────────────────────────────────────────
_redis_url = os.environ.get("REDIS_URL", "")
if _redis_url and not _redis_url.startswith("${"):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ─── Email ────────────────────────────────────────────────────────────────────
if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─── Logging — console apenas (sem RotatingFileHandler) ──────────────────────
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
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "lgpd": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "audit": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
