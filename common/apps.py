"""
Django app configuration for common module.
"""
from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuration for common app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
    verbose_name = 'Common Services'

