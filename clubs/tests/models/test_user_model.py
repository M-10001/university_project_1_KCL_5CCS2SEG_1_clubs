from django.test import TestCase
from django.core.exceptions import ValidationError
from clubs.models import User

class UserModelTestCase(TestCase):

    fixtures = [
            'clubs/tests/fixtures/default_user.json',
            'clubs/tests/fixtures/other_users.json'
         ]

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.user2 = User.objects.get(email = 'test2@example.org')

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        self.user.email = self.user2.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'teat1example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'test1@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'test1@example'
        self._assert_user_is_invalid()

    def test_email_must_contain_only_one_at_symbol(self):
        self.user.email = 'teat1@@example.org'
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
