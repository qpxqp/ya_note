from http import HTTPStatus

from django.contrib.auth import get_user  # type: ignore

from notes.tests.test_init import BaseTestNotesCase


class TestRoutes(BaseTestNotesCase):
    """Тестирование маршрутов."""

    # ТЕСТЫ ======================================================
    def test_a_availability_urls_for_all_users(self):
        """Проверка доступности страниц для пользователей."""
        URLS = (
            (self.URL_USERS_LOGIN, self.client, HTTPStatus.OK),
            (self.URL_USERS_LOGOUT, self.client, HTTPStatus.OK),
            (self.URL_USERS_SIGNUP, self.client, HTTPStatus.OK),
            (self.URL_NOTES_HOME, self.client, HTTPStatus.OK),

            (self.URL_USERS_LOGIN, self.author_client, HTTPStatus.OK),
            (self.URL_USERS_SIGNUP, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_HOME, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_LIST, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_ADD, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_SUCCESS, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_EDIT, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_DELETE, self.author_client, HTTPStatus.OK),
            (self.URL_NOTES_DETAIL, self.author_client, HTTPStatus.OK),

            (self.URL_NOTES_EDIT, self.not_author_client,
                HTTPStatus.NOT_FOUND),
            (self.URL_NOTES_DELETE, self.not_author_client,
                HTTPStatus.NOT_FOUND),
            (self.URL_NOTES_DETAIL, self.not_author_client,
                HTTPStatus.NOT_FOUND),
        )
        for url, user_client, status in URLS:
            with self.subTest(
                url=url, user=get_user(user_client), status=status
            ):
                response = user_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_b_redirects_for_all_users(self):
        """Проверка перенаправлений для пользователей."""
        for url in (self.URL_NOTES_EDIT, self.URL_NOTES_DELETE,
                    self.URL_NOTES_DETAIL):
            with self.subTest(url=url, user=get_user(self.client)):
                redirect_url = f'{self.URL_USERS_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
