from django.test import TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from .test_init import User
from notes.forms import NoteForm
from notes.models import Note


class TestNotesList(TestCase):
    """Тестровавние создания/удаления/редактирования заметки."""

    NOTES_COUNT = 3

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        cls.author = User.objects.create(username='Автор')
        cls.notes_list_url = reverse('notes:list')
        cls.notes_add_url = reverse('notes:add')
        all_note = [
            Note(
                title='Заголовок заметки',
                text='Текст заметки',
                slug=f'slug-{index}',
                author=cls.author
            )
            for index in range(cls.NOTES_COUNT)
        ]
        Note.objects.bulk_create(all_note)

    # ТЕСТЫ ======================================================
    def test_a_notes_count_for_author(self):
        """Подсчет количества заметок на странице автора."""
        self.client.force_login(self.author)
        response = self.client.get(self.notes_list_url)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, self.NOTES_COUNT)

    def test_authorized_client_has_form(self):
        """Проверка наличия формы для добавления заметки."""
        self.client.force_login(self.author)
        response = self.client.get(self.notes_add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
