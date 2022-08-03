from django.db.models import Count, Exists, OuterRef
from rest_framework import filters, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Post, User, ReadStatus

from .mixins import ListCreateViewSet, ListViewSet
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    FollowSerializers,
    PostSerializers,
    UserSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializers
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        post_read_status = ReadStatus.objects.filter(
            post=OuterRef('id'), user=self.request.user
        )
        queryset = Post.objects.annotate(
            read_status=Exists(post_read_status)
        )
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=self.kwargs.get('pk'))
        if not post.exists():
            raise NotFound(detail=f'Поста с номером {post} не существует')
        user = self.request.user
        record = ReadStatus.objects.filter(post=post[0], user=user)
        if not record.exists():
            ReadStatus.objects.create(post=post[0], user=user)
        return super().retrieve(request, *args, **kwargs)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.annotate(posts_count=Count('posts'))
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ('posts_count', )


class FollowViewSet(ListCreateViewSet):
    serializer_class = FollowSerializers
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('following__username',)

    def get_queryset(self):
        user = self.request.user
        return user.follower

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyFollowPostsViewSet(ListViewSet):
    serializer_class = PostSerializers
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        post_read_status = ReadStatus.objects.filter(
            post=OuterRef('id'), user=self.request.user
        )
        queryset = Post.objects.annotate(
            read_status=Exists(post_read_status)
        ).filter(
            author__following__user=self.request.user
        )
        return queryset
