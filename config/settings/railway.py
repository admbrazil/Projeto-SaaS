"""
Configuracoes para deploy no Railway.
"""
import os
from .base import *  # noqa

DEBUG = env.bool("DEBUG", default=False)

_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
_extra_hosts = [h.strip() for h in os.environ.get("EXTRA_ALLOWED_HOSTS", "").split(",") if h.strip()]

ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + _extra_hosts
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)

# DATABASE_URL: fallback para SQLite se nao definido ou referencia nao resolvida
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url and not _db_url.startswith("${{"):
    DATABASES = {"default": env.db_url_config(_db_url)}
    DATABASES["default"]["CONN_MAX_AGE"] = 60
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
] + [m for m in MIDDLEWARE if m not in (
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
)]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG and _railway_domain:
    CORS_ALLOWED_ORIGINS = [f"https://{_railway_domain}"]

_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(dsn=_sentry_dsn, integrations=[DjangoIntegration()],
                    traces_sample_rate=0.1, send_default_pii=False)

_redis_url = os.environ.get("REDIS_URL", "")
if _redis_url and not _redis_url.startswith("${{"):
    CACHES = {"default": {"BACKEND": "django_redis.cache.RedisCache",
              "LOCATION": _redis_url,
              "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
