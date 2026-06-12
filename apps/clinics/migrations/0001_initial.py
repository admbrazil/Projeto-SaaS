import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Clinic",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255, verbose_name="Nome")),
                ("display_name", models.CharField(max_length=255, verbose_name="Nome de exibição")),
                ("cnpj", models.CharField(max_length=14, unique=True, verbose_name="CNPJ")),
                ("subdomain", models.SlugField(help_text="Ex: 'iguape' para iguape.telesaas.com.br", max_length=63, unique=True, verbose_name="Subdomínio")),
                ("address", models.CharField(blank=True, max_length=255)),
                ("address_number", models.CharField(blank=True, max_length=20)),
                ("neighborhood", models.CharField(blank=True, max_length=100)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("state", models.CharField(blank=True, max_length=2)),
                ("zip_code", models.CharField(blank=True, max_length=8)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="clinic_logos/")),
                ("favicon", models.ImageField(blank=True, null=True, upload_to="clinic_favicons/")),
                ("login_background", models.ImageField(blank=True, null=True, upload_to="clinic_login_bgs/")),
                ("enable_login_bg", models.BooleanField(default=False)),
                ("plan", models.CharField(choices=[("basic", "Básico"), ("standard", "Standard"), ("premium", "Premium"), ("enterprise", "Enterprise / Governo")], default="basic", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("feature_scheduling", models.BooleanField(default=True, verbose_name="Agendamento")),
                ("feature_instant_links", models.BooleanField(default=True, verbose_name="Links instantâneos")),
                ("feature_nr1", models.BooleanField(default=False, verbose_name="NR-1")),
                ("feature_webhooks", models.BooleanField(default=False, verbose_name="Webhooks")),
                ("feature_custom_domain", models.BooleanField(default=False, verbose_name="Domínio próprio")),
                ("feature_app", models.BooleanField(default=False, verbose_name="App mobile")),
                ("video_provider", models.CharField(default="jitsi", max_length=20)),
                ("video_api_key", models.CharField(blank=True, max_length=255)),
                ("dpo_name", models.CharField(blank=True, max_length=255, verbose_name="Nome do DPO")),
                ("dpo_email", models.EmailField(blank=True, verbose_name="E-mail do DPO")),
                ("privacy_policy_url", models.URLField(blank=True, verbose_name="URL da política de privacidade")),
                ("webhook_url", models.URLField(blank=True)),
                ("webhook_secret", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Clínica", "verbose_name_plural": "Clínicas"},
        ),
        migrations.CreateModel(
            name="Specialty",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, verbose_name="Nome")),
                ("is_active", models.BooleanField(default=True)),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="specialties", to="clinics.clinic")),
            ],
            options={"verbose_name": "Especialidade", "unique_together": {("clinic", "name")}},
        ),
        migrations.CreateModel(
            name="ClinicAPIToken",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("token", models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("clinic", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="api_token", to="clinics.clinic")),
            ],
            options={"verbose_name": "Token de API"},
        ),
        migrations.CreateModel(
            name="ClinicPlan",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference_period", models.CharField(max_length=7, verbose_name="Período (YYYY-MM)")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("pending", "Pendente"), ("paid", "Pago"), ("overdue", "Atrasado")], default="pending", max_length=20)),
                ("due_date", models.DateField()),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to="clinics.clinic")),
            ],
            options={"verbose_name": "Cobrança", "ordering": ["-due_date"]},
        ),
    ]
