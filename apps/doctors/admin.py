from django.contrib import admin
from .models import Doctor, DoctorAvailability


class DoctorAvailabilityInline(admin.TabularInline):
    model = DoctorAvailability
    extra = 0


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "clinic", "full_crm", "is_active", "is_online")
    list_filter = ("is_active", "is_online", "clinic")
    search_fields = ("user__full_name", "crm")
    ordering = ("user__full_name",)
    inlines = [DoctorAvailabilityInline]
