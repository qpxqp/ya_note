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
        cls.URLS_AUTH = (
            ('notes:home', None, False),
            (cls.LOGIN_PATH, None, False),
            ('users:logout', None, False),
            ('users:signup', None, False),
            ('notes:list', None, True),
            ('notes:add', None, True),
            ('notes:success', None, True),
        )

    def setUp(self):
        """Подготовка данных для теста."""
        self.author = User.objects.create(username='Автор')
        self.notauthor = User.objects.create(username='Не автор')
        self.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='slug-note',
            author=self.author
        )
        self.URLS_AUTH += (
            ('notes:edit', (self.note.slug,), True),
            ('notes:detail', (self.note.slug,), True),
            ('notes:delete', (self.note.slug,), True),
        )

    def check_url_equal_status(self, name, args, status=HTTPStatus.OK):
        """Проверка статуса url."""
        url = reverse(name, args=args)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)

    # ТЕСТЫ ======================================================
    def test_a_availability_urls_for_author(self):
        """Проверка доступности страниц для автора."""
        for name, args, _ in self.URLS_AUTH:
            with self.subTest(user=self.author, name=name):
                self.client.force_login(self.author)
                self.check_url_equal_status(name, args)

    def test_b_ailability_urls_for_notauthor(self):
        """Проверка доступности страниц для не автора."""
        for name, args, _ in self.URLS_AUTH:
            with self.subTest(user=self.notauthor, name=name):
                self.client.force_login(self.notauthor)
                self.check_url_equal_status(
                    name,
                    args,
                    HTTPStatus.NOT_FOUND if args else HTTPStatus.OK
                )

    def test_c_ailability_urls_for_anonymous(self):
        """Проверка доступности страниц для анонима."""
        for name, args, auth in self.URLS_AUTH:
            with self.subTest(name=name):
                if not auth:
                    self.check_url_equal_status(name, args)
                else:
                    login_url = reverse(self.LOGIN_PATH)
                    url = reverse(name, args=args)
                    redirect_url = f'{login_url}?next={url}'
                    response = self.client.get(url)
                    self.assertRedirects(response, redirect_url)
