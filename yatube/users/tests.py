from django.urls import reverse_lazy
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from http import HTTPStatus

from .forms import CreationForm, User


def setUpModule():
    global URL_LOGOUT, URL_SIGNUP, URL_LOGIN
    URL_LOGOUT = '/auth/logout/'
    URL_SIGNUP = '/auth/signup/'
    URL_LOGIN = '/auth/login/'


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_users_urls(self):
        '''Проверка достпупности адресов'''
        adresses = (URL_LOGOUT, URL_SIGNUP, URL_LOGIN)
        for adress in adresses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_use_correct_template(self):
        '''URL-адрес использует корректный шаблон'''
        adresses_templates = {
            URL_LOGOUT: 'users/logged_out.html',
            URL_SIGNUP: 'users/signup.html',
            URL_LOGIN: 'users/login.html',
        }
        for adress, template in adresses_templates.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)


class UsersViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_sisgnup_use_correct_templates(self):
        '''users:signup использует корректный шаблон'''
        template = 'users/signup.html'
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, template)

    def test_signup_page_show_correct_context(self):
        '''Шаблон users/signup сформирован с правильным контекстом'''
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='newone')
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_create(self):
        '''Валидная форма создает новый пост'''
        users_count = User.objects.count()
        form_data = {
            'first_name': 'nicolas',
            'last_name': 'cage',
            'username': 'testusermuser',
            'email': 'supermegatester@mail.ru',
            'password1': 'zaqwsx963',
            'password2': 'zaqwsx963',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse_lazy('posts:posts_main'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(username='testusermuser',).exists()
        )
