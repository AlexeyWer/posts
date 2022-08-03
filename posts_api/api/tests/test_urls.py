from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from posts.models import Post, Follow

User = get_user_model()


class StaticURLTests(APITestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test')
        cls.post = Post.objects.create(
            title='test title',
            text='test text',
            author=cls.user
        )
        cls.urls_list = [
            reverse('posts-list'),
            reverse('users-list'),
            reverse('follow-list'),
            reverse('follow-posts-list'),
        ]
        cls.urls_detail = [
            reverse('posts-detail', kwargs={'pk': cls.post.pk}),
            reverse('users-detail', kwargs={'pk': cls.user.pk}),
        ]
    
    def setUp(self):
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=StaticURLTests.user)

    def test_urls_is_available_to_auth_user(self):
        """Общедоступные страницы доступны авторизованному пользователю."""
        urls = [
            *StaticURLTests.urls_list,
            *StaticURLTests.urls_detail
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)       