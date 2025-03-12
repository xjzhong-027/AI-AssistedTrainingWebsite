from django.apps import AppConfig


class LogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Log'
    verbose_name = '日志管理'

    def ready(self):
        # import Log.signals  # 导入 signals.py
        from .signals import register_signals
        register_signals()