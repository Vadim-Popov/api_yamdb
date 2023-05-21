"""Модуль сериалайзеров."""

from django.conf import settings
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category
from reviews.models import Comments
from reviews.models import Genre
from reviews.models import Review
from reviews.models import Title
from api.permissions import IsAdminOrStaff
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
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True,
        max_length=16,
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
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        """Вычисление среднего значения оценок для произведения."""
        return obj.reviews.aggregate(Avg('score', default=0)).get('score__avg')

    class Meta:
        """Мета класс."""

        model = Title
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений с детальной информацией."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        """Мета класс."""

        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        """Вычисление среднего значения оценок для произведения."""
        return obj.reviews.aggregate(Avg('score', default=0)).get('score__avg')
