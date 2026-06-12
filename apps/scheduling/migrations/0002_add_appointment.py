import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scheduling", "0001_initial"),
        ("clinics", "0002_add_missing_fields"),
        ("patients", "0001_initial"),
        ("doctors", "0002_add_missing_fields"),
    ]
    operations = [
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("scheduled_at", models.DateTimeField()),
                ("duration_minutes", models.PositiveSmallIntegerField(default=30)),
                ("status", models.CharField(
                    max_length=20,
                    choices=[("scheduled","Agendado"),("confirmed","Confirmado"),("cancelled","Cancelado"),("completed","Realizado"),("no_show","Nao compareceu")],
                    default="scheduled",
                )),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("clinic", models.ForeignKey("clinics.Clinic", on_delete=django.db.models.deletion.PROTECT, related_name="appointments")),
                ("patient", models.ForeignKey("patients.Patient", on_delete=django.db.models.deletion.PROTECT, related_name="appointments")),
                ("doctor", models.ForeignKey("doctors.Doctor", on_delete=django.db.models.deletion.PROTECT, related_name="appointments", null=True, blank=True)),
                ("specialty", models.ForeignKey("clinics.Specialty", on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True)),
            ],
            options={"verbose_name": "Agendamento", "ordering": ["scheduled_at"]},
        ),
        migrations.AddIndex(
            model_name="appointment",
            index=models.Index(fields=["clinic", "scheduled_at", "status"], name="scheduling_appt_clinic_idx"),
        ),
    ]
