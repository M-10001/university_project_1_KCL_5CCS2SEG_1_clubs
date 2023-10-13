from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.forms import ApplicationEditForm
from clubs.tests.helpers import LogInTester, reverse_with_next

class ApplicationEditViewTestCase(TestCase,LogInTester):
    """Tests of the application edit view."""

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
            member_type = 0
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
            member_type = 3
        )
        self.form_input = {
            'member_first_name' : 'firstname111',
            'member_last_name':'lastname111',
            'member_contact_details':'00002222222',
            'member_personal_statement':'Something random',
            'member_bio':'random bio',
            'member_chess_experience_level':2,
        }
        self.url = reverse('application_edit', kwargs={'club_id': self.club.id})

    def test_application_url(self):
        self.assertEqual(self.url,f'/application_edit/{self.club.id}/')

    def test_get_application_edit(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_edit.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplicationEditForm))
        self.assertFalse(form.is_bound)

    def test_post_unsuccessful_application_edit(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        self.form_input['member_chess_experience_level'] = -1
        response = self.client.post(self.url,self.form_input,follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_edit.html')
        form = response.context['form']
        membership = Membership.objects.get(club=self.club, member = self.user)
        self.assertEqual(membership.member_chess_experience_level,0)
        self.assertTrue(isinstance(form, ApplicationEditForm))
        self.assertTrue(form.is_bound)

    def test_edit_application_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url,self.form_input,follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_without_membership(self):
        user3 = User.objects.get(email = 'test3@example.org')
        self.client.login(email = 'test3@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url,self.form_input,follow=True)
        redirect_url = reverse('user_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_applicaiton_with_invalid_club_id(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        url = reverse('application_edit', kwargs={'club_id': self.club.id+9999})
        response = self.client.post(url,self.form_input,follow=True)
        membership = Membership.objects.get(club=self.club, member = self.user)
        self.assertEqual(membership.member_first_name,"first_name1")
        self.assertEqual(membership.member_last_name,"last_name1")
        self.assertEqual(membership.member_contact_details,"0712345678")
        self.assertEqual(membership.member_personal_statement,"My personal statement")
        self.assertEqual(membership.member_bio,"my bio")
        self.assertEqual(membership.member_chess_experience_level,0)
        redirect_url = reverse('user_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_with_member_membership(self):
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
            member_type = 1
        )
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url,self.form_input,follow=True)
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_successful_edit_applicaiton(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.post(self.url,self.form_input,follow=True)
        membership = Membership.objects.get(club=self.club, member = self.user)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.assertEqual(membership.member_first_name,"firstname111")
        self.assertEqual(membership.member_last_name,"lastname111")
        self.assertEqual(membership.member_contact_details,"00002222222")
        self.assertEqual(membership.member_personal_statement,"Something random")
        self.assertEqual(membership.member_bio,"random bio")
        self.assertEqual(membership.member_chess_experience_level,2)
        redirect_url = reverse('club_page', kwargs = {'club_id' : self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
