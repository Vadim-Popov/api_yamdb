"""Модуль сериалайзеров."""
from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from rest_framework.response import Response

from api.permissions import IsAdminOrStaff
from api_yamdb.settings import LEN_USERNAME, LEN_CONFIRMATION_CODE, MIN_YEAR
from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User


USERNAME_CHECK = r'^[\w.@+-]+$'  # Проверка имени на отсутствие спецсимволов


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""
   
    username = serializers.CharField(
        max_length=settings.LENGTH_USERNAME,
        validators=[
            RegexValidator(
                regex=USERNAME_CHECK,
                message="""Имя должно содержать,только
                буквы,
                цифры или же символ подчеркивания!"""),
            UniqueValidator(queryset=User.objects.all()),
        ],
    )

    class Meta:
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')
        model = User


class UsersMeSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=settings.LENGTH_USERNAME)
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username:
            raise serializers.ValidationError('Нет поля username')

        try:
            user = get_object_or_404(User, username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Пользователь с таким именем не найден')

        if user.username != username:
            return Response(
                {'detail': 'Неверный код доступа'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код доступа')

        return data


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    email = serializers.EmailField(max_length=settings.LENGTH_EMAIL)

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'me нельзя использовать в качестве имени',
            )
        return value


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
