from django import forms
from django.test import TestCase
from clubs.forms import MembershipSignUpForm
from clubs.models import Membership, Club, User

class MembershipSignUpFormTestCase(TestCase):
    """Unit tests of the membership sign up form."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.club = Club.objects.get(name = 'Test Club')
        self.form_input = {"member_first_name": "first_name1",
            "member_last_name": "last_name1",
            "member_contact_details": "0712345678",
            "member_personal_statement": "My personal statement",
            "member_bio": "my bio",
            "member_chess_experience_level": 0,
            "club" : 'Test Club' ,}

    def test_valid_membership_sign_up_form(self):
        form = MembershipSignUpForm(data=self.form_input, user=self.user)
        self.assertTrue(form.is_valid())

    def test_membership_sign_up_form_has_necessary_fields(self):
        form = MembershipSignUpForm(user=self.user)
        self.assertIn('member_first_name', form.fields)
        self.assertIn('member_last_name', form.fields)
        self.assertIn('member_contact_details', form.fields)
        self.assertIn('member_personal_statement', form.fields)
        self.assertIn('member_bio', form.fields)
        self.assertIn('member_chess_experience_level', form.fields)
        self.assertIn('club', form.fields)
        member_chess_experience_level_field = form.fields['member_chess_experience_level']
        self.assertTrue(isinstance(member_chess_experience_level_field, forms.ChoiceField))
        personal_statement_widget = form.fields['member_personal_statement'].widget
        self.assertTrue(isinstance(personal_statement_widget, forms.Textarea))
        member_bio_widget = form.fields['member_bio'].widget
        self.assertTrue(isinstance(member_bio_widget, forms.Textarea))
        club_field = form.fields['club']
        self.assertTrue(isinstance(club_field, forms.ChoiceField))

    def test_member_first_name_must_not_be_blank(self):
        self.form_input['member_first_name'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_member_last_name_must_not_be_blank(self):
        self.form_input['member_last_name'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_member_contact_details_must_not_be_blank(self):
        self.form_input['member_contact_details'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_member_personal_statement_may_be_blank(self):
        self.form_input['member_personal_statement'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertTrue(form.is_valid())

    def test_member_bio_may_be_blank(self):
        self.form_input['member_bio'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertTrue(form.is_valid())

    def test_member_chess_experience_level_must_not_be_blank(self):
        self.form_input['member_chess_experience_level'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_member_chess_experience_level_must_not_larger_than_3(self):
        self.form_input['member_chess_experience_level'] = 4
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_member_chess_experience_level_must_not_smaller_than_0(self):
        self.form_input['member_chess_experience_level'] = -1
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_club_must_not_be_blank(self):
        self.form_input['club'] = ''
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        self.assertFalse(form.is_valid())

    def test_membership_sign_up_form_must_save_correctly(self):
        form = MembershipSignUpForm(data=self.form_input,user=self.user)
        before_count = Membership.objects.count()
        form.save()
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count+1)
        membership = Membership.objects.get(member_first_name= "first_name1")
        self.assertEqual(membership.member_last_name,"last_name1")
        self.assertEqual(membership.member_contact_details,"0712345678")
        self.assertEqual(membership.member_personal_statement,"My personal statement")
        self.assertEqual(membership.member_bio,"my bio")
        self.assertEqual(membership.member_chess_experience_level,0)
