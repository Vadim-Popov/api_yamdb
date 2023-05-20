"""Модуль конфига приложения."""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфиг приложения Api."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
