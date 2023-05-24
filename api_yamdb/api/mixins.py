"""Модуль с миксинами приложения."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from api.permissions import IsAdminUserOrReadOnly


class CategoryGenreViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Миксин для категорий и жанров."""

    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'slug']
    search_fields = ['name', 'slug']
    lookup_field = 'slug'
