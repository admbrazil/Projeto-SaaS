from django.contrib import admin
from .models import Clinic, Specialty


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "cnpj", "city", "state", "is_active", "created_at")
    list_filter = ("is_active", "state")
    search_fields = ("name", "cnpj", "city")
    ordering = ("name",)


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name", "clinic", "is_active")
    list_filter = ("is_active", "clinic")
    search_fields = ("name",)
