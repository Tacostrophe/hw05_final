from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели корректно работает __str__."""
        model_str = {
            PostModelTest.post: (PostModelTest.post.text[:15] + '...'),
            PostModelTest.group: PostModelTest.group.title,
        }
        for model, expected_model_name in model_str.items():
            with self.subTest(model=model):
                self.assertEqual(expected_model_name, str(model))
