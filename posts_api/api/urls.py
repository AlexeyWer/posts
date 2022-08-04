from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FollowViewSet, MyFollowPostsViewSet, PostViewSet,
                    UserViewSet)

router = DefaultRouter()
router.register('posts', PostViewSet, basename='posts')
router.register('users', UserViewSet, basename='users')
router.register('follow', FollowViewSet, basename='follow')
router.register('follow/posts', MyFollowPostsViewSet, basename='follow-posts')


urlpatterns = [
    path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.jwt')),
    path('v1/', include(router.urls)),
]
