from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from clubs.forms import UserSignUpForm
from clubs.models import User

class UserSignUpFormTestCase(TestCase):
    """Unit tests of the user sign up form."""

    def setUp(self):
        self.form_input = {
            'email': 'test4@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
    def test_valid_sign_up_form(self):
        form = UserSignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = UserSignUpForm()
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_email_form_must_not_be_blank(self):
        self.form_input['email'] = ''
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_email_form_must_contain_at_validation(self):
        self.form_input['email'] = 'bademailexample.org'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_email_form_must_contain_one_at_validation(self):
        self.form_input['email'] = 'bademail@@example.org'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_email_form_must_not_contain_other_symbol_validation(self):
        self.form_input['email'] = 'bademail@exa#mple.org'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password456'
        self.form_input['password_confirmation'] = 'password456'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD456'
        self.form_input['password_confirmation'] = 'PASSWORD456'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABCDEF'
        self.form_input['password_confirmation'] = 'PasswordABCDEF'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword456'
        form = UserSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = UserSignUpForm(data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(email ='test4@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
