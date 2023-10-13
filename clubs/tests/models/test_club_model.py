from django.test import TestCase
from django.core.exceptions import ValidationError
from clubs.models import Club

class ClubModelTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(name = 'Test Club')
        self.club2 = Club.objects.get(name = 'Test Club 2')

    def test_valid_club(self):
        self._assert_club_is_valid()

    def test_club_name_must_not_be_blank(self):
        self.club.name = ""
        self._assert_club_is_invalid()

    def test_club_name_must_be_unique(self):
        self.club.name = self.club2.name
        self._assert_club_is_invalid()

    def test_club_name_may_contain_50_characters(self):
        self.club.name = "*" * 50
        self._assert_club_is_valid()

    def test_club_name_must_not_contain_more_than_50_characters(self):
        self.club.name = "*" * 51
        self._assert_club_is_invalid()

    def test_club_location_can_not_be_blank(self):
        self.club.location = ""
        self._assert_club_is_invalid()

    def test_club_location_may_contain_100_characters(self):
        self.club.location = "*" * 100
        self._assert_club_is_valid()

    def test_club_location_must_not_contain_more_than_100_characters(self):
        self.club.location = "*" * 101
        self._assert_club_is_invalid()

    def test_club_description_must_not_be_blank(self):
        self.club.description = ""
        self._assert_club_is_invalid()

    def test_club_description_may_contain_500_characters(self):
        self.club.description = "*" * 500
        self._assert_club_is_valid()

    def test_club_description_must_not_contain_more_than_500_characters(self):
        self.club.description = "*" * 501
        self._assert_club_is_invalid()

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()
