"""Модуль контроллеров приложения."""

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .mixins import CategoryGenreViewSet
from .permissions import (IsAdminModeratorAuthorOrReadOnly, IsAdminOrStaff,
                          IsAdminUserOrReadOnly)
from .serializers import (CategorySerializer, CommentsSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, TitleSerializer,
                          TitleGetSerializer, SignupSerializer,
                          UserSerializer, UsersMeSerializer)
from .utils import send_confirmation_code_to_email


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'path',
                         'delete', 'patch')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = [IsAuthenticated, IsAdminOrStaff, ]

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        """Отображает/обновляет данные текущего пользователя."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = UsersMeSerializer(request.user,
                                           data=request.data,
                                           partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
    """Контроллер для регистрации пользователей."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Создает нового/обновляет пользователя."""
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            user = get_object_or_404(User, username=username)
            serializer = SignupSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['email'] != user.email:
                return Response(
                    'Почта указана неверно!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(raise_exception=True)
            send_confirmation_code_to_email(request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(
                email=serializer.validated_data['email']
        ).exists():
            return Response(
                'Пользователь с таким адресом электронной '
                'почты уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.validated_data['username'] != 'admin':
            serializer.save()
            send_confirmation_code_to_email(request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            (
                'Использование имени пользователя '
                'admin запрещено!'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )


class GetTokenView(TokenObtainPairView):
    """Контроллер для получения токенов."""

    serializer_class = GetTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """Получает токен для указанного пользователя."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            return Response(
                'Неверный код доступа',
                status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response(str(token), status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )

    def title_get_or_404(self):
        """Получение объекта Title или 404."""
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получение queryset объектов Review или 404."""
        title = self.title_get_or_404()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Сохраняет новый объект Review."""
        title = self.title_get_or_404()
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user, title=title)
        return Response(status=status.HTTP_201_CREATED)


class CommentsViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Comments."""

    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly,)

    def review_get_or_404(self):
        """Получение объекта Review или 404."""
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )

    def perform_create(self, serializer):
        """Сохраняет новый объект Comment."""
        review = self.review_get_or_404()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        """Получение объекта Comment или 404."""
        review = self.review_get_or_404()
        return review.comments.all()


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Title."""

    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    serializer_class = TitleGetSerializer

    def get_serializer_class(self):
        """Возвращает сериализатор под текущий метод запроса."""
        if self.request.method in ['POST', 'PATCH']:
            return TitleSerializer
        return self.serializer_class

    def get_queryset(self):
        """Возвращает queryset с добавлением поля rating."""
        queryset = Title.objects.all()
        if self.action in ['list', 'retrieve']:
            queryset = Title.objects.annotate(rating=Avg('reviews__score'))
        return queryset
