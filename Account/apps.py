from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'Account'
    verbose_name = '账户管理'

    def ready(self):
        import Account.signals  # 导入 signals.py