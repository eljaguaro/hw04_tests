from django.test import TestCase, Client
from ..models import Post, Group, User


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
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
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
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
        self.assertEqual(response.status_code, 404)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_added_url_exists_at_desired_location(self):
        """Страница /create/ перенаправляет анонимного пользователю."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_post_added_url_exists_at_desired_location_auth(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_groups__url_exists_at_desired_location_authorized(self):
        """Страница /group/test-slug/ доступна любому
        пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post/1/edit перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_redirect_anonymous_authzed(self):
        """Страница /post/1/edit доступна авторизованному пользователю.
        """
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

    def group_url_test(self):
        """Страница группы доступна любому пользователю."""
        response = self.guest_client.get('group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def profile_url_test(self):
        """Страница профиля доступна любому пользователю."""
        response = self.guest_client.get('profile/david/')
        self.assertEqual(response.status_code, 200)

    def posts_url_test(self):
        """Страница поста доступна любому пользователю."""
        response = self.guest_client.get('posts/1/')
        self.assertEqual(response.status_code, 200)
