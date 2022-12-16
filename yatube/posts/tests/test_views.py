from django.test import Client, TestCase
from django import forms
from django.urls import reverse
from ..models import Group, Post, User

POSTSNUM_PAGE1 = 10
POSTSNUM_PAGE2_1 = 3
POSTSNUM_PAGE_EMT = 0


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

    def post_test(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.group)

    def test_home_page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        last_post = response.context['page_obj'][-1]
        self.post_test(last_post)

    def test_group_list_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        last_post = response.context['page_obj'][-1]
        self.post_test(last_post)

    def test_profile_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}))
        last_post = response.context['page_obj'][-1]
        self.post_test(last_post)

    def test_post_detail_pages_show_correct_context(self):
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        postcont = response.context.get('post')
        self.assertEqual(postcont.text, self.post.text)
        self.assertEqual(postcont.author, self.post.author)

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
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('is_edit'), True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ALL_POSTS = 13
        cls.user = User.objects.create_user(username='autha')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        many_posts = []
        for _ in range(ALL_POSTS):
            many_posts.append(Post(
                author=cls.user,
                text='test post',
                group=cls.group
            ))
        Post.objects.bulk_create(many_posts)

    def setUp(self):
        # Создаем авторизованный клиент
        self.guest_client = Client()
        self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)

    def test_index_pag(self):
        response = self.guest_client.get(reverse('posts:index'))
        post = response.context['page_obj']
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(post), POSTSNUM_PAGE1)

    def test_index_pag2(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE2_1)

    def test_group_list_pag(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
        # Проверка: количество постов на первой странице равно 10.
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE1)

    def test_group_list_pag2(self):
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2')
        post = response.context['page_obj']
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(post), POSTSNUM_PAGE2_1)

    def test_profile_pag(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username}))
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE1)

    def test_profile_pag2(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username': self.user.username}) + '?page=2')
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE2_1)


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
        post = response.context['page_obj']
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(post[-1], self.post)

    def test_group_list_post(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        # Проверка: количество постов на первой странице равно 10.
        post = response.context['page_obj']
        self.assertEqual(post[-1], self.post)

    def test_wr_group_list_post(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group2.slug}))
        # Проверка: количество постов на первой странице равно 10.
        post = response.context['page_obj']
        self.assertEqual(len(post), POSTSNUM_PAGE_EMT)

    def test_profile_page_post(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={
                'username':
                    self.post.author.username}))
        # Проверка: количество постов на первой странице равно 10.
        post = response.context['page_obj']
        self.assertEqual(post[-1], self.post)
