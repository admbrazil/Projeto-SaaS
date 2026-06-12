import sys
import traceback as _tb

_IMPORT_ERROR = None

try:
    from django.contrib import admin
    from .models import Consultation, MedicalDocument

    @admin.register(Consultation)
    class ConsultationAdmin(admin.ModelAdmin):
        list_display = ("code", "patient", "doctor", "consultation_type", "status", "payment_status", "requested_at")
        list_filter = ("status", "consultation_type", "payment_status", "clinic")
        search_fields = ("code", "patient__full_name", "doctor__user__full_name")
        ordering = ("-requested_at",)
        readonly_fields = ("code", "patient_token", "patient_token_expires_at", "created_at", "updated_at")

    @admin.register(MedicalDocument)
    class MedicalDocumentAdmin(admin.ModelAdmin):
        list_display = ("consultation", "doc_type", "cid_code", "issued_at", "issued_by")
        list_filter = ("doc_type",)
        search_fields = ("consultation__code", "cid_code")
        ordering = ("-issued_at",)

except Exception:
    _IMPORT_ERROR = _tb.format_exc()
    print("[ADMIN_ERROR] apps.consultations.admin:\n" + _IMPORT_ERROR, file=sys.stderr)
