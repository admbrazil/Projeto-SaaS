from django.contrib import admin
from .models import Patient, PatientTag

admin.site.register(Patient)
admin.site.register(PatientTag)
