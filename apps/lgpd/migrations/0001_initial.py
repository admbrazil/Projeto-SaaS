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
        ("patients", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ConsentVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.CharField(max_length=10, unique=True, verbose_name="Versão")),
                ("effective_date", models.DateField(verbose_name="Vigência a partir de")),
                ("terms_url", models.URLField(verbose_name="URL dos Termos")),
                ("privacy_url", models.URLField(verbose_name="URL da Política de Privacidade")),
                ("summary", models.TextField(verbose_name="Resumo das mudanças")),
                ("is_current", models.BooleanField(default=False, verbose_name="Versão atual")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "Versão dos Termos", "ordering": ["-effective_date"]},
        ),
        migrations.CreateModel(
            name="UserConsent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("accepted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("ip_address", models.GenericIPAddressField(verbose_name="IP no momento do consentimento")),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                ("consent_terms", models.BooleanField(default=True, verbose_name="Termos de uso")),
                ("consent_privacy", models.BooleanField(default=True, verbose_name="Política de privacidade")),
                ("consent_health_data", models.BooleanField(default=True, verbose_name="Tratamento de dados de saúde")),
                ("consent_communications", models.BooleanField(default=False, verbose_name="Comunicações de marketing")),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("revoke_reason", models.CharField(blank=True, max_length=255)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="consents", to=settings.AUTH_USER_MODEL)),
                ("version", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="lgpd.consentversion")),
            ],
            options={"verbose_name": "Consentimento", "ordering": ["-accepted_at"]},
        ),
        migrations.CreateModel(
            name="LGPDRequest",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("protocol", models.CharField(editable=False, max_length=20, unique=True, verbose_name="Protocolo")),
                ("requester_email", models.EmailField(verbose_name="E-mail do solicitante")),
                ("requester_name", models.CharField(max_length=255)),
                ("request_type", models.CharField(choices=[("access", "Acesso aos dados (Art. 18, II)"), ("correction", "Correção de dados (Art. 18, III)"), ("anonymization", "Anonimização (Art. 18, IV)"), ("deletion", "Eliminação dos dados (Art. 18, VI)"), ("portability", "Portabilidade (Art. 18, V)"), ("revoke_consent", "Revogação de consentimento (Art. 18, IX)"), ("information", "Informação sobre tratamento (Art. 18, I)")], max_length=20)),
                ("description", models.TextField(verbose_name="Descrição da solicitação")),
                ("status", models.CharField(choices=[("pending", "Aguardando análise"), ("in_review", "Em análise"), ("completed", "Concluída"), ("rejected", "Indeferida")], default="pending", max_length=20)),
                ("response", models.TextField(blank=True, verbose_name="Resposta ao titular")),
                ("rejection_reason", models.TextField(blank=True)),
                ("requested_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("deadline", models.DateField(verbose_name="Prazo de resposta")),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("exported_file", models.FileField(blank=True, null=True, upload_to="lgpd_exports/")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="lgpd_requests", to=settings.AUTH_USER_MODEL)),
                ("patient", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="lgpd_requests", to="patients.patient")),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lgpd_assigned", to=settings.AUTH_USER_MODEL, verbose_name="Responsável")),
            ],
            options={"verbose_name": "Solicitação LGPD", "ordering": ["-requested_at"]},
        ),
        migrations.CreateModel(
            name="DataProcessingRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255, verbose_name="Nome da operação")),
                ("purpose", models.TextField(verbose_name="Finalidade")),
                ("legal_basis", models.CharField(help_text="Ex: Art. 7°, VIII — legítimo interesse; Art. 11, II, f — saúde", max_length=100, verbose_name="Base legal")),
                ("data_categories", models.TextField(verbose_name="Categorias de dados")),
                ("data_subjects", models.CharField(help_text="Ex: pacientes, médicos", max_length=255, verbose_name="Titulares")),
                ("retention_period", models.CharField(max_length=100, verbose_name="Prazo de retenção")),
                ("third_parties", models.TextField(blank=True, verbose_name="Terceiros envolvidos")),
                ("security_measures", models.TextField(blank=True, verbose_name="Medidas de segurança")),
                ("cross_border_transfer", models.BooleanField(default=False, verbose_name="Transferência internacional")),
                ("last_review", models.DateField(verbose_name="Última revisão")),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_records", to="clinics.clinic")),
            ],
            options={"verbose_name": "Registro de Tratamento (ROPA)"},
        ),
    ]
