"""Модуль контроллеров приложения."""

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.filters import SearchFilter


from api.permissions import (IsAdminModeratorAuthorOrReadOnly,
                             IsAdminUserOrReadOnly)
from api.serializers import (CategorySerializer,
                             GenreSerializer,
                             UserSerializer, TitleSerializer,
                             TitleGetSerializer)
from api.utils import send_confirmation_code_to_email
from reviews.models import Category, Genre, Title
from users.models import User

from .serializers import (CommentsSerializer,
                          ReviewSerializer)

from reviews.models import Review
from .filters import TitleFilter
from api.permissions import IsAdminOrStaff
from api.utils import send_confirmation_code_to_email
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated, )
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from users.models import User

from .serializers import (
    UserSerializer,
    GetTokenSerializer,
    UsersMeSerializer,
    SignupSerializer,
)


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
    permission_classes = (AllowAny,)

    def post(self, request):
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
    serializer_class = GetTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request):
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
