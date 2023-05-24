"""Модуль с моделями приложения."""

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField('Название произведения',
                            max_length=settings.LEN_NAME)
    year = models.PositiveSmallIntegerField('Год произведения', db_index=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='titles')
    genre = models.ManyToManyField('Genre', blank=True, related_name='titles')
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        """Мета класс."""

        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        """Метод возвращает имя объекта."""
        return self.name


class BaseReview(models.Model):
    """Абстрактный базовый класс для отзывов и комментариев."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор',
        help_text='Пользователь, который оставил отзыв/комментарий',
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст отзыва/комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации, проставляется автоматически',
    )

    class Meta:
        """Мета класс."""

        abstract = True


class Review(BaseReview):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        help_text='Выберите произведение, к которому хотите оставить отзыв',
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(settings.MIN_SCORE_VALUE,
                              message='Оценка меньше допустимой'),
            MaxValueValidator(settings.MAX_SCORE_VALUE,
                              message='Оценка больше допустимой'),
        ),
        verbose_name='Оценка произведения',
        help_text='Укажите оценку произведения',
    )

    class Meta:
        """Мета класс."""

        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'],
                                    name='unique_review'),
        ]

    def __str__(self) -> str:
        """Метод возвращает 15 символов отзыва."""
        return self.text[:settings.LEN_TEXT]


class Comments(BaseReview):
    """Модель комментария."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        help_text='Отзыв, к которому оставляют комментарий',
    )

    class Meta:
        """Мета класс."""

        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self) -> str:
        """Метод возвращает 15 символов комментария."""
        return self.text[:settings.LEN_TEXT]


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField('Название категории',
                            max_length=settings.LEN_NAME)
    slug = models.SlugField('Слаг категории',
                            max_length=settings.LEN_SLUG, unique=True)

    class Meta:
        """Мета класс."""

        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Метод возвращает слаг объекта."""
        return self.slug


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField('Жанр', max_length=settings.LEN_NAME)
    slug = models.SlugField('Слаг', max_length=settings.LEN_SLUG, unique=True)

    class Meta:
        """Мета класс."""

        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        """Метод возвращает слаг объекта."""
        return self.slug


class GenreTitle(models.Model):
    """Модель связи между жанрами и произведениями."""

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        """Мета класс."""

        verbose_name = 'Жанр-Произведение'

    def __str__(self):
        """Возвращает принадлежность произведения к жанру."""
        return f'{self.title} соответсвует жанру {self.genre}'
