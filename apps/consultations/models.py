"""Models de Consulta e documentos médicos."""
import uuid
import shortuuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _generate_consultation_code():
    return shortuuid.ShortUUID(alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789").random(10)


class Consultation(models.Model):
    class Type(models.TextChoices):
        INSTANT   = "instant",   _("Pronto Atendimento")
        SCHEDULED = "scheduled", _("Agendada")

    class Status(models.TextChoices):
        WAITING     = "waiting",     _("Aguardando")
        IN_HELPDESK = "in_helpdesk", _("Em atendimento — Helpdesk")
        RELEASED    = "released",    _("Liberado para médico")
        IN_PROGRESS = "in_progress", _("Em atendimento — Médico")
        FINISHED    = "finished",    _("Finalizada")
        CANCELLED   = "cancelled",   _("Cancelada")
        NO_SHOW     = "no_show",     _("Não compareceu")

    class PaymentStatus(models.TextChoices):
        FREE = "free"; PENDING = "pending"; PAID = "paid"; REFUNDED = "refunded"

    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code             = models.CharField(max_length=10, unique=True, default=_generate_consultation_code, editable=False)
    clinic           = models.ForeignKey("clinics.Clinic", on_delete=models.PROTECT, related_name="consultations")
    patient          = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="consultations")
    doctor           = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT, null=True, blank=True, related_name="consultations")
    specialty        = models.ForeignKey("clinics.Specialty", on_delete=models.SET_NULL, null=True, blank=True)
    consultation_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INSTANT)
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    payment_status   = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.FREE)
    price            = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    requested_at     = models.DateTimeField(default=timezone.now)
    scheduled_for    = models.DateTimeField(null=True, blank=True)
    started_at       = models.DateTimeField(null=True, blank=True)
    finished_at      = models.DateTimeField(null=True, blank=True)
    patient_token    = models.CharField(max_length=200, blank=True, editable=False)
    patient_token_expires_at = models.DateTimeField(null=True, blank=True)
    internal_notes   = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Consulta")
        ordering = ["-requested_at"]
        indexes = [models.Index(fields=["clinic", "status"]), models.Index(fields=["code"])]

    def __str__(self):
        return f"Consulta {self.code} — {self.patient}"

    def save(self, *args, **kwargs):
        if not self.patient_token:
            self.patient_token = self.patient.generate_magic_link(expires_in_hours=48)
            self.patient_token_expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    def transition_to(self, new_status, by_user=None):
        self.status = new_status
        now = timezone.now()
        if new_status == self.Status.IN_PROGRESS:
            self.started_at = now
        if new_status == self.Status.FINISHED and self.started_at:
            self.finished_at = now
        self.save()
        from apps.audit.models import AuditLog
        AuditLog.log(user=by_user, event_type=AuditLog.EventType.CONSULTATION_STATUS,
                     target_type="Consulta", target_id=self.code, clinic=self.clinic)
