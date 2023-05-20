"""Модуль админки приложения reviews."""

from django.contrib import admin

from reviews.models import Comments, Review


class ReviewAdmin(admin.ModelAdmin):
    """Конфигурация модели Review для отображения в админке."""

    list_display = ('pk', 'author', 'text', 'pub_date')
    search_fields = ('author', 'text')
    list_filter = ('author', 'pub_date')
    empty_value_diplay = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Конфигурация модели Comments для отображения в админке."""

    list_display = ('pk', 'author', 'review', 'text', 'pub_date')
    search_fields = ('author', 'review')
    list_filter = ('author', 'review', 'pub_date')
    empty_value_display = '-пусто-'


admin.site.register(Comments, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
