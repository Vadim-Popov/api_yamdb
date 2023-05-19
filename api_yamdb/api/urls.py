from rest_framework.routers import DefaultRouter
from django.urls import include, path
from api.views import signup, get_token, UsersViewSet, CategoryViewSet, GenreViewSet
from .views import ReviewViewSet
from .views import CommentsViewSet

router_v1 = DefaultRouter()

router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='titles_reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='reviews_comments'
)

urlpatterns = [
    path('v1/auth/signup/', signup, name='user_registration'),
    path('v1/auth/token/', get_token, name='user_get_token'),
    path('v1/', include(router_v1.urls)),
]
