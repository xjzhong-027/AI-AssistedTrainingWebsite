"""
Tests for LoginInfo model in Account module.

These tests verify that LoginInfo model works correctly after migration from ELW.
"""
from django.test import TestCase
from django.utils import timezone
from Account.models import LoginInfo


class LoginInfoModelTestCase(TestCase):
    """Test LoginInfo model"""

    def test_create_login_info(self):
        """Test creating a LoginInfo record"""
        login_info = LoginInfo.objects.create(
            username='test_user',
            week=1,
            action='login',
            action_time=timezone.now(),
            last_active_time='',
            device_info='Test Device'
        )
        
        self.assertIsNotNone(login_info)
        self.assertEqual(login_info.username, 'test_user')
        self.assertEqual(login_info.week, 1)
        self.assertEqual(login_info.action, 'login')
        self.assertIsNotNone(login_info.action_time)

    def test_login_info_str(self):
        """Test LoginInfo string representation"""
        login_info = LoginInfo.objects.create(
            username='test_user',
            week=1,
            action='login',
            action_time=timezone.now(),
            last_active_time='',
            device_info='Test Device'
        )
        
        # Should have a string representation
        str_repr = str(login_info)
        self.assertIsNotNone(str_repr)

    def test_login_info_fields(self):
        """Test that LoginInfo has all required fields"""
        login_info = LoginInfo(
            username='test_user',
            week=1,
            action='login',
            action_time=timezone.now(),
            last_active_time='',
            device_info='Test Device'
        )
        
        # Verify all fields exist
        self.assertEqual(login_info.username, 'test_user')
        self.assertEqual(login_info.week, 1)
        self.assertEqual(login_info.action, 'login')
        self.assertIsNotNone(login_info.action_time)
        self.assertEqual(login_info.last_active_time, '')
        self.assertEqual(login_info.device_info, 'Test Device')

    def test_login_info_query(self):
        """Test querying LoginInfo records"""
        # Create multiple records
        LoginInfo.objects.create(
            username='user1',
            week=1,
            action='login',
            action_time=timezone.now(),
            last_active_time='',
            device_info='Device1'
        )
        LoginInfo.objects.create(
            username='user2',
            week=1,
            action='login',
            action_time=timezone.now(),
            last_active_time='',
            device_info='Device2'
        )
        
        # Query by username
        user1_logins = LoginInfo.objects.filter(username='user1')
        self.assertEqual(user1_logins.count(), 1)
        
        # Query all
        all_logins = LoginInfo.objects.all()
        self.assertEqual(all_logins.count(), 2)

