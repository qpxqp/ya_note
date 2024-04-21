from django.urls import reverse  # type: ignore
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.test_init import BaseTestNotesCase


class TestNotesList(BaseTestNotesCase):
    """Тестровавние создания/удаления/редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        super().setUpTestData()
        cls.NOTES_COUNT = 3
        cls.NOTE_INDEX = cls.NOTES_COUNT - 1

        cls.NOTE_INDEX_EXTEND = '-{index}'
        cls.NOTE_TITLE += cls.NOTE_INDEX_EXTEND
        cls.NOTE_SLUG += cls.NOTE_INDEX_EXTEND

        Note.objects.bulk_create(
            Note(
                title=cls.NOTE_TITLE.format(index=index),
                text='Текст заметки',
                slug=cls.NOTE_SLUG.format(index=index),
                author=cls.author
            )
            for index in range(cls.NOTES_COUNT)
        )

        cls.URL_NOTES_EDIT = reverse(cls.PATH_EDIT, args=(
            cls.NOTE_SLUG.format(index=cls.NOTE_INDEX),
        ))

    # ТЕСТЫ ======================================================
    def test_a_note_in_context_author_and_notauthor(self):
        """Проверка наличия заметки на странице со списком заметок."""
        for user, in_notes in (
            (self.author_client, True), (self.not_author_client, False)
        ):
            with self.subTest(user=user):
                response = user.get(self.URL_NOTES_LIST)
                notes = response.context['object_list']
                note = Note.objects.get(
                    slug=self.NOTE_SLUG.format(index=self.NOTE_INDEX)
                )
                self.assertIs(note in notes, in_notes)

    def test_b_note_has_form(self):
        """Проверка наличия формы заметки."""
        for url in self.URL_NOTES_ADD, self.URL_NOTES_EDIT:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_c_notes_count_for_author(self):
        """Проверка количества заметок на странице автора."""
        response = self.author_client.get(self.URL_NOTES_LIST)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, self.NOTES_COUNT)
