from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("audit", "0003_fix_notnull_defaults")]
    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE audit_auditlog ALTER COLUMN created_at SET DEFAULT NOW();",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
