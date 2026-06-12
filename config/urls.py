"""URL configuration principal do projeto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({"status": "ok"})


def admin_debug(request):
    import importlib, traceback
    result = {}
    import django.contrib.admin as _a
    result["registered"] = sorted([str(m._meta.label) for m in _a.site._registry.keys()])
    for mod_path, key in [
        ("apps.patients.admin", "patients"),
        ("apps.doctors.admin", "doctors"),
        ("apps.consultations.admin", "consultations"),
    ]:
        try:
            mod = importlib.import_module(mod_path)
            err = getattr(mod, "_IMPORT_ERROR", None)
            result[key] = err if err else "ok"
        except Exception:
            result[key] = traceback.format_exc()
    return JsonResponse(result, json_dumps_params={"indent": 2})


urlpatterns = [
    path("health/", health_check, name="health"),
    path("__debug__/", admin_debug, name="admin_debug"),
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("painel/", include("apps.clinics.urls")),
    path("paciente/", include("apps.patients.urls")),
    path("painel/nr1/", include("apps.consultations.nr1_urls")),
    path("meus-dados/", include("apps.lgpd.urls")),
    path("api/clinic/", include("apps.api.urls")),
    path("api/", include("apps.api.mevo_urls")),
    path("tutoriais/", include("apps.clinics.tutorial_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
