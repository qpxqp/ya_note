from http import HTTPStatus

from django.test import TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from .test_init import User
from notes.models import Note


class TestRoutes(TestCase):
    """Тестирование маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        cls.LOGIN_PATH = 'users:login'
        cls.URLS = (
            ('notes:home', None),
            (cls.LOGIN_PATH, None),
            ('users:logout', None),
            ('users:signup', None),
        )
        cls.URLS_FOR_AUTHENTIFICATED = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )

    def setUp(self):
        """Подготовка данных для теста."""
        self.author = User.objects.create(username='Автор')
        self.attacker = User.objects.create(username='Злоумышленник')
        self.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='slug-note',
            author=self.author
        )
        self.URLS_FOR_AUTHOR = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

    def check_url_equal_status(self, name, args, status=HTTPStatus.OK):
        """Проверка статуса url."""
        url = reverse(name, args=args)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)

    # ТЕСТЫ ======================================================
    def test_a_pages_availability(self):
        """Проверка доступности страниц анонимом."""
        for name, args in self.URLS:
            with self.subTest(name=name):
                self.check_url_equal_status(name, args)

    def test_b_availability_notes_for_author(self):
        """Проверка доступности страниц заметки и списка заметок для автора."""
        self.client.force_login(self.author)
        for name, args in self.URLS_FOR_AUTHOR + self.URLS_FOR_AUTHENTIFICATED:
            with self.subTest(user=self.author, name=name):
                self.check_url_equal_status(name, args)

    def test_c_notavailability_notes_for_attacker(self):
        """Проверка доступности страниц заметки для не автора."""
        self.client.force_login(self.attacker)
        for name, args in self.URLS_FOR_AUTHOR:
            with self.subTest(user=self.author, name=name):
                self.check_url_equal_status(name, args, HTTPStatus.NOT_FOUND)

    def test_d_redirect_for_anonymous_client(self):
        """Проверка редиректов."""
        login_url = reverse(self.LOGIN_PATH)
        for name, args in self.URLS_FOR_AUTHOR:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
