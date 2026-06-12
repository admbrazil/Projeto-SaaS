"""URL configuration principal do projeto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Endpoint de saude para Railway / load balancers."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # Health check (Railway, uptime monitors)
    path("health/", health_check, name="health"),

    # Admin Django (restrito por IP em producao via middleware)
    path("admin/", admin.site.urls),

    # Autenticacao
    path("", include("apps.accounts.urls")),

    # Painel administrativo da clinica
    path("painel/", include("apps.clinics.urls")),

    # Portal do paciente
    path("paciente/", include("apps.patients.urls")),

    # Relatorios NR1
    path("painel/nr1/", include("apps.consultations.nr1_urls")),

    # LGPD - portal de direitos do titular
    path("meus-dados/", include("apps.lgpd.urls")),

    # API publica (Bearer Token)
    path("api/clinic/", include("apps.api.urls")),

    # Endpoint MEVO
    path("api/", include("apps.api.mevo_urls")),

    # Tutoriais
    path("tutoriais/", include("apps.clinics.tutorial_urls")),
]

# Arquivos de midia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
