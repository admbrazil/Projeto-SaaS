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
            name="Doctor",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("crm", models.CharField(max_length=20, verbose_name="CRM")),
                ("crm_state", models.CharField(max_length=2, verbose_name="Estado do CRM")),
                ("weekly_hours", models.PositiveSmallIntegerField(default=9, verbose_name="Horas disponíveis/semana")),
                ("is_active", models.BooleanField(default=True)),
                ("is_online", models.BooleanField(default=False)),
                ("last_ping", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("clinic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="doctors", to="clinics.clinic")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="doctor_profile", to=settings.AUTH_USER_MODEL)),
                ("specialties", models.ManyToManyField(blank=True, related_name="doctors", to="clinics.specialty")),
            ],
            options={"verbose_name": "Médico", "unique_together": {("clinic", "crm", "crm_state")}},
        ),
        migrations.CreateModel(
            name="DoctorAvailability",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.IntegerField(choices=[(0, "Segunda-feira"), (1, "Terça-feira"), (2, "Quarta-feira"), (3, "Quinta-feira"), (4, "Sexta-feira"), (5, "Sábado"), (6, "Domingo")])),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("slot_duration_minutes", models.PositiveSmallIntegerField(default=20)),
                ("is_active", models.BooleanField(default=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="availability", to="doctors.doctor")),
            ],
            options={"verbose_name": "Disponibilidade", "unique_together": {("doctor", "weekday", "start_time")}},
        ),
    ]
