"""Модуль сериалайзеров."""
from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from api.permissions import IsAdminOrStaff
from api_yamdb.settings import LEN_USERNAME, LEN_CONFIRMATION_CODE, MIN_YEAR
from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User

USERNAME_CHECK = r'^[\w.@+-]+$'  # Проверка имени на отсутствие спецсимволов


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        """Мета класс."""

        model = User
        fields = ('email', 'username')


class AuthTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена авторизации."""

    username = serializers.RegexField(
        regex=USERNAME_CHECK,
        max_length=LEN_USERNAME,
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True,
        max_length=LEN_CONFIRMATION_CODE,
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с правами администратора или персонала."""

    permission_classes = (IsAdminOrStaff,)

    class Meta:
        """Мета класс."""

        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        """Мета класс."""

        model = Category
        fields = ['name', 'slug']


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        """Мета класс."""

        model = Genre
        fields = ['name', 'slug']


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов на произведения."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    def validate_score(self, value):
        """Проверка значения оценки на соответствие."""
        if not settings.MIN_SCORE_VALUE <= value <= settings.MAX_SCORE_VALUE:
            raise serializers.ValidationError(
                f'Оценка должна быть от {settings.MIN_SCORE_VALUE}'
                f'до {settings.MAX_SCORE_VALUE}!',
            )
        return value

    def validate(self, data):
        """Проверка наличия только одного отзыва для каждого произведения."""
        author = self.context['request'].user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if self.instance is None and \
                Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                'Может существовать только один отзыв!',
            )
        return data

    class Meta:
        """Мета класс."""

        fields = '__all__'
        read_only_fields = ['title']
        model = Review
        read_only_fields = ['title']


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        """Мета класс."""

        model = Comments
        fields = '__all__'
        read_only_fields = ('pub_date', 'review')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all())
    year = serializers.IntegerField(
        validators=[MinValueValidator(MIN_YEAR),
                    MaxValueValidator(datetime.now().year)])

    class Meta:
        """Мета класс."""

        model = Title
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений с детальной информацией."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        """Мета класс."""

        model = Title
        fields = '__all__'
