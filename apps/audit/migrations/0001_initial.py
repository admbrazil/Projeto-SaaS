import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("clinics", "0001_initial"),
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_cpf_snapshot", models.CharField(blank=True, help_text="CPF no momento do evento (preservado mesmo se user deletado)", max_length=11)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                ("event_type", models.CharField(choices=[("login_success", "Login bem-sucedido"), ("login_failed", "Falha de login"), ("logout", "Logout"), ("lockout", "Conta bloqueada"), ("magic_link", "Acesso via Magic Link"), ("consultation_created", "Consulta criada"), ("consultation_status", "Status da consulta alterado"), ("consultation_finished", "Consulta finalizada"), ("document_created", "Documento médico emitido"), ("document_accessed", "Documento médico acessado"), ("consent_given", "Consentimento registrado"), ("consent_revoked", "Consentimento revogado"), ("lgpd_request", "Solicitação LGPD"), ("data_exported", "Dados exportados"), ("data_anonymized", "Dados anonimizados"), ("api_access", "Acesso à API"), ("api_error", "Erro na API"), ("webhook_sent", "Webhook disparado"), ("user_created", "Usuário criado"), ("user_updated", "Usuário atualizado"), ("settings_changed", "Configurações alteradas")], max_length=50)),
                ("target_type", models.CharField(blank=True, max_length=100, verbose_name="Tipo do objeto")),
                ("target_id", models.CharField(blank=True, max_length=100, verbose_name="ID do objeto")),
                ("description", models.TextField(blank=True)),
                ("extra_data", models.JSONField(blank=True, default=dict, verbose_name="Dados extras")),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("success", models.BooleanField(default=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to=settings.AUTH_USER_MODEL)),
                ("clinic", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="clinics.clinic")),
            ],
            options={"verbose_name": "Log de Auditoria", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="auditlog", index=models.Index(fields=["clinic", "created_at"], name="audit_log_clinic_created_idx")),
        migrations.AddIndex(model_name="auditlog", index=models.Index(fields=["user", "created_at"], name="audit_log_user_created_idx")),
        migrations.AddIndex(model_name="auditlog", index=models.Index(fields=["event_type", "created_at"], name="audit_log_event_created_idx")),
    ]
