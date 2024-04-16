from http import HTTPStatus

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import Client, TestCase  # type: ignore
from django.urls import reverse  # type: ignore
from pytils.translit import slugify

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
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')

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

    def setUp(self):
        self.author = User.objects.create(username='Автор')
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.author
        )

        self.EDIT_URL = reverse('notes:edit', args=(self.note.slug,))
        self.DELETE_URL = reverse('notes:delete', args=(self.note.slug,))

        self.notauthor = User.objects.create(username='Не автор')
        self.notauthor_client = Client()
        self.notauthor_client.force_login(self.notauthor)

    # ТЕСТЫ ======================================================
    def test_a_authorized_user_created_note(self):
        """Тестирование создания заметки автором."""
        notes_count = Note.objects.count()

        response = self.author_client.post(self.ADD_URL,
                                           data=self.form_data_new_slug)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count + 1)

        note = Note.objects.get(slug=self.NEW_NOTE_SLUG)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_b_anonymous_user_cant_create_note(self):
        """Тестирование создания заметки от анонимного клиента."""
        notes_count = Note.objects.count()
        self.client.post(self.ADD_URL,
                         data=self.form_data_new_slug)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_c_user_cant_edit_note_of_another_user(self):
        """Тестирование на редактирование от имени другого пользователя."""
        response = self.notauthor_client.post(self.EDIT_URL,
                                              data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_d_user_cant_delete_note_of_another_user(self):
        """Тестирование на удаление заметки от имени другого пользователя."""
        notes_count = Note.objects.count()
        response = self.notauthor_client.delete(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_e_author_can_edit_note(self):
        """Тестирование на редактирование от имени автора."""
        response = self.author_client.post(self.EDIT_URL,
                                           data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_f_author_can_delete_note(self):
        """Тестирование на удаление от имени автора."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_g_created_notunique_slug_in_note(self):
        """Тестирование создания заметки с неуникальным полем slug."""
        with self.assertRaises(IntegrityError):
            Note.objects.create(
                title=self.NOTE_TITLE,
                text=self.NOTE_TEXT,
                slug=self.NOTE_SLUG,
                author=self.author
            )

    def test_h_create_slug_with_slugify(self):
        """Проверка автоматического формирования slug при незаполненном поле."""
        title = 'Новая заметка без слага'
        self.note = Note.objects.create(
            title=title,
            text=self.NOTE_TEXT,
            author=self.author
        )
        max_slug_length = Note._meta.get_field('slug').max_length
        slug = slugify(title)[:max_slug_length]
        self.assertEqual(Note.objects.get(slug=slug).slug, slug)
