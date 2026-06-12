"""
Configuracoes para deploy no Railway.
Herda base.py e adapta para o ambiente Railway.

Variavel obrigatoria no Railway:
  DJANGO_SETTINGS_MODULE=config.settings.railway
"""
import os
from .base import *  # noqa

DEBUG = env.bool("DEBUG", default=False)

# Hosts permitidos
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
_extra_hosts = [h.strip() for h in os.environ.get("EXTRA_ALLOWED_HOSTS", "").split(",") if h.strip()]

ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + _extra_hosts
if _railway_domain:
    ALLOWED_HOSTS.append(_railway_domain)

# Banco de dados via DATABASE_URL (Railway injeta automaticamente)
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = 60

# WhiteNoise para arquivos estaticos sem nginx/S3
_mw = list(MIDDLEWARE)
_sec_idx = next((i for i, m in enumerate(_mw) if 'SecurityMiddleware' in m), 1)
_mw.insert(_sec_idx + 1, "whitenoise.middleware.WhiteNoiseMiddleware")
MIDDLEWARE = _mw

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

# HTTPS via proxy Railway
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# CORS
CORS_ALLOW_ALL_ORIGINS = DEBUG
if not DEBUG and _railway_domain:
    CORS_ALLOWED_ORIGINS = [f"https://{_railway_domain}"]

# Sentry (opcional)
_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(dsn=_sentry_dsn, integrations=[DjangoIntegration()],
                    traces_sample_rate=0.1, send_default_pii=False)

# Cache
_redis_url = os.environ.get("REDIS_URL", "")
if _redis_url:
    CACHES = {"default": {"BACKEND": "django_redis.cache.RedisCache",
                          "LOCATION": _redis_url,
                          "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# Email
if os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND    = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST       = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT       = int(os.environ.get("EMAIL_PORT", 587))
    EMAIL_USE_TLS    = True
    EMAIL_HOST_USER  = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
