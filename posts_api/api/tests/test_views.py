import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from posts.models import Follow, Post

from ..serializers import FollowSerializers, PostSerializers

User = get_user_model()


class PostsViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='First_user')
        cls.first_post = Post.objects.create(
            title='first title',
            text='first text',
            author=cls.first_user
        )
        cls.urls = {
            'posts-list': reverse('posts-list'),
            'users-list': reverse('users-list'),
            'follow-list': reverse('follow-list'),
            'follow-post-list': reverse('follow-posts-list'),
            'posts-detail': reverse(
                'posts-detail', kwargs={'pk': cls.first_post.pk}
            ),
            'users-detail': reverse(
                'users-detail', kwargs={'pk': cls.first_user.pk}
            ),
        }
        cls.json_body = {
            'title': 'new title',
            'text': 'new text'
        }

    def setUp(self):
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=PostsViewTests.first_user)

    def test_posts_list_get_return_valid_data(self):
        """GET запрос к posts-list возвращает правильные данные."""
        response = self.auth_client.get(
            PostsViewTests.urls['posts-list']
        )
        posts = Post.objects.all()
        serializer = PostSerializers(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_posts_list_post_return_valid_data(self):
        """POST запрос к posts-list возвращает правильные данные."""
        response = self.auth_client.post(
            PostsViewTests.urls['posts-list'],
            PostsViewTests.json_body,
            format='json'
        )
        post = Post.objects.latest('pub_date')
        serializer = PostSerializers(post)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_posts_detail_get_return_valid_data(self):
        """GET запрос к posts-detail возвращает правильные данные."""
        response = self.auth_client.get(
            PostsViewTests.urls['posts-detail']
        )
        posts = Post.objects.get(pk=PostsViewTests.first_post.pk)
        serializer = PostSerializers(posts)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_posts_detail_put_and_patch_return_valid_data(self):
        """PUT и PATCH запрос к posts-detail возвращает правильные данные."""
        response = self.auth_client.put(
            PostsViewTests.urls['posts-detail'],
            PostsViewTests.json_body,
            format='json'
        )
        post = Post.objects.get(pk=PostsViewTests.first_post.pk)
        serializer = PostSerializers(post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        second_response = self.auth_client.patch(
            PostsViewTests.urls['posts-detail'],
            {'title': 'another title'},
            format='json'
        )
        post = Post.objects.get(pk=PostsViewTests.first_post.pk)
        serializer = PostSerializers(post)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data, serializer.data)

    def test_posts_detail_delete_return_valid_data(self):
        """DELETE запрос к posts-detail удаляет запись, возвращает статус."""
        post_id = PostsViewTests.first_post.pk
        response = self.auth_client.delete(
            PostsViewTests.urls['posts-detail']
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Post.objects.filter(pk=post_id).exists()
        )


class FollowViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='First_user')
        cls.second_user = User.objects.create_user(username='Second_user')
        cls.first_post = Post.objects.create(
            title='first title',
            text='first text',
            author=cls.first_user
        )
        cls.second_post = Post.objects.create(
            title='second title',
            text='second text',
            author=cls.second_user
        )
        cls.urls = {
            'follow-list': reverse('follow-list'),
            'follow-posts-list': reverse('follow-posts-list'),
        }
        cls.json_body = {
            'following': FollowViewTests.second_user.username
        }

    def setUp(self):
        self.first_auth_client = APIClient()
        self.first_auth_client.force_authenticate(
            user=FollowViewTests.first_user
        )
        self.second_auth_client = APIClient()
        self.second_auth_client.force_authenticate(
            user=FollowViewTests.second_user
        )

    def test_follow_list_get_return_valid_data(self):
        """GET запрос к follow-list возвращает правильные данные."""
        Follow.objects.create(
            user=FollowViewTests.first_user,
            following=FollowViewTests.second_user
        )
        response = self.first_auth_client.get(
            FollowViewTests.urls['follow-list']
        )
        follow = FollowViewTests.first_user.follower
        serializer = FollowSerializers(follow, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_follow_list_post_create_valid_data(self):
        """POST запрос к follow-list создает подписку."""
        response = self.first_auth_client.post(
            FollowViewTests.urls['follow-list'],
            FollowViewTests.json_body,
            format='json'
        )
        follow = Follow.objects.filter(
            user=FollowViewTests.first_user,
            following=FollowViewTests.second_user
        ).exists()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(follow)

    def test_self_following_is_not_possible(self):
        """Самоподписка невозможна."""
        response = self.first_auth_client.post(
            FollowViewTests.urls['follow-list'],
            {'following': FollowViewTests.first_user.username},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = {
            "non_field_errors": [ErrorDetail(
                string='Подписка на себя невозможна!', code='invalid'
            )]
        }
        self.assertEqual(response.data, error)

    def test_follow_posts_list_get_return_valid_data(self):
        """GET запрос к follow-posts-list возвращает правильные данные."""
        Follow.objects.create(
            user=FollowViewTests.first_user,
            following=FollowViewTests.second_user
        )

        # Запрос нужен для установки read_status = True
        self.first_auth_client.get(
            reverse(
                'posts-detail', kwargs={'pk': FollowViewTests.second_post.pk}
            )
        )

        response = self.first_auth_client.get(
            FollowViewTests.urls['follow-posts-list']
        )
        posts = Post.objects.filter(
            author__following__user=FollowViewTests.first_user
        )
        serializer = PostSerializers(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class UsersViewTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='First_user')
        cls.post = Post.objects.create(
            title='test title',
            text='test text',
            author=cls.user
        )
        cls.urls = {
            'users-list': reverse('users-list'),
            'users-detail': reverse(
                'users-detail', kwargs={'pk': UsersViewTests.user.pk}
            ),
        }

    def setUp(self):
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=UsersViewTests.user)

    def test_users_list_get_return_valid_data(self):
        """GET запрос к users-list возвращает правильные данные."""
        response = self.auth_client.get(
            UsersViewTests.urls['users-list']
        )
        json_response = json.dumps(response.data)
        json_data = json.dumps([{
            'id': UsersViewTests.user.pk,
            'username': UsersViewTests.user.username,
            'posts_count': UsersViewTests.user.posts.count()
        }])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response, json_data)

    def test_users_detail_get_return_valid_data(self):
        """GET запрос к users-detail возвращает правильные данные."""
        response = self.auth_client.get(
            UsersViewTests.urls['users-detail']
        )
        json_response = json.dumps(response.data)
        json_data = json.dumps({
            'id': UsersViewTests.user.pk,
            'username': UsersViewTests.user.username,
            'posts_count': UsersViewTests.user.posts.count()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response, json_data)
