from django.test import TestCase, Client
from ..models import Post, Group, User
from http import HTTPStatus


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """ Создадим запись в БД для проверки доступности task/test-slug/ """
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='dТестовый текст',
        )
        cls.user = User.objects.create(
            username='david'
        )
        cls.post = Post.objects.create(
            text='teefwfweest-slug',
            author=cls.user,
        )

    def setUp(self):
        """ Создаем неавторизованный клиент """
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/david/': 'posts/profile.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        """Страница /task/test-slug/ перенаправляет анонимного
        пользователя.
        """
        response = self.guest_client.get('/dwdwew/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_adresses(self):
        """URL-адрес использует соответствующий шаблон."""
        guest_adresses = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/david/': HTTPStatus.OK,
            '/posts/1/edit/': HTTPStatus.FOUND,
            '/posts/1/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND
        }
        authzed_adresses = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/david/': HTTPStatus.OK,
            '/posts/1/edit/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for address, status in guest_adresses.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

        for address, status in authzed_adresses.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)
