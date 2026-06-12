from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("accounts", "0002_add_cpf_hash")]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE accounts_user ALTER COLUMN phone SET DEFAULT '';",
                "ALTER TABLE accounts_user ALTER COLUMN failed_login_attempts SET DEFAULT 0;",
                "ALTER TABLE accounts_user ALTER COLUMN lgpd_consent_version SET DEFAULT '';",
                "ALTER TABLE accounts_user ALTER COLUMN created_at SET DEFAULT NOW();",
                "ALTER TABLE accounts_user ALTER COLUMN updated_at SET DEFAULT NOW();",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
