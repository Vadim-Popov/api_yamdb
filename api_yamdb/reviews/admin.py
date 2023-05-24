"""Модуль админки приложения reviews."""

from django.contrib import admin

from reviews.models import Category, Genre, Title, Comments, Review


class CategoryAdmin(admin.ModelAdmin):
    """Административная панель категорий."""

    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_diplay = '-пусто-'


class GenreAdmin(admin.ModelAdmin):
    """Административная панель жанров."""

    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    empty_value_diplay = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    """Административная панель произведений."""

    list_display = ('pk', 'name', 'description', 'year', 'category')
    search_fields = ('name',)
    list_filter = ('year', 'category')
    empty_value_diplay = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    """Административная панель отзывов."""

    list_display = ('pk', 'author', 'text', 'pub_date')
    search_fields = ('author', 'text')
    list_filter = ('author', 'pub_date')
    empty_value_diplay = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Административная панель комментариев."""

    list_display = ('pk', 'author', 'review', 'text', 'pub_date')
    search_fields = ('author', 'review')
    list_filter = ('author', 'review', 'pub_date')
    empty_value_display = '-пусто-'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Comments, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
