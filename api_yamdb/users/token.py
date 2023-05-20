"""Модуль содержит функции для работы с токенами."""

from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Функция генерации токена для пользователя."""
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
    }
