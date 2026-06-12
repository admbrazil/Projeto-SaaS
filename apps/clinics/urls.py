from django.urls import path
from . import views

app_name = "clinics"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pacientes/", views.pacientes_list, name="pacientes"),
    path("medicos/", views.medicos_list, name="medicos"),
    path("consultas/", views.consultas_list, name="consultas"),
]
