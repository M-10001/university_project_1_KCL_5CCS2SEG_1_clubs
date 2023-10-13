from django.test import TestCase
from django.core.exceptions import ValidationError
from clubs.models import Club, User, Membership

class MembershipModelTestCase(TestCase):

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
    ]
    def setUp(self):
        super(TestCase, self).setUp()
        self.club = Club.objects.get(name = 'Test Club')
        self.user = User.objects.get(email = 'test1@example.org')
        self.membership = Membership.objects.create(
            club = self.club,
            member = self.user ,
            member_first_name = "first_name1",
            member_last_name = "last_name1",
            member_contact_details = "0123456789",
            member_personal_statement ="This is my personal statement.",
            member_bio="My bio",
            member_chess_experience_level="1",
            member_type = "2"
        )

    def test_valid_membership(self):
        self._assert_membership_is_valid()

    def test_member_first_name_must_not_be_blank(self):
        self.membership.member_first_name = ""
        self._assert_membership_is_invalid()

    def test_member_first_name_may_contain_50_characters(self):
        self.membership.member_first_name = "x" * 50
        self._assert_membership_is_valid()

    def test_member_first_name_must_not_contain_more_than_50_characters(self):
        self.membership.member_first_name = "x" * 51
        self._assert_membership_is_invalid()

    def test_member_last_name_must_not_be_blank(self):
        self.membership.member_last_name = ""
        self._assert_membership_is_invalid()

    def test_member_last_name_may_contain_50_characters(self):
        self.membership.member_last_name = "x" * 50
        self._assert_membership_is_valid()

    def test_member_last_name_must_not_contain_more_than_50_characters(self):
        self.membership.member_last_name = "x" * 51
        self._assert_membership_is_invalid()

    def test_member_contact_details_must_not_be_blank(self):
        self.membership.member_contact_details = ""
        self._assert_membership_is_invalid()

    def test_member_contact_details_may_contain_100_characters(self):
        self.membership.member_contact_details = "x" * 100
        self._assert_membership_is_valid()

    def test_member_contact_details_must_not_contain_more_than_100_characters(self):
        self.membership.member_contact_details = "x" * 101
        self._assert_membership_is_invalid()

    def test_member_personal_statement_may_be_blank(self):
        self.membership.member_personal_statement = ""
        self._assert_membership_is_valid()

    def test_member_personal_statement_may_contain_200_characters(self):
        self.membership.member_personal_statement = "x" * 200
        self._assert_membership_is_valid()

    def test_member_personal_statement_must_not_contain_more_than_200_characters(self):
        self.membership.member_personal_statement = "x" * 201
        self._assert_membership_is_invalid()

    def test_member_bio_may_be_blank(self):
        self.membership.member_bio = ""
        self._assert_membership_is_valid()

    def test_member_bio_may_contain_500_characters(self):
        self.membership.member_bio = "x" * 500
        self._assert_membership_is_valid()

    def test_member_bio_must_not_contain_more_than_500_characters(self):
        self.membership.member_bio = "x" * 501
        self._assert_membership_is_invalid()

    def test_member_chess_experience_level_must_not_be_blank(self):
        self.membership.member_chess_experience_level = None
        self._assert_membership_is_invalid()

    def test_member_chess_experience_level_may_be_0_1_2_3(self):
        self.membership.member_chess_experience_level = 0
        self._assert_membership_is_valid()
        self.membership.member_chess_experience_level = 1
        self._assert_membership_is_valid()
        self.membership.member_chess_experience_level = 2
        self._assert_membership_is_valid()
        self.membership.member_chess_experience_level = 3
        self._assert_membership_is_valid()

    def test_member_chess_experience_level_must_not_larger_than_3(self):
        self.membership.member_chess_experience_level = 4
        self._assert_membership_is_invalid()

    def test_member_chess_experience_level_must_not_smaller_than_0(self):
        self.membership.member_chess_experience_level = -1
        self._assert_membership_is_invalid()

    def test_member_type_must_not_be_blank(self):
        self.membership.member_type = None
        self._assert_membership_is_invalid()

    def test_member_type_may_be_0_1_2_3(self):
        self.membership.member_type = 0
        self._assert_membership_is_valid()
        self.membership.member_type = 1
        self._assert_membership_is_valid()
        self.membership.member_type = 2
        self._assert_membership_is_valid()
        self.membership.member_type = 3
        self._assert_membership_is_valid()

    def test_member_type_must_not_larger_than_3(self):
        self.membership.member_type = 4
        self._assert_membership_is_invalid()

    def test_member_type_must_not_smaller_than_0(self):
        self.membership.member_type = -1
        self._assert_membership_is_invalid()

    def _assert_membership_is_valid(self):
        try:
            self.membership.full_clean()
        except (ValidationError):
            self.fail('Test membership should be valid')

    def _assert_membership_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership.full_clean()
