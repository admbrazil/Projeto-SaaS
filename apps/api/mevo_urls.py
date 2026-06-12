from django.urls import path
from .views import MevoDataView
urlpatterns = [
    path("check-clinics-mevo-data/", MevoDataView.as_view(), name="mevo_data"),
]
