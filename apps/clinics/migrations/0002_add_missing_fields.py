from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("clinics", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="clinic", name="slug",
            field=models.SlugField(unique=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="clinic", name="primary_color",
            field=models.CharField(max_length=7, default="#0066cc"),
        ),
        migrations.AddField(
            model_name="clinic", name="max_patients",
            field=models.PositiveIntegerField(default=500),
        ),
        migrations.AddField(
            model_name="specialty", name="cbo_code",
            field=models.CharField(max_length=10, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cliniccapitoken", name="name",
            field=models.CharField(max_length=100, default="API Token"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cliniccapitoken", name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="cliniccapitoken", name="last_used",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
