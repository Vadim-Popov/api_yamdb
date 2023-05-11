from rest_framework.routers import DefaultRouter
from django.urls import include, path
from api.views import signup, get_token, UsersViewSet


router = DefaultRouter()

router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/auth/signup/', signup, name='user_registration'),
    path('v1/auth/token/', get_token, name='user_get_token'),
    path('v1/', include(router.urls)),
]
