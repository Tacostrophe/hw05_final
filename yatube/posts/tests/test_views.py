import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Comment, Follow, Post, Group, User
from yatube.settings import POSTS_PER_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        for i in range(2):
            Group.objects.create(
                title=f'Test group{i+1}',
                slug=f'test-slug{i+1}',
                description=f'Test description{i+1}',
            )
        for j in range(23):
            Post.objects.create(
                author=cls.user,
                group=Group.objects.get(pk=(j % 2 + 1)),
                text=f'Test text{j+1}',
            )
        cls.test_comment = Comment.objects.create(
            author=cls.user,
            post=Post.objects.get(id=1),
            text='Test comment'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='not_auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(PostsPagesTests.user)

    def test_pages_use_correct_templates(self):
        '''URL-адреса используют корректные шаблоны'''
        templates_reverses = {
            'posts/index.html': (
                reverse('posts:posts_main'),
            ),
            'posts/group_list.html': (
                reverse('posts:posts_group',
                        kwargs={'slug': 'test-slug1'}),
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': str(Post.objects.get(pk=1).author.username)
                }),
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': str(Post.objects.get(pk=1).id)}),
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit',
                        kwargs={'post_id': str(Post.objects.get(pk=1).id)}),
                reverse('posts:post_create'),
            ),
        }
        for template, reverses in templates_reverses.items():
            for reverse_page in reverses:
                with self.subTest(page=reverse_page):
                    response = self.author.get(reverse_page)
                    self.assertTemplateUsed(response, template)

    def test_posts_main_page_show_correct_context(self):
        '''Шаблон posts_main сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:posts_main'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, f'Test text{first_object.pk}')
        self.assertEqual(first_object.group.title,
                         f'Test group{first_object.group.pk}')
        self.assertEqual(first_object.group.slug,
                         f'test-slug{first_object.group.pk}')
        self.assertEqual(first_object.group.description,
                         f'Test description{first_object.group.pk}')

    def test_posts_group_page_show_correct_context(self):
        '''Шаблон posts_group сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse(
            'posts:posts_group', kwargs={'slug': 'test-slug1'}
        ))
        the_group = response.context['group']
        first_object = response.context['page_obj'][0]
        self.assertEqual(the_group.title,
                         f'Test group{the_group.pk}')
        self.assertEqual(the_group.slug,
                         f'test-slug{the_group.pk}')
        self.assertEqual(the_group.description,
                         f'Test description{the_group.pk}')
        self.assertEqual(first_object.text, f'Test text{first_object.pk}')

    def test_profile_page_show_correct_context(self):
        '''Шаблон profile сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}
        ))
        first_object = response.context['page_obj'][0]
        the_author = response.context['author']
        self.assertEqual(the_author, PostsPagesTests.user)
        self.assertEqual(first_object.text, f'Test text{first_object.pk}')
        self.assertEqual(first_object.group.title,
                         f'Test group{first_object.group.pk}')
        self.assertEqual(first_object.group.slug,
                         f'test-slug{first_object.group.pk}')
        self.assertEqual(first_object.group.description,
                         f'Test description{first_object.group.pk}')

    def test_post_detail_page_show_correct_context(self):
        '''Шаблон post_detail сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        the_post = response.context.get('post')
        self.assertEqual(the_post.text, f'Test text{the_post.pk}')
        self.assertEqual(the_post.group.title,
                         f'Test group{the_post.group.pk}')
        self.assertEqual(the_post.group.slug,
                         f'test-slug{the_post.group.pk}')
        self.assertEqual(the_post.group.description,
                         f'Test description{the_post.group.pk}')

    def test_post_edit_page_show_correct_context(self):
        '''Шаблон post_edit сформирован с правильным контекстом'''
        response = self.author.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        '''Шаблон post_create сформирован с правильным контекстом'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_main_first_page_contains_right_number_of_posts(self):
        '''Проверка количества постов на первой странице posts_main'''
        response = self.authorized_client.get(reverse('posts:posts_main'))
        if Post.objects.count() >= POSTS_PER_PAGE:
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
        else:
            self.assertEqual(len(response.context['page_obj']),
                             Post.objects.count() % POSTS_PER_PAGE)

    def test_posts_main_last_page_contains_right_number_of_posts(self):
        '''Проверка количества постов на последней странице posts_main'''
        response = self.authorized_client.get(
            reverse('posts:posts_main') + '?page='
            + str(Post.objects.count() // POSTS_PER_PAGE + 1)
        )
        self.assertEqual(len(response.context['page_obj']),
                         Post.objects.count() % POSTS_PER_PAGE)

    def test_posts_group_first_page_contains_right_number_of_posts(self):
        '''Проверка количества постов на первой странице posts_group'''
        group_posts = Post.objects.filter(group__slug='test-slug1')
        response = self.authorized_client.get(reverse(
            'posts:posts_group', kwargs={'slug': 'test-slug1'}
        ))
        if group_posts.count() >= POSTS_PER_PAGE:
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
        else:
            self.assertEqual(len(response.context['page_obj']),
                             group_posts.count() % POSTS_PER_PAGE)

    def test_posts_group_last_page_contains_right_number_of_posts(self):
        '''Проверка количества постов на последней странице posts_group'''
        group_posts = Post.objects.filter(group__slug='test-slug1')
        response = self.authorized_client.get(
            reverse('posts:posts_group', kwargs={'slug': 'test-slug1'})
            + '?page=' + str(group_posts.count() // POSTS_PER_PAGE + 1)
        )
        self.assertEqual(len(response.context['page_obj']),
                         group_posts.count() % POSTS_PER_PAGE)

    def test_profile_first_page_contains_right_number_of_posts(self):
        '''Проверка количества постов на первой странице profile'''
        profile_posts = Post.objects.filter(author__username='auth')
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}
        ))
        if profile_posts.count() >= POSTS_PER_PAGE:
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
        else:
            self.assertEqual(len(response.context['page_obj']),
                             profile_posts.count() % POSTS_PER_PAGE)

    def test_profile_last_page_contains_right_number_of_posts(self):
        '''Проверка количества постов на последней странице profile'''
        profile_posts = Post.objects.filter(author__username='auth')
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
            + '?page=' + str(profile_posts.count() // POSTS_PER_PAGE + 1)
        )
        self.assertEqual(len(response.context['page_obj']),
                         profile_posts.count() % POSTS_PER_PAGE)

    def test_post_correct_locations(self):
        '''Проверка, что пост с группой отображается
        на главной, странице своей группы и в профиле автора'''
        test_post = Post.objects.order_by('-pk')[0]
        reverses = (
            reverse('posts:posts_main'),
            reverse(
                'posts:posts_group', kwargs={'slug': test_post.group.slug}
            ),
            reverse(
                'posts:profile', kwargs={'username': test_post.author.username}
            )
        )
        for reverse_page in reverses:
            with self.subTest(reverse_page=reverse_page):
                response = self.guest_client.get(reverse_page)
                posts = response.context['page_obj']
                self.assertIn(test_post, posts)

    def test_no_post_in_another_group_page(self):
        '''Проверка, что пост не появляется на странице другой группы'''
        test_post = Post.objects.order_by('-pk')[0]
        another_group = Group.objects.exclude(id=test_post.group.id)[0]
        response = self.guest_client.get(reverse(
            'posts:posts_group', kwargs={'slug': another_group.slug}
        ))
        posts = response.context['page_obj']
        self.assertNotIn(test_post, posts)

    def test_post_pages_show_image_in_context(self):
        '''Посты с изображениями формируют корректный контекст для шаблонов'''
        pic_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        picture = SimpleUploadedFile(
            name='pic.gif',
            content=pic_gif,
            content_type='image/gif'
        )
        post_with_pic = Post.objects.create(
            author=PostsPagesTests.user,
            group=Group.objects.get(pk=1),
            text='Test text with pic',
            image=picture
        )
        reverses = (
            reverse('posts:posts_main'),
            reverse('posts:posts_group', kwargs={'slug': 'test-slug1'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        )
        for reverse_one in reverses:
            with self.subTest(resverse_one=reverse_one):
                response = self.authorized_client.get(reverse_one)
                the_post = response.context['page_obj'][0]
                self.assertEqual(the_post.image, 'posts/pic.gif')
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': post_with_pic.id}
        ))
        the_post = response.context.get('post')
        self.assertEqual(the_post.image, 'posts/pic.gif')

    def test_comment_is_visible(self):
        '''Проверка, что комментарий отображается'''
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        comments = response.context['comments']
        self.assertIn(self.test_comment, comments)


class PostsCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        Post.objects.create(
            author=cls.author,
            text='just a text',
        )
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.user_follower = User.objects.create_user(username='followfull')
        self.user_not_follower = User.objects.create_user(
            username='followless'
        )
        self.follower = Client()
        self.follower.force_login(self.user_follower)
        self.not_follower = Client()
        self.not_follower.force_login(self.user_not_follower)
        self.post = Post.objects.create(
            author=PostsCacheTests.author,
            text='another text',
        )

    def test_posts_main_cache(self):
        '''Проверка работы кэша на главной странице'''
        the_reverse = reverse('posts:posts_main')
        response = self.guest_client.get(the_reverse)
        self.assertContains(response, self.post.text)
        self.post.delete()
        response = self.guest_client.get(the_reverse)
        self.assertContains(response, self.post.text)
        cache.clear()
        response = self.guest_client.get(the_reverse)
        self.assertNotContains(response, self.post.text)

    def test_authorized_can_follow_unfollow(self):
        '''Авторизованный пользователь может подписываться и отписываться'''
        self.follower.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostsCacheTests.author.username}
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.user_follower
        ).filter(
            author=PostsCacheTests.author
        ).exists())
        self.follower.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostsCacheTests.author.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower
        ).filter(
            author=PostsCacheTests.author
        ).exists())

    def test_follower_see_new_post(self):
        '''Новый пост появляется в ленте только подписчиков'''
        Follow.objects.create(
            user=self.user_follower,
            author=PostsCacheTests.author,
        )
        new_post = Post.objects.create(
            author=PostsCacheTests.author,
            text='Following test text',
        )
        follower_response = self.follower.get(reverse('posts:follow_index'))
        not_follower_response = self.not_follower.get(reverse(
            'posts:follow_index'
        ))
        follower_posts = follower_response.context['page_obj']
        not_follower_posts = not_follower_response.context['page_obj']
        self.assertIn(new_post, follower_posts)
        self.assertNotIn(new_post, not_follower_posts)
