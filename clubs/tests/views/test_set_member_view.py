from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next

class SetMemberViewTestCase(TestCase,LogInTester):
    """Tests of the set member view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json'
            ]

    def setUp(self):
        self.user = User.objects.get(email = 'test1@example.org')
        self.user2 = User.objects.get(email = 'test2@example.org')
        self.user3 = User.objects.get(email = 'test3@example.org')
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
            member_type = 2
        )
        Membership.objects.create(
            club = self.club,
            member = self.user2,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 0
        )
        Membership.objects.create(
            club = self.club,
            member = self.user3,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 3
        )

        self.url = reverse('set_member', kwargs={
                'club_id': self.club.id,
                'user_id': self.user2.id,
            })

    def test_set_member_url(self):
        self.assertEqual(self.url,f'/set_member/{self.user2.id}/{self.club.id}/')

    def test_set_member_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_member_without_membership(self):
        user4 = User.objects.get(email = 'test4@example.org')
        self.client.login(email = 'test4@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        redirect_url = reverse('user_page')
        response = self.client.get(self.url,follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_set_applicant_to_member_with_officer_membership(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        response = self.client.get(self.url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        new_membership = Membership.objects.filter(member_type=1).latest('member')
        self.assertEqual(self.user2, new_membership.member)
        self.assertEqual(applicant_after_count, applicant_before_count-1)
        self.assertEqual(member_after_count, member_before_count+1)
        response_url = reverse('show_member', kwargs = {'user_id' : self.user2.id, 'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_member.html')

    def test_set_applicant_to_member_with_ownership(self):
        self.client.login(email = 'test3@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        response = self.client.get(self.url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count-1)
        self.assertEqual(member_after_count, member_before_count+1)
        new_membership = Membership.objects.filter(member_type=1).latest('member')
        self.assertEqual(self.user2, new_membership.member)
        response_url = reverse('show_member', kwargs = {'user_id' : self.user2.id, 'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_member.html')

    def test_set_officer_to_member_with_ownership(self):
        self.client.login(email = 'test3@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('set_member', kwargs={
                'club_id': self.club.id,
                'user_id': self.user.id,
            })
        officer_before_count = Membership.objects.filter(member_type=2).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        response = self.client.get(url,follow=True)
        officer_after_count = Membership.objects.filter(member_type=2).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(officer_after_count, officer_before_count-1)
        self.assertEqual(member_after_count, member_before_count+1)
        new_membership = Membership.objects.filter(member_type=1).latest('member')
        self.assertEqual(self.user, new_membership.member)
        response_url = reverse('show_member', kwargs = {'user_id' : self.user.id, 'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_member.html')

    def test_set_member_with_applicant_membership(self):
        self.client.login(email = 'test2@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        response = self.client.get(self.url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count)
        self.assertEqual(member_after_count, member_before_count)
        response_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_page.html')

    def test_set_member_with_member_membership(self):
        user4 = User.objects.get(email = 'test4@example.org')
        Membership.objects.create(
            club = self.club,
            member = user4,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1
        )
        self.client.login(email = 'test4@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        response = self.client.get(self.url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count)
        self.assertEqual(member_after_count, member_before_count)
        response_url = reverse('member_list', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'member_list.html')

    def test_set_member_to_member(self):
        user4 = User.objects.get(email = 'test4@example.org')
        Membership.objects.create(
            club = self.club,
            member = user4,
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
        url = reverse('set_member', kwargs={
                'club_id': self.club.id,
                'user_id': user4.id,
            })
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        response = self.client.get(url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count)
        self.assertEqual(member_after_count, member_before_count)
        response_url = reverse('show_member', kwargs = {'user_id' : user4.id, 'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_member.html')

    def test_set_member_with_invalid_club_id(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        url = reverse('set_member', kwargs={
                'club_id': self.club.id+9999,
                'user_id': self.user2.id,
            })
        response = self.client.get(url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count)
        self.assertEqual(member_after_count, member_before_count)
        response_url = reverse('user_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_page.html')

    def test_set_member_with_invalid_user_id(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        url = reverse('set_member', kwargs={
                'club_id': self.club.id,
                'user_id': self.user2.id+9999,
            })
        response = self.client.get(url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count)
        self.assertEqual(member_after_count, member_before_count)
        response_url = reverse('member_list', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'member_list.html')

    def test_set_officer_to_member_with_member_membership(self):
        user4 = User.objects.get(email = 'test4@example.org')
        Membership.objects.create(
            club = self.club,
            member = user4,
            member_first_name = 'first_name1',
            member_last_name = 'last_name1',
            member_contact_details = '0712345678',
            member_personal_statement = 'My personal statement',
            member_bio =  'my bio',
            member_chess_experience_level = 0,
            member_type = 1
        )
        self.client.login(email = 'test4@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        applicant_before_count = Membership.objects.filter(member_type=0).count()
        member_before_count = Membership.objects.filter(member_type=1).count()
        url = reverse('set_member', kwargs={
                'club_id': self.club.id,
                'user_id': self.user.id,
            })
        response = self.client.get(url,follow=True)
        applicant_after_count = Membership.objects.filter(member_type=0).count()
        member_after_count = Membership.objects.filter(member_type=1).count()
        self.assertEqual(applicant_after_count, applicant_before_count)
        self.assertEqual(member_after_count, member_before_count)
        response_url = reverse('member_list', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'member_list.html')
