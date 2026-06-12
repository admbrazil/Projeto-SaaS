"""Model de Médico."""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Doctor(models.Model):
    class Status(models.TextChoices):
        AVAILABLE   = "available",   _("Disponível")
        IN_CONSULT  = "in_consult",  _("Em consulta")
        UNAVAILABLE = "unavailable", _("Indisponível")
        OFFLINE     = "offline",     _("Offline")

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="doctor_profile")
    clinic     = models.ForeignKey("clinics.Clinic", on_delete=models.PROTECT, related_name="doctors")
    crm        = models.CharField(max_length=20)
    crm_state  = models.CharField(max_length=2)
    specialties = models.ManyToManyField("clinics.Specialty", blank=True)
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    bio        = models.TextField(blank=True)
    photo      = models.ImageField(upload_to="doctor_photos/", null=True, blank=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Médico")
        unique_together = ("crm", "crm_state")

    def __str__(self):
        return f"Dr(a). {self.user.full_name} — CRM {self.crm}/{self.crm_state}"
