import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("clinics", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("cpf", models.CharField(help_text="Somente dígitos, sem pontuação.", max_length=11, unique=True, verbose_name="CPF")),
                ("full_name", models.CharField(max_length=255, verbose_name="Nome completo")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-mail")),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="Telefone")),
                ("role", models.CharField(choices=[("platform_admin", "Administrador da Plataforma"), ("clinic_admin", "Administrador da Clínica"), ("clinic_manager", "Gestor da Clínica"), ("doctor", "Médico da Clínica"), ("helpdesk", "Helpdesk"), ("patient", "Paciente")], default="patient", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("failed_login_attempts", models.PositiveSmallIntegerField(default=0)),
                ("locked_until", models.DateTimeField(blank=True, null=True)),
                ("lgpd_consent_at", models.DateTimeField(blank=True, null=True, verbose_name="Consentimento LGPD em")),
                ("lgpd_consent_version", models.CharField(blank=True, max_length=10, verbose_name="Versão dos termos")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("last_login_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("clinic", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="users", to="clinics.clinic", verbose_name="Clínica")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"verbose_name": "Usuário", "verbose_name_plural": "Usuários"},
        ),
        migrations.AddIndex(model_name="user", index=models.Index(fields=["cpf"], name="accounts_user_cpf_idx")),
        migrations.AddIndex(model_name="user", index=models.Index(fields=["clinic", "role"], name="accounts_user_clinic_role_idx")),
    ]
