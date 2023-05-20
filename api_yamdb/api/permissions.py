"""Модуль содержит классы для определения прав доступа."""

from rest_framework import permissions


class IsAdminOrStaff(permissions.BasePermission):
    """
    Класс прав доступа.

    Доступ только администраторам и сотрудникам.
    """

    def has_permission(self, request, view):
        """Проверяет, имеет ли пользователь необходимые права."""
        return (
            request.user.is_staff
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Класс прав доступа.

    Разрешает чтение всем пользователям а создание, обновление и
    удаление - только администраторам.
    """

    def has_permission(self, request, view):
        """Проверяет, имеет ли пользователь необходимые права."""
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """
    Класс прав доступа.

    Разрешает чтение всем пользователям, а создание, обновление и удаление
    разрешены автору, модератору или администратору.
    """

    def has_permission(self, request, view):
        """Проверяет, имеет ли пользователь необходимые права."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Проверяет, есть ли у пользователя права для конкретного объекта."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
