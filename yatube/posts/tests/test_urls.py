from django.test import Client, TestCase
from http import HTTPStatus

from ..models import Post, Group, User


def setUpModule():
    global URL_MAIN_PAGE, URL_ABOUT_AUTHOR, URL_ABOUT_TECH
    global URL_GROUP, URL_PROFILE, URL_CREATE, URL_LOGIN, URL_FOLLOW_INDEX
    URL_MAIN_PAGE = '/'
    URL_ABOUT_AUTHOR = '/about/author/'
    URL_ABOUT_TECH = '/about/tech/'
    URL_GROUP = '/group/test-slug/'
    URL_PROFILE = '/profile/auth/'
    URL_CREATE = '/create/'
    URL_LOGIN = '/auth/login/'
    URL_FOLLOW_INDEX = '/follow/'


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages(self):
        '''Статические страницы доступны любому пользователю'''
        adresses = (URL_MAIN_PAGE, URL_ABOUT_AUTHOR, URL_ABOUT_TECH)
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='not_auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(PostsURLTests.user)
        self.post_id = PostsURLTests.post.id
        self.url_post = f'/posts/{self.post_id}/'
        self.url_post_edit = f'/posts/{self.post_id}/edit/'
        self.url_add_comment = f'/posts/{self.post_id}/comment/'
        self.url_follow = f'/profile/{self.user.username}/follow/'
        self.url_unfollow = f'/profile/{self.user.username}/unfollow/'

    def test_posts_url_anonymous(self):
        '''Cтраницы ведут себя так, как от них ждут'''
        adresses_statuses = {
            URL_GROUP: HTTPStatus.OK,
            URL_PROFILE: HTTPStatus.OK,
            self.url_post: HTTPStatus.OK,
            self.url_post_edit: HTTPStatus.FOUND,
            URL_CREATE: HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for adress, status in adresses_statuses.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status)

    def test_url_redirect_anonymous(self):
        '''Страницы перенаправляют неавторизованных пользователей'''
        adresses_redirects = {
            self.url_post_edit: URL_LOGIN + '?next=' + self.url_post_edit,
            URL_CREATE: URL_LOGIN + '?next=' + URL_CREATE,
            self.url_add_comment: URL_LOGIN + '?next=' + self.url_add_comment,
            URL_FOLLOW_INDEX: URL_LOGIN + '?next=' + URL_FOLLOW_INDEX,
            self.url_follow: URL_LOGIN + '?next=' + self.url_follow,
            self.url_unfollow: URL_LOGIN + '?next=' + self.url_unfollow,
        }
        for adress, redirect in adresses_redirects.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_create_url_exists_at_desired_location_authorized(self):
        '''Страница create доступна авторизованному пользователю'''
        response = self.authorized_client.get(URL_CREATE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_url_redirect_authorized_not_author(self):
        '''Страница posts/<int:post_id>/edit перенаправляет не автора'''
        response = self.authorized_client.get(
            self.url_post_edit, follow=True
        )
        self.assertRedirects(response, self.url_post)

    def test_posts_edit_url_exists_at_desired_location_author(self):
        '''Страница /posts/<int:post_id>/edit доступна автору поста'''
        response = self.author.get(self.url_post_edit)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_templates(self):
        '''URL-адрес использует корректрный шаблон'''
        adresses_templates = {
            URL_MAIN_PAGE: 'posts/index.html',
            URL_GROUP: 'posts/group_list.html',
            URL_PROFILE: 'posts/profile.html',
            self.url_post: 'posts/post_detail.html',
            self.url_post_edit: 'posts/create_post.html',
            URL_CREATE: 'posts/create_post.html',
        }
        for adress, template in adresses_templates.items():
            with self.subTest(adress=adress):
                response = self.author.get(adress)
                self.assertTemplateUsed(response, template)
