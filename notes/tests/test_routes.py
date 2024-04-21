from http import HTTPStatus

from django.contrib.auth import get_user_model, get_user
from django.urls import reverse  # type: ignore

from notes.models import Note
from notes.tests.test_init import BaseTestNotesCase


class TestRoutes(BaseTestNotesCase):
    """Тестирование маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        super().setUpTestData()
        cls.URLS = (
            (cls.URL_USERS_LOGIN, cls.anonymous_client, HTTPStatus.OK),
            (cls.URL_USERS_LOGOUT, cls.anonymous_client, HTTPStatus.OK),
            (cls.URL_USERS_SIGNUP, cls.anonymous_client, HTTPStatus.OK),
            (cls.URL_NOTES_HOME, cls.anonymous_client, HTTPStatus.OK),

            (cls.URL_USERS_LOGIN, cls.author_client, HTTPStatus.OK),
            (cls.URL_USERS_SIGNUP, cls.author_client, HTTPStatus.OK),
            (cls.URL_NOTES_HOME, cls.author_client, HTTPStatus.OK),
            (cls.URL_NOTES_LIST, cls.author_client, HTTPStatus.OK),
            (cls.URL_NOTES_ADD, cls.author_client, HTTPStatus.OK),
            (cls.URL_NOTES_SUCCESS, cls.author_client, HTTPStatus.OK),
        )

    def setUp(self):
        """Подготовка данных для теста."""
        self.note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.author
        )
        self.URL_EDIT = reverse(
            self.PATH_EDIT, args=(self.note.slug,)
        )
        self.URL_DELETE = reverse(
            self.PATH_DELETE, args=(self.note.slug,)
        )
        self.URL_DETAIL = reverse(
            self.PATH_DETAIL, args=(self.note.slug,)
        )

        self.URLS += (
            (self.URL_EDIT, self.author_client, HTTPStatus.OK),
            (self.URL_DELETE, self.author_client, HTTPStatus.OK),
            (self.URL_DETAIL, self.author_client, HTTPStatus.OK),

            (self.URL_EDIT, self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.URL_DELETE, self.not_author_client, HTTPStatus.NOT_FOUND),
            (self.URL_DETAIL, self.not_author_client, HTTPStatus.NOT_FOUND),
        )
        self.URLS_REDIRECTS = (
            (self.URL_EDIT, self.anonymous_client, self.URL_USERS_LOGIN),
            (self.URL_DELETE, self.anonymous_client, self.URL_USERS_LOGIN),
            (self.URL_DETAIL, self.anonymous_client, self.URL_USERS_LOGIN),
        )

    # ТЕСТЫ ======================================================
    def test_a_availability_urls_for_all_users(self):
        """Проверка доступности страниц для пользователей."""
        for url, user_client, status in self.URLS:
            with self.subTest(url=url, user=get_user(user_client)):
                response = user_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_b_redirects_for_all_users(self):
        """Проверка перенаправлений для пользователей."""
        for url, user_client, url_redirect in self.URLS_REDIRECTS:
            with self.subTest(url=url, user=get_user(user_client)):
                redirect_url = f'{url_redirect}?next={url}'
                response = user_client.get(url)
                self.assertRedirects(response, redirect_url)
