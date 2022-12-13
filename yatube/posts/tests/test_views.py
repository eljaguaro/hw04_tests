from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django import forms
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1234567',
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        # self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        expected = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        expected = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}))
        expected = list(Post.objects.all()[:10])
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_pages_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='autha')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for _ in range(13):
            Post.objects.create(
                author=cls.user,
                text='Test post',
                group=cls.group
            )
        # Post.objects.bulk_create(many_posts)

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)

    def test_index_pag(self):
        response = self.guest_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_pag2(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_pag(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_pag2(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2')
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_pag(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_pag2(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class DopTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='autha')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test post',
            group=cls.group
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)

    def test_index_post(self):
        response = self.guest_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(response.context['page_obj'][-1], self.post)

    def test_group_list_post(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(response.context['page_obj'][-1], self.post)

    def test_wr_group_list_post(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group2.slug}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_profile_page_post(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username':
                    self.post.author.username}))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(response.context['page_obj'][-1], self.post)
