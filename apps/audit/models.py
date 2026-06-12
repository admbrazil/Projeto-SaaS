"""Audit log imutável — registra todos os eventos de segurança."""
import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS         = "login_success",         _("Login bem-sucedido")
        LOGIN_FAILED          = "login_failed",          _("Falha de login")
        LOGOUT                = "logout",                _("Logout")
        LOCKOUT               = "lockout",               _("Conta bloqueada")
        MAGIC_LINK            = "magic_link",            _("Acesso via Magic Link")
        PASSWORD_CHANGE       = "password_change",       _("Troca de senha")
        CONSULTATION_CREATED  = "consultation_created",  _("Consulta criada")
        CONSULTATION_STATUS   = "consultation_status",   _("Status de consulta alterado")
        CONSULTATION_CANCELLED = "consultation_cancelled", _("Consulta cancelada")
        DOCUMENT_ISSUED       = "document_issued",       _("Documento médico emitido")
        API_ACCESS            = "api_access",            _("Acesso à API")
        API_ERROR             = "api_error",             _("Erro de API")
        LGPD_CONSENT          = "lgpd_consent",         _("Consentimento LGPD registrado")
        LGPD_REQUEST          = "lgpd_request",         _("Solicitação LGPD criada")
        DATA_EXPORT           = "data_export",          _("Exportação de dados")
        DATA_ANONYMIZED       = "data_anonymized",      _("Dados anonimizados")

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type   = models.CharField(max_length=40, choices=EventType.choices, db_index=True)
    user         = models.ForeignKey("accounts.User", on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name="audit_logs")
    clinic       = models.ForeignKey("clinics.Clinic", on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name="audit_logs")
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    target_type  = models.CharField(max_length=50, blank=True)
    target_id    = models.CharField(max_length=100, blank=True)
    description  = models.TextField(blank=True)
    extra_data   = models.JSONField(default=dict, blank=True)
    success      = models.BooleanField(default=True)
    timestamp    = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = _("Log de Auditoria")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["event_type", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.event_type} — {self.user or 'anon'}"

    @classmethod
    def log(cls, event_type, user=None, ip="", target_type="", target_id="",
            description="", extra_data=None, clinic=None, success=True, request=None):
        if request and not ip:
            xff = request.META.get("HTTP_X_FORWARDED_FOR")
            ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")
        if request and not clinic and hasattr(request, "clinic"):
            clinic = request.clinic
        cls.objects.create(
            event_type=event_type, user=user, clinic=clinic,
            ip_address=ip or None, target_type=target_type,
            target_id=str(target_id), description=description,
            extra_data=extra_data or {}, success=success,
        )
