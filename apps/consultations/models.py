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
        FREE     = "free",     _("Gratuita")
        PENDING  = "pending",  _("Aguardando pagamento")
        PAID     = "paid",     _("Pago")
        REFUNDED = "refunded", _("Reembolsado")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True, default=_generate_consultation_code, editable=False)
    clinic = models.ForeignKey("clinics.Clinic", on_delete=models.PROTECT, related_name="consultations")
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="consultations")
    doctor = models.ForeignKey("doctors.Doctor", on_delete=models.PROTECT, null=True, blank=True, related_name="consultations")
    specialty = models.ForeignKey("clinics.Specialty", on_delete=models.SET_NULL, null=True, blank=True)
    consultation_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INSTANT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.FREE)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    requested_at = models.DateTimeField(default=timezone.now, verbose_name=_("Solicitada em"))
    scheduled_for = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    patient_token = models.CharField(max_length=200, blank=True, editable=False)
    patient_token_expires_at = models.DateTimeField(null=True, blank=True)
    helpdesk_wait_seconds = models.PositiveIntegerField(default=0)
    doctor_wait_seconds = models.PositiveIntegerField(default=0)
    consultation_duration_seconds = models.PositiveIntegerField(default=0)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="+")

    class Meta:
        verbose_name = _("Consulta")
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["clinic", "status"]),
            models.Index(fields=["clinic", "requested_at"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return f"Consulta {self.code} — {self.patient}"

    def save(self, *args, **kwargs):
        if not self.patient_token:
            self.patient_token = self.patient.generate_magic_link(expires_in_hours=48)
            self.patient_token_expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    @property
    def doctor_url(self):
        if self.clinic:
            return f"{self.clinic.base_url}/painel/medicos/atendimento/{self.code}/"
        return f"/painel/medicos/atendimento/{self.code}/"

    def transition_to(self, new_status: str, by_user=None):
        old_status = self.status
        self.status = new_status
        now = timezone.now()
        if new_status == self.Status.IN_PROGRESS and self.requested_at:
            self.started_at = now
        if new_status == self.Status.FINISHED and self.started_at:
            self.finished_at = now
            self.consultation_duration_seconds = int((now - self.started_at).total_seconds())
        self.save()
        from apps.audit.models import AuditLog
        AuditLog.log(user=by_user, action=f"status_{new_status}",
                     target_type="Consulta", target_id=self.code, clinic=self.clinic)


class MedicalDocument(models.Model):
    class DocType(models.TextChoices):
        PRESCRIPTION = "prescription", _("Receita Médica")
        CERTIFICATE  = "certificate",  _("Atestado Médico")
        REFERRAL     = "referral",     _("Encaminhamento")
        EXAM_REQUEST = "exam_request", _("Solicitação de Exame")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    content = models.JSONField(default=dict, verbose_name=_("Conteúdo"))
    cid_code = models.CharField(max_length=10, blank=True, verbose_name=_("CID"))
    cid_description = models.CharField(max_length=255, blank=True)
    pdf_file = models.FileField(upload_to="medical_docs/%Y/%m/", null=True, blank=True)
    issued_at = models.DateTimeField(default=timezone.now)
    issued_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")

    class Meta:
        verbose_name = _("Documento Médico")


class ConsultationEvaluation(models.Model):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name="evaluation")
    score = models.PositiveSmallIntegerField(verbose_name=_("Nota"))
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Avaliação")

    def __str__(self):
        return f"Avaliação {self.score}/10 — {self.consultation}"
