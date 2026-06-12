"""Model de Agendamento."""
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Agendado")
        CONFIRMED = "confirmed", _("Confirmado")
        CANCELLED = "cancelled", _("Cancelado")
        COMPLETED = "completed", _("Realizado")
        NO_SHOW   = "no_show",   _("Não compareceu")

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic      = models.ForeignKey("clinics.Clinic", on_delete=models.PROTECT, related_name="appointments")
    patient     = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="appointments")
    doctor      = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT, related_name="appointments", null=True, blank=True)
    specialty   = models.ForeignKey("clinics.Specialty", on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Agendamento")
        ordering = ["scheduled_at"]
        indexes = [models.Index(fields=["clinic", "scheduled_at", "status"])]

    def __str__(self):
        return f"{self.patient} — {self.scheduled_at:%d/%m/%Y %H:%M}"
