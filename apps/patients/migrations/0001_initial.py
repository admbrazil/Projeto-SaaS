import uuid

import django.db.models.deletion
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
            name="PatientTag",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=50)),
                ("color", models.CharField(default="#6c757d", max_length=7)),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="patient_tags", to="clinics.clinic")),
            ],
            options={"unique_together": {("clinic", "name")}},
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("cpf", models.CharField(max_length=11, verbose_name="CPF")),
                ("cpf_hash", models.CharField(db_index=True, editable=False, max_length=64, verbose_name="Hash CPF (busca)")),
                ("full_name", models.CharField(max_length=255, verbose_name="Nome completo")),
                ("birth_date", models.DateField(verbose_name="Data de nascimento")),
                ("gender", models.CharField(blank=True, choices=[("M", "Masculino"), ("F", "Feminino"), ("O", "Outro"), ("N", "Prefiro não informar")], max_length=1)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("address_number", models.CharField(blank=True, max_length=20)),
                ("neighborhood", models.CharField(blank=True, max_length=100)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("state", models.CharField(blank=True, max_length=2)),
                ("zip_code", models.CharField(blank=True, max_length=8)),
                ("lgpd_consent_at", models.DateTimeField(blank=True, null=True)),
                ("lgpd_consent_version", models.CharField(blank=True, max_length=10)),
                ("lgpd_consent_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("is_anonymized", models.BooleanField(default=False, verbose_name="Dados anonimizados")),
                ("anonymized_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="patients", to="clinics.clinic")),
                ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="patient_profile", to=settings.AUTH_USER_MODEL)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="patients_created", to=settings.AUTH_USER_MODEL)),
                ("tags", models.ManyToManyField(blank=True, related_name="patients", to="patients.patienttag")),
            ],
            options={"verbose_name": "Paciente", "verbose_name_plural": "Pacientes", "unique_together": {("clinic", "cpf")}},
        ),
        migrations.AddIndex(model_name="patient", index=models.Index(fields=["clinic", "cpf_hash"], name="patients_patient_clinic_cpf_hash_idx")),
        migrations.AddIndex(model_name="patient", index=models.Index(fields=["clinic", "full_name"], name="patients_patient_clinic_name_idx")),
        migrations.CreateModel(
            name="PatientAttachment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("file", models.FileField(upload_to="patient_attachments/%Y/%m/")),
                ("name", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="patients.patient")),
                ("uploaded_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Anexo"},
        ),
    ]
