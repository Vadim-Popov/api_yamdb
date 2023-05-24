"""Модуль содержит настройки админки для приложения Users."""

from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """Класс для кастомизации отображения модели пользователя в админке."""

    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'bio'
    )


admin.site.register(User, UserAdmin)
