import sys
import traceback as _tb

_IMPORT_ERROR = None

try:
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

except Exception:
    _IMPORT_ERROR = _tb.format_exc()
    print("[ADMIN_ERROR] apps.doctors.admin:\n" + _IMPORT_ERROR, file=sys.stderr)
