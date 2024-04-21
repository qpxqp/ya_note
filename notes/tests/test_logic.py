from http import HTTPStatus

from django.contrib.auth import get_user_model, get_user
from django.urls import reverse  # type: ignore
from pytils.translit import slugify

from .test_init import BaseTestNotesCase
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreateEditDelete(BaseTestNotesCase):
    """Тестровавние создания/удаления/редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для класса."""
        super().setUpTestData()
        cls.NEW_NOTE_TITLE = 'Обновлённый заголовок заметки'
        cls.NEW_NOTE_TEXT = 'Обновлённая заметка'
        cls.NEW_NOTE_SLUG = 'new-slug'

        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }
        cls.form_data_new_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def setUp(self):
        self.note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.author
        )

        self.URL_NOTES_EDIT = reverse(
            self.PATH_EDIT, args=(self.note.slug,)
        )
        self.URL_NOTES_DELETE = reverse(
            self.PATH_DELETE, args=(self.note.slug,)
        )

    # ТЕСТЫ ======================================================
    def test_a_authorized_user_created_note(self):
        """Тестирование создания заметки автором."""
        notes_count = Note.objects.count()

        response = self.author_client.post(self.URL_NOTES_ADD,
                                           data=self.form_data_new_slug)
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), notes_count + 1)

        note = Note.objects.get(slug=self.form_data_new_slug['slug'])
        self.assertEqual(note.title, self.form_data_new_slug['title'])
        self.assertEqual(note.text, self.form_data_new_slug['text'])
        self.assertEqual(note.author, get_user(self.author_client))

    def test_b_anonymous_user_cant_create_note(self):
        """Тестирование создания заметки от анонимного клиента."""
        notes_count = Note.objects.count()
        self.anonymous_client.post(self.URL_NOTES_ADD,
                                   data=self.form_data_new_slug)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_c_user_cant_edit_note_of_another_user(self):
        """Тестирование на редактирование от имени другого пользователя."""
        notes_count = Note.objects.count()
        response = self.not_author_client.post(self.URL_NOTES_EDIT,
                                               data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, Note.objects.count())
        note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_d_user_cant_delete_note_of_another_user(self):
        """Тестирование на удаление заметки от имени другого пользователя."""
        notes_count = Note.objects.count()
        response = self.not_author_client.delete(self.URL_NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_e_author_can_edit_note(self):
        """Тестирование на редактирование от имени автора."""
        response = self.author_client.post(self.URL_NOTES_EDIT,
                                           data=self.form_data)
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_f_author_can_delete_note(self):
        """Тестирование на удаление от имени автора."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.URL_NOTES_DELETE)
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_g_created_notunique_slug_in_note(self):
        """Тестирование создания заметки с неуникальным полем slug."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.URL_NOTES_ADD,
                                           data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertFormError(
            response, 'form', 'slug',
            errors=self.form_data.get('slug') + WARNING,
        )

    def test_h_create_slug_with_slugify(self):
        """Проверка автоматического формирования slug при пустом поле."""
        self.form_data['slug'] = ''
        notes_count = Note.objects.count()
        response = self.author_client.post(self.URL_NOTES_ADD,
                                           data=self.form_data)
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        slug = slugify(self.form_data['title'])
        self.assertEqual(Note.objects.get(slug=slug).slug, slug)
