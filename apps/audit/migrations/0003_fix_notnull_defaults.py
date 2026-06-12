from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("audit", "0002_add_timestamp")]
    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE audit_auditlog ALTER COLUMN user_cpf_snapshot SET DEFAULT '';",
                "ALTER TABLE audit_auditlog ALTER COLUMN user_agent SET DEFAULT '';",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
