from django import forms
from django.test import TestCase
from clubs.forms import ClubCreationForm
from clubs.models import Club

class ClubCreationFormTestCase(TestCase):
    """Unit tests of the club creation form."""

    def setUp(self):
        self.form_input = {"name": "Test Club",
            "location": "Test Location 111",
            "description": "This is a test Club"}

    def test_valid_club_creation_form(self):
        form = ClubCreationForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_club_creation_form_has_necessary_fields(self):
        form = ClubCreationForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)
        location_widget = form.fields['location'].widget
        self.assertTrue(isinstance(location_widget, forms.Textarea))
        description_widget = form.fields['description'].widget
        self.assertTrue(isinstance(description_widget, forms.Textarea))

    def test_name_field_must_not_be_blank(self):
        self.form_input['name'] =''
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_location_field_must_not_be_blank(self):
        self.form_input['location'] =''
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_description_field_must_not_be_blank(self):
        self.form_input['description'] =''
        form = ClubCreationForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_club_creation_form_must_save_correctly(self):
        form = ClubCreationForm(data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        club = Club.objects.get(name="Test Club")
        self.assertEqual(club.location,"Test Location 111")
        self.assertEqual(club.description,"This is a test Club")
