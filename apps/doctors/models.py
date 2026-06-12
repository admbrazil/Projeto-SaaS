"""Model de Médico e disponibilidade de agenda."""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Doctor(models.Model):
    """Médico vinculado a uma clínica."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey("clinics.Clinic", on_delete=models.CASCADE, related_name="doctors")
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="doctor_profile")
    crm = models.CharField(max_length=20, verbose_name=_("CRM"))
    crm_state = models.CharField(max_length=2, verbose_name=_("Estado do CRM"))
    specialties = models.ManyToManyField("clinics.Specialty", blank=True, related_name="doctors")
    weekly_hours = models.PositiveSmallIntegerField(default=9, verbose_name=_("Horas disponíveis/semana"))
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_ping = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Médico")
        unique_together = ("clinic", "crm", "crm_state")

    def __str__(self):
        return f"Dr(a). {self.user.full_name} — CRM {self.crm}-{self.crm_state}"

    @property
    def full_crm(self):
        return f"{self.crm}-{self.crm_state}"


class DoctorAvailability(models.Model):
    """Disponibilidade semanal do médico para agendamento."""

    class WeekDay(models.IntegerChoices):
        MONDAY    = 0, _("Segunda-feira")
        TUESDAY   = 1, _("Terça-feira")
        WEDNESDAY = 2, _("Quarta-feira")
        THURSDAY  = 3, _("Quinta-feira")
        FRIDAY    = 4, _("Sexta-feira")
        SATURDAY  = 5, _("Sábado")
        SUNDAY    = 6, _("Domingo")

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="availability")
    weekday = models.IntegerField(choices=WeekDay.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveSmallIntegerField(default=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Disponibilidade")
        unique_together = ("doctor", "weekday", "start_time")

    def __str__(self):
        return f"{self.doctor} — {self.get_weekday_display()} {self.start_time}-{self.end_time}"
