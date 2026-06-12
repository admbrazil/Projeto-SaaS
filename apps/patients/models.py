"""
Model de Paciente com conformidade LGPD completa.
"""
import hashlib
import hmac
import secrets
import time
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _hash_cpf(cpf: str) -> str:
    """Hash HMAC-SHA256 do CPF para busca sem expor o valor real."""
    return hmac.new(
        settings.SECRET_KEY.encode(),
        cpf.encode(),
        hashlib.sha256,
    ).hexdigest()


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE   = "M", _("Masculino")
        FEMALE = "F", _("Feminino")
        OTHER  = "O", _("Outro")
        PREFER_NOT = "N", _("Prefiro não informar")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(
        "clinics.Clinic", on_delete=models.PROTECT, related_name="patients"
    )
    cpf = models.CharField(max_length=11, verbose_name=_("CPF"))
    cpf_hash = models.CharField(max_length=64, db_index=True, editable=False,
                                 verbose_name=_("Hash CPF (busca)"))
    full_name = models.CharField(max_length=255, verbose_name=_("Nome completo"))
    birth_date = models.DateField(verbose_name=_("Data de nascimento"))
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    address_number = models.CharField(max_length=20, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=8, blank=True)
    lgpd_consent_at = models.DateTimeField(null=True, blank=True)
    lgpd_consent_version = models.CharField(max_length=10, blank=True)
    lgpd_consent_ip = models.GenericIPAddressField(null=True, blank=True)
    is_anonymized = models.BooleanField(default=False, verbose_name=_("Dados anonimizados"))
    anonymized_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField("PatientTag", blank=True, related_name="patients")
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="patient_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="patients_created",
    )

    class Meta:
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")
        unique_together = ("clinic", "cpf")
        indexes = [
            models.Index(fields=["clinic", "cpf_hash"]),
            models.Index(fields=["clinic", "full_name"]),
        ]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.cpf_hash = _hash_cpf(self.cpf)
        super().save(*args, **kwargs)

    @property
    def cpf_masked(self) -> str:
        if len(self.cpf) == 11:
            return f"***.***.*{self.cpf[7:9]}-{self.cpf[9:]}"
        return "***.***.***-**"

    @property
    def age(self) -> int:
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def generate_magic_link(self, expires_in_hours: int = 24) -> str:
        expires_at = int(time.time()) + (expires_in_hours * 3600)
        payload = f"{self.pk}.{expires_at}"
        signature = hmac.new(
            settings.MAGIC_LINK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        token = f"{payload}.{signature}"
        return f"/paciente/patient-login/{token}/"

    @classmethod
    def verify_magic_link(cls, token: str):
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Token malformado.")
        patient_id, expires_at_str, signature = parts
        try:
            expires_at = int(expires_at_str)
        except ValueError:
            raise ValueError("Token inválido.")
        if time.time() > expires_at:
            raise ValueError("Token expirado.")
        payload = f"{patient_id}.{expires_at_str}"
        expected = hmac.new(
            settings.MAGIC_LINK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Assinatura inválida.")
        try:
            return cls.objects.get(pk=patient_id)
        except cls.DoesNotExist:
            raise ValueError("Paciente não encontrado.")

    def anonymize(self, reason: str = "user_request"):
        anon_id = f"ANON-{secrets.token_hex(8).upper()}"
        self.cpf = "00000000000"
        self.cpf_hash = _hash_cpf("00000000000")
        self.full_name = anon_id
        self.phone = ""; self.email = ""; self.address = ""
        self.address_number = ""; self.neighborhood = ""
        self.city = ""; self.state = ""; self.zip_code = ""
        self.is_anonymized = True
        self.anonymized_at = timezone.now()
        self.is_active = False
        self.save()


class PatientTag(models.Model):
    """Tag para segmentação de pacientes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey("clinics.Clinic", on_delete=models.CASCADE, related_name="patient_tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#6c757d")

    class Meta:
        unique_together = ("clinic", "name")

    def __str__(self):
        return self.name


class PatientAttachment(models.Model):
    """Anexos do paciente."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="patient_attachments/%Y/%m/")
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Anexo")
