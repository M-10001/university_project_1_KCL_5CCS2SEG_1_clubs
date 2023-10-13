from django import forms
from django.test import TestCase
from clubs.forms import ApplicationEditForm
from clubs.models import User,Club,Membership

class ApplicationEditFormTestCase(TestCase):
    """Unit tests of the edit/update user profile form."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.club = Club.objects.get(name = "Test Club")
        self.membership = Membership.objects.create(
            club = self.club,
            member = self.user,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 0)

        self.form_input = {'member_first_name': 'test1',
            'member_last_name': '1lastname',
            'member_contact_details': 'Kings College London, Strand, WC2R 2LS',
            'member_personal_statement': 'Hello, I am a chess beginner.',
            'member_bio': 'My bio',
            'member_chess_experience_level': 3}

    def test_application_edit_form_has_necessary_fields(self):
        form = ApplicationEditForm()
        self.assertIn('member_first_name', form.fields)
        self.assertIn('member_last_name', form.fields)
        self.assertIn('member_contact_details', form.fields)
        self.assertIn('member_personal_statement', form.fields)
        self.assertIn('member_bio', form.fields)
        self.assertIn('member_chess_experience_level', form.fields)
        member_chess_experience_level_field = form.fields['member_chess_experience_level']
        self.assertTrue(isinstance(member_chess_experience_level_field, forms.ChoiceField))
        personal_statement_widget = form.fields['member_personal_statement'].widget
        self.assertTrue(isinstance(personal_statement_widget, forms.Textarea))
        member_bio_widget = form.fields['member_bio'].widget
        self.assertTrue(isinstance(member_bio_widget, forms.Textarea))

    def test_valid_user_personal_information_edit_form(self):
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_member_first_name_must_not_be_blank(self):
        self.form_input['member_first_name']=""
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_member_last_name_must_not_be_blank(self):
        self.form_input['member_last_name']=""
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_member_contact_details_must_not_be_blank(self):
        self.form_input['member_contact_details']=""
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_member_personal_statement_may_be_blank(self):
        self.form_input['member_personal_statement']=""
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_member_bio_may_be_blank(self):
        self.form_input['member_bio']=""
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_member_chess_experience_level_must_not_be_blank(self):
        self.form_input['member_chess_experience_level']=""
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_member_chess_experience_level_must_not_larger_than_3(self):
        self.form_input['member_chess_experience_level']=4
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_member_chess_experience_level_must_not_smaller_than_0(self):
        self.form_input['member_chess_experience_level']=-1
        form = ApplicationEditForm(instance = self.membership,data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = ApplicationEditForm(instance = self.membership, data=self.form_input)
        membership_before_count = Membership.objects.count()
        form.save()
        membership_after_count = Membership.objects.count()
        self.assertEqual(membership_after_count, membership_before_count)
        membership = Membership.objects.get(club=self.club,member=self.user)
        self.assertEqual(self.membership.member_first_name, 'test1')
        self.assertEqual(self.membership.member_last_name, '1lastname')
        self.assertEqual(self.membership.member_contact_details, 'Kings College London, Strand, WC2R 2LS')
        self.assertEqual(self.membership.member_personal_statement,'Hello, I am a chess beginner.')
        self.assertEqual(self.membership.member_bio, 'My bio')
        self.assertEqual(self.membership.member_chess_experience_level,3)
