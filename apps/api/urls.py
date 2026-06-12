from django.urls import path
from . import views
app_name = "api"
urlpatterns = [
    path("add-consultation/", views.ConsultationCreateView.as_view(), name="add_consultation"),
    path("consultations/", views.ConsultationListView.as_view(), name="consultations"),
    path("consultation/<str:code>/", views.ConsultationDetailView.as_view(), name="consultation_detail"),
    path("consultation/<str:code>/cancel/", views.ConsultationCancelView.as_view(), name="cancel_consultation"),
]
