from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next

class ShowMemberViewTestCase(TestCase,LogInTester):
    """Tests of the show member view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json'
            ]

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.user2 = User.objects.get(email = 'test2@example.org')
        self.user3 = User.objects.get(email = 'test3@example.org')
        self.club = Club.objects.get(name = 'Test Club')
        self.url = reverse('show_member', kwargs={'club_id': self.club.id,'user_id': self.user2.id})
        self.membership = Membership.objects.create(
            club = self.club,
            member = self.user2,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1)

        Membership.objects.create(
            club = self.club,
            member = self.user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 3)

    def test_show_member_url(self):
        self.assertEqual(self.url,f'/member/{self.user2.id}/{self.club.id}/')

    def test_get_show_member_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_member_without_membership(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('user_page')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_member_with_membership_when_logged_in_with_valid_id(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        Membership.objects.create(
            club = self.club,
            member = self.user,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1
        )
        response = self.client.get(self.url)
        self.assertContains(response, self.membership.member_first_name)
        self.assertContains(response, self.membership.member_last_name)
        self.assertContains(response,self.membership.member_bio)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_member.html')

    def test_get_show_member_with_invalid_club_id(self):
        Membership.objects.create(
            club = self.club,
            member = self.user,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1
        )
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.invalid_url = reverse('show_member', kwargs={'club_id': self.club.id+9999,'user_id': self.user2.id})
        response = self.client.get(self.invalid_url, follow=True)
        response_url = reverse('user_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_page.html')

    def test_get_show_member_with_membership_with_invalid_user_id(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        Membership.objects.create(
            club = self.club,
            member = self.user,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1
        )
        self.invalid_url = reverse('show_member', kwargs={'club_id': self.club.id,'user_id': self.user2.id+9999})
        response = self.client.get(self.invalid_url, follow=True)
        response_url = reverse('member_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'member_list.html')
