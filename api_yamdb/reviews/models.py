from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from user.models import User

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
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:15]
