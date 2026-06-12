"""URL configuration principal."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("meus-dados/", include("apps.lgpd.urls")),
    path("api/clinic/", include("apps.api.urls")),
    path("api/", include("apps.api.mevo_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
