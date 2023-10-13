from django.test import TestCase
from django.urls import reverse
from clubs.forms import MembershipSignUpForm
from clubs.models import User, Club, Membership
from clubs.tests.helpers import LogInTester, reverse_with_next

class MembershipSignUpViewTestCase(TestCase,LogInTester):
    """Tests of the membership sign up view."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json'
            ]

    def setUp(self):
        self.url = reverse('membership_sign_up')
        self.user = User.objects.get(email = 'test1@example.org')
        self.user2 = User.objects.get(email = 'test2@example.org')
        self.club = Club.objects.get(name = 'Test Club')
        self.form_input={
            'member_first_name' : 'first_name1',
            'member_last_name':'last_name1',
            'member_contact_details':'0712345678',
            'member_personal_statement':'My personal statement',
            'member_bio':'my bio',
            'member_chess_experience_level':0,
            'club':'Test Club'
        }

    def test_membership_sign_up_url(self):
        self.assertEqual(self.url,'/membership_sign_up/')

    def test_get_membership_sign_up_when_logged_in(self):
        self.client.login(email = self.user.email, password = "Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'membership_sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MembershipSignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_membership_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse_with_next('log_in',self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_unsuccessful_membership_sign_up(self):
        self.client.login(email = self.user.email, password = "Password123")
        self.assertTrue(self._is_logged_in())
        self.form_input['member_contact_details'] = ''
        before_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'membership_sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MembershipSignUpForm))
        self.assertTrue(form.is_bound)

    def test_successful_membership_sign_up_with_redirects(self):
        self.client.login(email = self.user.email, password = "Password123")
        self.assertTrue(self._is_logged_in())
        before_count = Membership.objects.count()
        response = self.client.post(self.url, self.form_input,follow=True)
        after_count = Membership.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('user_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_page.html')
        membership = Membership.objects.get(member=self.user,club = self.club)
        self.assertEqual(membership.member_first_name,"first_name1")
        self.assertEqual(membership.member_last_name,"last_name1")
        self.assertEqual(membership.member_contact_details,"0712345678")
        self.assertEqual(membership.member_personal_statement,"My personal statement")
        self.assertEqual(membership.member_bio,"my bio")
        self.assertEqual(membership.member_chess_experience_level,0)

    def test_can_not_sign_up_membership_for_others(self):
        self.client.login(email = self.user.email, password = "Password123")
        self.assertTrue(self._is_logged_in())
        self.form_input['user'] = self.user2
        membership_count_before = Membership.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        membership_count_after = Membership.objects.count()
        self.assertEqual(membership_count_after, membership_count_before+1)
        new_membership = Membership.objects.latest('member')
        self.assertEqual(self.user, new_membership.member)
