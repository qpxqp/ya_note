from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseTestNotesCase(TestCase):
    """Подготовка для тестов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования."""
        cls.NOTE_TITLE = 'Заголовок заметки'
        cls.NOTE_TEXT = 'Текст заметки'
        cls.NOTE_SLUG = 'slug'

        cls.URL_USERS_LOGIN = reverse('users:login')
        cls.URL_USERS_LOGOUT = reverse('users:logout')
        cls.URL_USERS_SIGNUP = reverse('users:signup')
        cls.URL_NOTES_HOME = reverse('notes:home')
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_SUCCESS = reverse('notes:success')
        cls.PATH_EDIT = 'notes:edit'
        cls.PATH_DELETE = 'notes:delete'
        cls.PATH_DETAIL = 'notes:detail'

        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.anonymous_client = Client()
