"""Model de Paciente com conformidade LGPD completa."""
import hashlib, hmac, secrets, time, uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _hash_cpf(cpf):
    return hmac.new(settings.SECRET_KEY.encode(), cpf.encode(), hashlib.sha256).hexdigest()


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "M"; FEMALE = "F"; OTHER = "O"; PREFER_NOT = "N"

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic       = models.ForeignKey("clinics.Clinic", on_delete=models.PROTECT, related_name="patients")
    cpf          = models.CharField(max_length=11)
    cpf_hash     = models.CharField(max_length=64, db_index=True, editable=False)
    full_name    = models.CharField(max_length=255)
    birth_date   = models.DateField()
    gender       = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    phone        = models.CharField(max_length=20, blank=True)
    email        = models.EmailField(blank=True)
    address      = models.CharField(max_length=255, blank=True)
    city         = models.CharField(max_length=100, blank=True)
    state        = models.CharField(max_length=2, blank=True)
    zip_code     = models.CharField(max_length=8, blank=True)
    lgpd_consent_at = models.DateTimeField(null=True, blank=True)
    lgpd_consent_version = models.CharField(max_length=10, blank=True)
    is_anonymized = models.BooleanField(default=False)
    anonymized_at = models.DateTimeField(null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    user         = models.OneToOneField("accounts.User", on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="patient_profile")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Paciente")
        unique_together = ("clinic", "cpf")
        indexes = [models.Index(fields=["clinic", "cpf_hash"])]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.cpf_hash = _hash_cpf(self.cpf)
        super().save(*args, **kwargs)

    @property
    def cpf_masked(self):
        if len(self.cpf) == 11:
            return f"***.***.*{self.cpf[7:9]}-{self.cpf[9:]}"
        return "***.***.***-**"

    def generate_magic_link(self, expires_in_hours=24):
        expires_at = int(time.time()) + (expires_in_hours * 3600)
        payload = f"{self.pk}.{expires_at}"
        signature = hmac.new(settings.MAGIC_LINK_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return f"/paciente/patient-login/{payload}.{signature}/"

    @classmethod
    def verify_magic_link(cls, token):
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
        expected = hmac.new(settings.MAGIC_LINK_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Assinatura inválida.")
        try:
            return cls.objects.get(pk=patient_id)
        except cls.DoesNotExist:
            raise ValueError("Paciente não encontrado.")

    def anonymize(self):
        anon_id = f"ANON-{secrets.token_hex(8).upper()}"
        self.cpf = "00000000000"; self.cpf_hash = _hash_cpf("00000000000")
        self.full_name = anon_id; self.phone = ""; self.email = ""
        self.address = ""; self.city = ""; self.state = ""; self.zip_code = ""
        self.is_anonymized = True; self.anonymized_at = timezone.now(); self.is_active = False
        self.save()
