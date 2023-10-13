from clubs.models import User,Club, Membership
from django.test import TestCase
from django.urls import reverse
from clubs.tests.helpers import LogInTester,reverse_with_next

class ClubPageViewTestCase(TestCase,LogInTester):
    """Tests of the club page view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_users.json',
            ]

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.user2 = User.objects.get(email = 'test2@example.org')
        self.club = Club.objects.get(name = 'Test Club')
        Membership.objects.create(
            club = self.club,
            member = self.user2,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 3
        )
        self.url = reverse('club_page', kwargs={'club_id': self.club.id})

    def test_club_page_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}/')

    def test_get_club_page_without_membership(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('user_page')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_page_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_page_with_invalid_id(self):
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
        invalid_url = reverse('club_page', kwargs={'club_id': self.club.id+9999})
        response = self.client.get(invalid_url)
        redirect_url = reverse('user_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_club_page_with_membership_when_logged_in(self):
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
        self.assertContains(response, self.club.name)
        self.assertContains(response, self.club.location)
        self.assertContains(response,self.club.description)
        membership = Membership.objects.get(club=self.club,member_type=3)
        self.assertContains(response,membership.member_first_name)
        self.assertContains(response,membership.member_last_name)
        self.assertContains(response,membership.member_bio)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_page.html')
