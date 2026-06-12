import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="auditlog",
            name="timestamp",
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
    ]
