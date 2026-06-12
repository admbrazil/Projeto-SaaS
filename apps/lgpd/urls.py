from django.urls import path
from . import views
app_name = "lgpd"
urlpatterns = [
    path("consentimento/", views.consent_required, name="consent"),
    path("", views.my_data_portal, name="portal"),
    path("solicitar/", views.new_lgpd_request, name="new_request"),
    path("exportar/", views.export_my_data, name="export"),
]
