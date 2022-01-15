from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Test comment'
        )
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.user,
        )

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели корректно работает __str__."""
        model_str = {
            PostModelTest.post: (PostModelTest.post.text[:15] + '...'),
            PostModelTest.group: PostModelTest.group.title,
            PostModelTest.comment: (PostModelTest.comment.text[:15] + '...'),
            PostModelTest.follow: (
                PostModelTest.follower.username + '->'
                + PostModelTest.user.username
            ),
        }
        for model, expected_model_name in model_str.items():
            with self.subTest(model=model):
                self.assertEqual(expected_model_name, str(model))
