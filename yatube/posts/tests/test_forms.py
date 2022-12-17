from ..forms import PostForm
from ..models import Group, Post, User
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
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username':
                    self.user.username}))
        post = Post.objects.exclude(pk=1).first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.exclude(pk=1).filter(
                text=form_data['text'],
                author=self.user,
                group=form_data['group']
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            post.text, form_data['text']),
        self.assertEqual(
            post.group.id,
            form_data['group'])

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый тексто',
            'group': self.group.id
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        post = Post.objects.all().first()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, form_data['text']),
        self.assertEqual(post.group.id, form_data['group'])
