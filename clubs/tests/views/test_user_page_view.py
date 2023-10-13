from clubs.models import User
from django.test import TestCase
from django.urls import reverse
from clubs.tests.helpers import LogInTester,reverse_with_next

class UserPageViewTestCase(TestCase,LogInTester):
    """Tests of the user page view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('user_page')
        self.user = User.objects.get(email = 'test1@example.org')

    def test_user_page_url(self):
        self.assertEqual(self.url,'/user_page/')

    def test_get_user_page(self):
        self.client.login(email = 'test1@example.org', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_page.html')

    def test_get_user_page_when_not_logged_in(self):
        self.assertFalse(self._is_logged_in())
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    
