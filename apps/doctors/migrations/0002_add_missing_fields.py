from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("doctors", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="doctor", name="status",
            field=models.CharField(
                max_length=20,
                choices=[("available","Disponivel"),("in_consult","Em consulta"),("unavailable","Indisponivel"),("offline","Offline")],
                default="offline",
            ),
        ),
        migrations.AddField(
            model_name="doctor", name="bio",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="doctor", name="photo",
            field=models.ImageField(upload_to="doctor_photos/", null=True, blank=True),
        ),
    ]
