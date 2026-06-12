import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("doctors", "0001_initial"),
        ("clinics", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Schedule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("min_advance_hours", models.PositiveSmallIntegerField(default=1)),
                ("max_advance_days", models.PositiveSmallIntegerField(default=30)),
                ("slot_minutes", models.PositiveSmallIntegerField(default=20)),
                ("break_minutes", models.PositiveSmallIntegerField(default=5)),
                ("is_active", models.BooleanField(default=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="schedules", to="doctors.doctor")),
                ("specialty", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="clinics.specialty")),
            ],
            options={"verbose_name": "Agenda", "unique_together": {("doctor", "specialty")}},
        ),
        migrations.CreateModel(
            name="BlockedSlot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                ("reason", models.CharField(blank=True, max_length=100)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocked_slots", to="doctors.doctor")),
            ],
            options={"verbose_name": "Horário bloqueado"},
        ),
    ]
