from ..forms import PostForm
from ..models import Group, Post, User
# from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
            id=1
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1234567',
            pk=1
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Task."""
        # Подсчитаем количество записей в Task
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username':
                    self.user.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.exclude(pk=1).filter(
                text=form_data['text'],
                author=self.user,
                group=form_data['group']
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertEqual(Post.objects.exclude(pk=1)[0].id, 2)
        self.assertEqual(
            Post.objects.exclude(pk=1)[0].text, form_data['text']),
        self.assertEqual(
            Post.objects.exclude(pk=1)[0].group.id,
            form_data['group'])

    def test_edit_post(self):
        post = Post.objects.all()[0]
        """Валидная форма создает запись в Task."""
        # Подсчитаем количество записей в Task
        form_data = {
            'text': 'Тестовый тексто',
            'group': self.group.id
        }
        # Отправляем POST-запрос
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': post.id}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что создалась запись с заданным слагом
        self.assertEqual(Post.objects.all()[0].id, post.id)
        self.assertEqual(Post.objects.all()[0].text, form_data['text']),
        self.assertEqual(Post.objects.all()[0].group.id, form_data['group'])
