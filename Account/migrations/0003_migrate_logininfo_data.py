"""
Data migration: Migrate LoginInfo data from ELW to Account module.

This migration copies data from ELW.LoginInfo to Account.LoginInfo.
After this migration, ELW.LoginInfo can be safely removed.
"""
from django.db import migrations


def migrate_logininfo_data(apps, schema_editor):
    """Migrate LoginInfo data from ELW to Account"""
    # Get old and new models
    try:
        ELWLoginInfo = apps.get_model('ELW', 'LoginInfo')
        AccountLoginInfo = apps.get_model('Account', 'LoginInfo')
        
        # Copy all data
        for old_record in ELWLoginInfo.objects.all():
            AccountLoginInfo.objects.create(
                username=old_record.username,
                week=old_record.week,
                action=old_record.action,
                action_time=old_record.action_time,
                last_active_time=old_record.last_active_time,
                device_info=old_record.device_info,
            )
        print(f"Migrated {ELWLoginInfo.objects.count()} LoginInfo records from ELW to Account")
    except LookupError:
        # ELW.LoginInfo doesn't exist yet (fresh install), skip migration
        print("ELW.LoginInfo not found, skipping data migration")


def reverse_migrate_logininfo_data(apps, schema_editor):
    """Reverse migration: Copy data back from Account to ELW"""
    try:
        ELWLoginInfo = apps.get_model('ELW', 'LoginInfo')
        AccountLoginInfo = apps.get_model('Account', 'LoginInfo')
        
        # Copy all data back
        for new_record in AccountLoginInfo.objects.all():
            ELWLoginInfo.objects.create(
                username=new_record.username,
                week=new_record.week,
                action=new_record.action,
                action_time=new_record.action_time,
                last_active_time=new_record.last_active_time,
                device_info=new_record.device_info,
            )
    except LookupError:
        # ELW.LoginInfo doesn't exist, skip reverse migration
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0002_logininfo'),
        ('ELW', '0001_initial'),  # Ensure ELW migrations are applied
    ]

    operations = [
        migrations.RunPython(migrate_logininfo_data, reverse_migrate_logininfo_data),
    ]

