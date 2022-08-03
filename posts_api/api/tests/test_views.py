from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from posts.models import Post, Follow

from ..serializers import PostSerializers

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
            'users-list':reverse('users-list'),
            'follow-list': reverse('follow-list'),
            'follow-post-list':reverse('follow-posts-list'),
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
        """DELETE запрос к posts-detail возвращает правильные данные."""
        post_id = PostsViewTests.first_post.pk
        response = self.auth_client.delete(
            PostsViewTests.urls['posts-detail']
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Post.objects.filter(pk=post_id).exists()
        )