"""Модуль контроллеров приложения."""

from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.filters import SearchFilter


from api.permissions import (IsAdminModeratorAuthorOrReadOnly, IsAdminOrStaff,
                             IsAdminUserOrReadOnly)
from api.serializers import (AuthTokenSerializer, CategorySerializer,
                             GenreSerializer, SignUpSerializer,
                             UserSerializer, TitleSerializer,
                             TitleGetSerializer)
from api.utils import send_confirmation_code_to_email
from reviews.models import Category, Genre, Title
from users.models import User
from users.token import get_tokens_for_user

from .serializers import (CommentsSerializer,
                          ReviewSerializer)

from reviews.models import Review
from .filters import TitleFilter


@api_view(('POST',))
@permission_classes((AllowAny,))
def signup(request):
    """Регистрация нового пользователя."""
    username = request.data.get('username')
    if User.objects.filter(username=username).exists():
        user = get_object_or_404(User, username=username)
        serializer = SignUpSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['email'] != user.email:
            return Response(
                'Почта указана неверно!', status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(raise_exception=True)
        send_confirmation_code_to_email(username)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if serializer.validated_data['username'] != settings.NOT_ALLOWED_USERNAME:
        serializer.save()
        send_confirmation_code_to_email(username)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(
        (
            f'Использование имени пользователя '
            f'{settings.NOT_ALLOWED_USERNAME} запрещено!'
        ),
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(('POST',))
@permission_classes((AllowAny,))
def get_token(request):
    """Получение токена при авторизации."""
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    confirmation_code = serializer.data.get('confirmation_code')
    if confirmation_code == str(user.confirmation_code):
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrStaff,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete',)

    @action(
        methods=('get', 'patch',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Получение, изменение и сохранение данных пользователя."""
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'slug']
    search_fields = ['name', 'slug']
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'slug']
    search_fields = ['name', 'slug']
    lookup_field = 'slug'


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

    queryset = Title.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Возвращает сериализатор под текущий метода запроса."""
        if self.request.method in ['POST', 'PATCH']:
            return TitleSerializer
        return TitleGetSerializer
