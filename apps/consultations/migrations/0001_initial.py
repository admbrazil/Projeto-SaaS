import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def _generate_consultation_code():
    import shortuuid
    return shortuuid.ShortUUID(alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789").random(10)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("clinics", "0001_initial"),
        ("patients", "0001_initial"),
        ("doctors", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Consultation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(default=_generate_consultation_code, editable=False, max_length=10, unique=True)),
                ("consultation_type", models.CharField(choices=[("instant", "Pronto Atendimento"), ("scheduled", "Agendada")], default="instant", max_length=20)),
                ("status", models.CharField(choices=[("waiting", "Aguardando"), ("in_helpdesk", "Em atendimento - Helpdesk"), ("released", "Liberado para médico"), ("in_progress", "Em atendimento - Médico"), ("finished", "Finalizada"), ("cancelled", "Cancelada"), ("no_show", "Não compareceu")], default="waiting", max_length=20)),
                ("payment_status", models.CharField(choices=[("free", "Gratuita"), ("pending", "Aguardando pagamento"), ("paid", "Pago"), ("refunded", "Reembolsado")], default="free", max_length=20)),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("requested_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="Solicitada em")),
                ("scheduled_for", models.DateTimeField(blank=True, null=True, verbose_name="Agendada para")),
                ("started_at", models.DateTimeField(blank=True, null=True, verbose_name="Iniciada em")),
                ("finished_at", models.DateTimeField(blank=True, null=True, verbose_name="Finalizada em")),
                ("patient_token", models.CharField(blank=True, editable=False, max_length=200)),
                ("patient_token_expires_at", models.DateTimeField(blank=True, null=True)),
                ("helpdesk_wait_seconds", models.PositiveIntegerField(default=0)),
                ("doctor_wait_seconds", models.PositiveIntegerField(default=0)),
                ("consultation_duration_seconds", models.PositiveIntegerField(default=0)),
                ("internal_notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="consultations", to="clinics.clinic")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="consultations", to="patients.patient")),
                ("doctor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="consultations", to="doctors.doctor")),
                ("specialty", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="clinics.specialty")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Consulta", "ordering": ["-requested_at"]},
        ),
        migrations.AddIndex(model_name="consultation", index=models.Index(fields=["clinic", "status"], name="consultations_clinic_status_idx")),
        migrations.AddIndex(model_name="consultation", index=models.Index(fields=["clinic", "requested_at"], name="consultations_clinic_req_at_idx")),
        migrations.AddIndex(model_name="consultation", index=models.Index(fields=["code"], name="consultations_code_idx")),
        migrations.CreateModel(
            name="MedicalDocument",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("doc_type", models.CharField(choices=[("prescription", "Receita Médica"), ("certificate", "Atestado Médico"), ("referral", "Encaminhamento"), ("exam_request", "Solicitação de Exame")], max_length=20)),
                ("content", models.JSONField(default=dict, verbose_name="Conteúdo")),
                ("cid_code", models.CharField(blank=True, max_length=10, verbose_name="CID")),
                ("cid_description", models.CharField(blank=True, max_length=255)),
                ("pdf_file", models.FileField(blank=True, null=True, upload_to="medical_docs/%Y/%m/")),
                ("issued_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("consultation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="consultations.consultation")),
                ("issued_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Documento Médico"},
        ),
        migrations.CreateModel(
            name="ConsultationEvaluation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveSmallIntegerField(help_text="0 a 10", verbose_name="Nota")),
                ("comment", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("consultation", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="evaluation", to="consultations.consultation")),
            ],
            options={"verbose_name": "Avaliação"},
        ),
    ]
