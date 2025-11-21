"""
Tests for URL routing to ensure login-related routes point to Account.views.

This is part of task 2.3: Update URL routing.
"""
from django.test import TestCase, Client
from django.urls import reverse, resolve
from Account import views as account_views


class URLRoutingTestCase(TestCase):
    """Test that login-related URLs route to Account.views"""

    def test_login_url_resolves_to_account_views(self):
        """Test that /login/ routes to Account.views.user_login"""
        url = reverse('login')
        self.assertEqual(url, '/login/')
        
        # Resolve the URL to get the view function
        resolved = resolve('/login/')
        self.assertEqual(resolved.func, account_views.user_login)

    def test_logout_url_resolves_to_account_views(self):
        """Test that /logout/ routes to Account.views.log_out"""
        url = reverse('logout')
        self.assertEqual(url, '/logout/')
        
        # Resolve the URL to get the view function
        resolved = resolve('/logout/')
        self.assertEqual(resolved.func, account_views.log_out)

    def test_update_last_activity_url_resolves_to_account_views(self):
        """Test that /update_last_activity/ routes to Account.views.update_last_activity"""
        url = reverse('update_last_activity')
        self.assertEqual(url, '/update_last_activity/')
        
        # Resolve the URL to get the view function
        resolved = resolve('/update_last_activity/')
        self.assertEqual(resolved.func, account_views.update_last_activity)

    def test_login_url_accessible(self):
        """Test that login URL is accessible via GET request"""
        client = Client()
        response = client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_url_redirects_when_not_logged_in(self):
        """Test that logout URL redirects to login when not logged in"""
        client = Client()
        response = client.get(reverse('logout'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_update_last_activity_url_returns_json(self):
        """Test that update_last_activity URL returns JSON response"""
        client = Client()
        response = client.get(reverse('update_last_activity'))
        # Should return JSON (even if not logged in, it should return status)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

