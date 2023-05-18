"""Модуль c моделями проекта."""

from django.db import models


class Category(models.Model):
    """Модель категорий."""
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Слаг категории', max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель жанра."""
    name = models.CharField('Жанр', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField('Название произведения', max_length=256)
    year = models.PositiveSmallIntegerField('Год произведения', db_index=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='titles')
    genre = models.ManyToManyField('Genre', blank=True, related_name='titles')
    description = models.TextField('Описание', null=True, blank=True)
 
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
