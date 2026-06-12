"""Módulo LGPD — Lei Geral de Proteção de Dados (Lei 13.709/2018)."""
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ConsentVersion(models.Model):
    version        = models.CharField(max_length=10, unique=True)
    effective_date = models.DateField()
    terms_url      = models.URLField()
    privacy_url    = models.URLField()
    summary        = models.TextField()
    is_current     = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-effective_date"]

    def __str__(self):
        return f"v{self.version} ({self.effective_date})"

    def save(self, *args, **kwargs):
        if self.is_current:
            ConsentVersion.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_current=True).first()


class UserConsent(models.Model):
    id                    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user                  = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="consents")
    version               = models.ForeignKey(ConsentVersion, on_delete=models.PROTECT)
    accepted_at           = models.DateTimeField(default=timezone.now)
    ip_address            = models.GenericIPAddressField()
    user_agent            = models.CharField(max_length=500, blank=True)
    consent_terms         = models.BooleanField(default=True)
    consent_privacy       = models.BooleanField(default=True)
    consent_health_data   = models.BooleanField(default=True)
    consent_communications = models.BooleanField(default=False)
    revoked_at            = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return self.revoked_at is None


class LGPDRequest(models.Model):
    class RequestType(models.TextChoices):
        ACCESS         = "access",         _("Acesso aos dados (Art. 18, II)")
        CORRECTION     = "correction",     _("Correção de dados (Art. 18, III)")
        ANONYMIZATION  = "anonymization",  _("Anonimização (Art. 18, IV)")
        DELETION       = "deletion",       _("Eliminação dos dados (Art. 18, VI)")
        PORTABILITY    = "portability",    _("Portabilidade (Art. 18, V)")
        REVOKE_CONSENT = "revoke_consent", _("Revogação de consentimento (Art. 18, IX)")
        INFORMATION    = "information",    _("Informação sobre tratamento (Art. 18, I)")

    class Status(models.TextChoices):
        PENDING   = "pending",   _("Aguardando análise")
        IN_REVIEW = "in_review", _("Em análise")
        COMPLETED = "completed", _("Concluída")
        REJECTED  = "rejected",  _("Indeferida")

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    protocol        = models.CharField(max_length=20, unique=True, editable=False)
    user            = models.ForeignKey("accounts.User", on_delete=models.PROTECT,
                                         null=True, blank=True, related_name="lgpd_requests")
    requester_email = models.EmailField()
    requester_name  = models.CharField(max_length=255)
    request_type    = models.CharField(max_length=20, choices=RequestType.choices)
    description     = models.TextField()
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    response        = models.TextField(blank=True)
    requested_at    = models.DateTimeField(default=timezone.now)
    deadline        = models.DateField(blank=True)
    completed_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"[{self.protocol}] {self.get_request_type_display()}"

    def save(self, *args, **kwargs):
        if not self.protocol:
            self.protocol = self._generate_protocol()
        if not self.deadline:
            from datetime import timedelta
            from django.conf import settings
            days = getattr(settings, "LGPD_RESPONSE_DAYS", 15)
            self.deadline = (timezone.now() + timedelta(days=days)).date()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_protocol():
        import secrets
        return f"LGPD-{timezone.now().strftime('%Y%m')}-{secrets.token_hex(3).upper()}"
