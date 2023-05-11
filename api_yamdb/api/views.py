from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


from api.permissions import (IsAdminModeratorAuthorOrReadOnly, IsAdminOrStaff,
                             IsAdminUserOrReadOnly)
from api.serializers import (AuthTokenSerializer, SignUpSerializer,
                             UserSerializer)
from api.utils import send_confirmation_code_to_email
from users.models import User
from users.token import get_tokens_for_user


@api_view(('POST',))
@permission_classes((AllowAny,))
def signup(request):
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
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    confirmation_code = serializer.data.get('confirmation_code')
    if confirmation_code == str(user.confirmation_code):
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
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
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
