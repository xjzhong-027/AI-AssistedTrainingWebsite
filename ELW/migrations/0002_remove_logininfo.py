"""
Migration to remove LoginInfo model from ELW app.

LoginInfo has been migrated to Account app.
Data migration was handled in Account/migrations/0003_migrate_logininfo_data.py
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ELW', '0001_initial'),
        ('Account', '0003_migrate_logininfo_data'),  # Ensure data is migrated first
    ]

    operations = [
        migrations.DeleteModel(
            name='LoginInfo',
        ),
    ]

