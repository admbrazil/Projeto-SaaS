"""Models de Clínica, Especialidade e Token de API."""
import uuid, secrets
from django.db import models
from django.utils.translation import gettext_lazy as _


class Clinic(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, help_text="Usado como subdomínio: slug.telesaas.com.br")
    cnpj        = models.CharField(max_length=14, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    email       = models.EmailField(blank=True)
    address     = models.CharField(max_length=255, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    state       = models.CharField(max_length=2, blank=True)
    logo        = models.ImageField(upload_to="clinic_logos/", null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#0066cc")
    is_active   = models.BooleanField(default=True)
    max_patients = models.PositiveIntegerField(default=500)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Clínica")

    def __str__(self):
        return self.name


class Specialty(models.Model):
    clinic    = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="specialties")
    name      = models.CharField(max_length=100)
    cbo_code  = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("clinic", "name")

    def __str__(self):
        return f"{self.name} ({self.clinic})"


class ClinicAPIToken(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic     = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="api_tokens")
    name       = models.CharField(max_length=100, help_text="Descrição do token (ex: Integração MEVO)")
    token      = models.CharField(max_length=64, unique=True, editable=False, db_index=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used  = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clinic} — {self.name}"
