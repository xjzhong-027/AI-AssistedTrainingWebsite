from django.apps import AppConfig


class BackupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Backup'
    verbose_name = '备份管理'