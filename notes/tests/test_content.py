from django.test import TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from .test_init import User
from notes.forms import NoteForm
from notes.models import Note


class TestNotesList(TestCase):
    """Тестровавние создания/удаления/редактирования заметки."""

    NOTES_COUNT = 3

    NOTE_TITLE = 'Заголовок заметки-{index}'
    NOTE_SLUG = 'slug-{index}'
    NOTE_INDEX = NOTES_COUNT - 1

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        cls.NOTES_LIST_URL = reverse('notes:list')
        cls.NOTES_ADD_URL = reverse('notes:add')

    def setUp(self):
        self.author = User.objects.create(username='Автор')
        self.notauthor = User.objects.create(username='Не автор')
        all_note = [
            Note(
                title=self.NOTE_TITLE.format(index=index),
                text='Текст заметки',
                slug=self.NOTE_SLUG.format(index=index),
                author=self.author
            )
            for index in range(self.NOTES_COUNT)
        ]
        Note.objects.bulk_create(all_note)

        self.NOTES_EDIT_URL = reverse('notes:edit', args=(
            self.NOTE_SLUG.format(index=self.NOTE_INDEX),
        ))

    # ТЕСТЫ ======================================================
    def test_a_note_in_context_author_and_notauthor(self):
        """Проверка наличия заметки на странице со списком заметок."""
        for user in self.author, self.notauthor:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.NOTES_LIST_URL)
                notes = response.context['object_list']
                note = Note.objects.get(
                    slug=self.NOTE_SLUG.format(index=self.NOTE_INDEX)
                )
                if user is self.author:
                    self.assertIn(note, notes)
                else:
                    self.assertNotIn(note, notes)

    def test_b_note_not_in_context_notauthor(self):
        """Проверка заметок автора в списке не автора."""
        self.client.force_login(self.notauthor)
        response = self.client.get(self.NOTES_LIST_URL)
        notes = response.context['object_list']
        note = Note.objects.get(
            slug=self.NOTE_SLUG.format(index=self.NOTE_INDEX)
        )
        self.assertNotIn(note, notes)

    def test_c_note_has_form(self):
        """Проверка наличия формы заметки."""
        for url in self.NOTES_ADD_URL, self.NOTES_EDIT_URL:
            self.client.force_login(self.author)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)

    def test_d_notes_count_for_author(self):
        """Проверка количества заметок на странице автора."""
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, self.NOTES_COUNT)
