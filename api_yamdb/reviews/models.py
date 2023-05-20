"""Модуль с моделями приложения."""

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField('Название произведения', max_length=256)
    year = models.PositiveSmallIntegerField('Год произведения', db_index=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='titles')
    genre = models.ManyToManyField('Genre', blank=True, related_name='titles')
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        """Мета класс."""

        ordering = ['name']

    def __str__(self):
        """Метод возвращает имя объекта."""
        return self.name


class Review(models.Model):
    """Модель отзывы на произведения."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
        help_text='Пользователь, который оставил отзыв',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Выберите произведение, к которому хотите оставить отзыв',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(settings.MIN_SCORE_VALUE,
                              message='Оценка меньше допустимой',),
            MaxValueValidator(settings.MAX_SCORE_VALUE,
                              message='Оценка больше допустимой',),
        ),
        verbose_name='Оценка произведения',
        help_text='Укажите оценку произведения',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации отзыва, проставляется автоматически.',
    )

    class Meta:
        """Мета класс."""

        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review',
            ),
        )

    def __str__(self) -> str:
        """Метод возвращает 15 символов отзыва."""
        return self.text[:15]


class Comments(models.Model):
    """Модель комментария."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Пользователь, который оставил комментарий',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        help_text='Отзыв, к которому оставляют комментарий',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст комментария, который пишет пользователь',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
        help_text='Дата публикации проставляется автоматически',
    )

    class Meta:
        """Мета класс."""

        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        """Метод возвращает 15 символов комментария."""
        return self.text[:15]


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Слаг категории', max_length=50, unique=True)

    class Meta:
        """Мета класс."""

        ordering = ['name']

    def __str__(self):
        """Метод возвращает слаг объекта."""
        return self.slug


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField('Жанр', max_length=256)
    slug = models.SlugField('Слаг', max_length=50, unique=True)

    class Meta:
        """Мета класс."""

        ordering = ['name']

    def __str__(self):
        """Метод возвращает слаг объекта."""
        return self.slug


class GenreTitle(models.Model):
    """Модель связи между жанрами и произведениями."""

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        """Возвращает принадлежность произведения к жанру."""
        return f'{self.title} соответсвует жанру {self.genre}'
