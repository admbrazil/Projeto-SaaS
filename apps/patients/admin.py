from django.contrib import admin
from .models import Patient, PatientTag


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "cpf_masked_display", "clinic", "city", "state", "is_active")
    list_filter = ("is_active", "clinic", "state", "gender")
    search_fields = ("full_name", "cpf", "email", "phone")
    ordering = ("full_name",)
    readonly_fields = ("cpf_hash", "created_at", "updated_at")

    def cpf_masked_display(self, obj):
        return obj.cpf_masked
    cpf_masked_display.short_description = "CPF"


@admin.register(PatientTag)
class PatientTagAdmin(admin.ModelAdmin):
    list_display = ("name", "clinic", "color")
    search_fields = ("name",)
