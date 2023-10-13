from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next

class SetOwnerViewTestCase(TestCase,LogInTester):
    """Tests of the set owner view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json'
            ]

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.user2 = User.objects.get(email = 'test2@example.org')
        self.club = Club.objects.get(name = 'Test Club')
        Membership.objects.create(
            club = self.club,
            member = self.user,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 2)

        Membership.objects.create(
            club = self.club,
            member = self.user2,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 3)

        self.url = reverse('set_owner', kwargs={'club_id': self.club.id,'user_id': self.user.id})

    def test_set_officer_url(self):
        self.assertEqual(self.url,f'/set_owner/{self.user.id}/{self.club.id}/')

    def test_set_owner_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_owner_without_membership(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test3@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('user_page')
        response = self.client.get(self.url,follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_owner_with_invalid_club_id(self):
        self.client.login(email = 'test2@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('set_owner', kwargs={'club_id': self.club.id+9999,'user_id': self.user.id})
        response = self.client.get(url,follow=True)
        membership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, membership.member)
        redirect_url = reverse('user_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_owner_with_invalid_user_id(self):
        self.client.login(email = 'test2@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('set_owner', kwargs={'club_id': self.club.id,'user_id': self.user.id+9999})
        response = self.client.get(url,follow=True)
        membership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, membership.member)
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_set_owner(self):
        self.client.login(email = 'test2@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url,follow=True)
        ownership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user, ownership.member)
        membership = Membership.objects.get(club = self.club, member = self.user2)
        self.assertEqual(membership.member_type,2)
        redirect_url = reverse('show_member', kwargs = {'user_id' : self.user.id, 'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_owner_with_applicant_membership(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test3@example.org', password='Password123')
        Membership.objects.create(
            club = self.club,
            member = user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 0)
        response = self.client.get(self.url,follow=True)
        ownership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, ownership.member)
        applicantship = Membership.objects.get(club = self.club, member = user3)
        self.assertEqual(applicantship.member_type,0)
        officership = Membership.objects.get(club = self.club, member = self.user)
        self.assertEqual(officership.member_type,2)
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_owner_with_member_membership(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test3@example.org', password='Password123')
        Membership.objects.create(
            club = self.club,
            member = user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1)
        response = self.client.get(self.url,follow=True)
        ownership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, ownership.member)
        membership = Membership.objects.get(club = self.club, member = user3)
        self.assertEqual(membership.member_type,1)
        officership = Membership.objects.get(club = self.club, member = self.user)
        self.assertEqual(officership.member_type,2)
        redirect_url = reverse('member_list', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_owner_with_officer_membership(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test3@example.org', password='Password123')
        Membership.objects.create(
            club = self.club,
            member = user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 2)
        response = self.client.get(self.url,follow=True)
        ownership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, ownership.member)
        officership = Membership.objects.get(club = self.club, member = self.user)
        self.assertEqual(officership.member_type,2)
        redirect_url = reverse('show_member', kwargs = {'user_id' : self.user.id, 'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_applicant_to_owner(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test2@example.org', password='Password123')
        Membership.objects.create(
            club = self.club,
            member = user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 0)
        url = reverse('set_owner', kwargs={'club_id': self.club.id,'user_id': user3.id})
        response = self.client.get(url,follow=True)
        ownership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, ownership.member)
        applicantship = Membership.objects.get(club = self.club, member = user3)
        self.assertEqual(applicantship.member_type,0)
        redirect_url = reverse('show_member', kwargs = {'user_id' : user3.id, 'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_member_to_owner(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test2@example.org', password='Password123')
        Membership.objects.create(
            club = self.club,
            member = user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1)
        url = reverse('set_owner', kwargs={'club_id': self.club.id,'user_id': user3.id})
        response = self.client.get(url,follow=True)
        ownership = Membership.objects.get(club = self.club, member_type = 3)
        self.assertEqual(self.user2, ownership.member)
        membership = Membership.objects.get(club = self.club, member = user3)
        self.assertEqual(membership.member_type,1)
        redirect_url = reverse('show_member', kwargs = {'user_id' : user3.id, 'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
