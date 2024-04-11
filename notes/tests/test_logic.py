from http import HTTPStatus
from django.db import IntegrityError
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from .test_init import User
from notes.models import Note


class TestNoteCreateEditDelete(TestCase):
    """Тестровавние создания/удаления/редактирования заметки."""

    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NEW_NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.attacker = User.objects.create(username='Злоумышленник')
        cls.attacker_client = Client()
        cls.attacker_client.force_login(cls.attacker)

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }
        cls.form_data_new_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    # ТЕСТЫ ======================================================
    def test_a_authorized_user_created_note(self):
        """Тестирование создания заметки автором."""
        notes_count = Note.objects.count()

        response = self.author_client.post(self.add_url,
                                           data=self.form_data_new_slug)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count + 1)

        note = Note.objects.get(slug=self.NEW_NOTE_SLUG)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_b_anonymous_user_cant_create_note(self):
        """Тестирование создания заметки от анонимного клиента."""
        notes_count = Note.objects.count()
        self.client.post(self.add_url,
                         data=self.form_data_new_slug)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_c_user_cant_edit_note_of_another_user(self):
        """Тестирование на редактирование от имени другого пользователя."""
        response = self.attacker_client.post(self.edit_url,
                                             data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_d_user_cant_delete_note_of_another_user(self):
        """Тестирование на удаление заметки от имени другого пользователя."""
        notes_count = Note.objects.count()
        response = self.attacker_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_e_author_can_edit_note(self):
        """Тестирование на редактирование от имени автора."""
        response = self.author_client.post(self.edit_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_f_author_can_delete_note(self):
        """Тестирование на удаление от имени автора."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_g_created_notunique_note(self):
        """Тестирование создания заметки с неуникальным полем slug."""
        with self.assertRaises(IntegrityError):
            Note.objects.create(
                title=self.NOTE_TITLE,
                text=self.NOTE_TEXT,
                slug=self.NOTE_SLUG,
                author=self.author
            )
