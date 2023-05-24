"""Модуль с моделями приложения."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


USER_TYPE_CHOICES = (
    ('user', 'user'),
    ('admin', 'admin'),
    ('moderator', 'moderator')
)


class User(AbstractUser):
    """Расширенная модель пользователя."""

    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=settings.LENGTH_EMAIL,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(choice[0]) for choice in USER_TYPE_CHOICES),
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_CHOICES[0][0]
    )
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
        verbose_name='Код доступа',
    )

    class Meta:
        """Мета класс."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    # чтобы мы могли обращаться к методам, как к атрибутам
    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором.."""
        return (
            self.role == USER_TYPE_CHOICES[1][0]
            or (self.is_staff and self.is_superuser)
        )

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return (
            self.role == USER_TYPE_CHOICES[2][0]
            or self.is_staff
            or self.is_admin
        )
