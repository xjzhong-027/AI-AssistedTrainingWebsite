"""
Tests for AuthService implementation.

These tests verify that AuthServiceImpl correctly implements the AuthService interface.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from Account.models import Students, Teachers, Admins, LoginInfo, Class, Course, Attendance
from Account.services.auth_service_impl import AuthServiceImpl
from common.exceptions import AuthenticationError, UserNotFoundError


class AuthServiceImplTestCase(TestCase):
    """Test AuthService implementation"""

    def setUp(self):
        """Set up test data"""
        # Create test course
        self.course = Course.objects.create(
            year=2024,
            grade=1,
            semester=1
        )
        
        # Create test teacher
        self.teacher = Teachers.objects.create(
            username='test_teacher',
            name='Test Teacher',
            password='teacher123'
        )
        self.teacher_user = User.objects.create_user(
            username='test_teacher',
            password='teacher123'
        )
        self.teacher.user = self.teacher_user
        self.teacher.save()
        
        # Create test class
        self.class_instance = Class.objects.create(
            course=self.course,
            teacher=self.teacher,
            start_date='2024-01-01',
            week=1,
            start_time='08:00:00',
            end_time='10:00:00'
        )
        
        # Create test student
        self.student_user = User.objects.create_user(
            username='test_student',
            password='student123'
        )
        self.student = Students.objects.create(
            username='test_student',
            name='Test Student',
            password='student123',
            class_instance=self.class_instance
        )
        self.student.user = self.student_user
        self.student.save()
        
        # Create test admin
        self.admin = Admins.objects.create(
            username='test_admin',
            password='admin123'
        )

    def test_authenticate_student_success(self):
        """Test successful student authentication"""
        result = AuthServiceImpl.authenticate_student('test_student', 'student123')
        self.assertIsNotNone(result)
        self.assertIn('student', result)
        self.assertIn('user', result)
        self.assertEqual(result['student'], self.student)
        self.assertEqual(result['user'], self.student_user)

    def test_authenticate_student_failure_wrong_password(self):
        """Test student authentication with wrong password"""
        result = AuthServiceImpl.authenticate_student('test_student', 'wrong_password')
        self.assertIsNone(result)

    def test_authenticate_student_failure_not_exists(self):
        """Test student authentication with non-existent username"""
        result = AuthServiceImpl.authenticate_student('nonexistent', 'password')
        self.assertIsNone(result)

    def test_authenticate_teacher_success(self):
        """Test successful teacher authentication"""
        result = AuthServiceImpl.authenticate_teacher('test_teacher', 'teacher123')
        self.assertIsNotNone(result)
        self.assertIn('teacher', result)
        self.assertIn('user', result)
        self.assertEqual(result['teacher'], self.teacher)
        self.assertEqual(result['user'], self.teacher_user)

    def test_authenticate_teacher_failure_wrong_password(self):
        """Test teacher authentication with wrong password"""
        result = AuthServiceImpl.authenticate_teacher('test_teacher', 'wrong_password')
        self.assertIsNone(result)

    def test_authenticate_admin_success(self):
        """Test successful admin authentication"""
        result = AuthServiceImpl.authenticate_admin('test_admin', 'admin123')
        self.assertIsNotNone(result)
        self.assertIn('admin', result)
        self.assertEqual(result['admin'], self.admin)

    def test_authenticate_admin_failure_not_exists(self):
        """Test admin authentication with non-existent username"""
        result = AuthServiceImpl.authenticate_admin('nonexistent', 'password')
        self.assertIsNone(result)

    def test_create_login_record(self):
        """Test creating login record"""
        client = Client()
        request = client.get('/login/').wsgi_request
        
        login_record = AuthServiceImpl.create_login_record('test_student', 'student', request)
        self.assertIsNotNone(login_record)
        self.assertEqual(login_record.username, 'test_student')
        self.assertEqual(login_record.action, 'login')
        self.assertIsNotNone(login_record.action_time)
        self.assertEqual(login_record.week, 0)  # 默认值为0
        self.assertIsNotNone(login_record.device_info)

    def test_update_last_activity(self):
        """Test updating last activity"""
        client = Client()
        request = client.get('/login/').wsgi_request
        request.session['is_login'] = True
        request.session['username'] = 'test_student'
        
        # Should not raise exception
        AuthServiceImpl.update_last_activity('test_student', request)
        self.assertIn('last_active_time', request.session)

    def test_is_authenticated_true(self):
        """Test is_authenticated returns True for logged in user"""
        client = Client()
        request = client.get('/login/').wsgi_request
        request.session['is_login'] = True
        request.session['username'] = 'test_student'
        
        result = AuthServiceImpl.is_authenticated(request)
        self.assertTrue(result)

    def test_is_authenticated_false(self):
        """Test is_authenticated returns False for not logged in user"""
        client = Client()
        request = client.get('/login/').wsgi_request
        
        result = AuthServiceImpl.is_authenticated(request)
        self.assertFalse(result)

    def test_get_current_user_logged_in(self):
        """Test get_current_user for logged in student"""
        client = Client()
        request = client.get('/login/').wsgi_request
        request.session['is_login'] = True
        request.session['username'] = 'test_student'
        request.session['role'] = 'student'
        
        result = AuthServiceImpl.get_current_user(request)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'test_student')
        self.assertEqual(result['role'], 'student')

    def test_get_current_user_not_logged_in(self):
        """Test get_current_user for not logged in user"""
        client = Client()
        request = client.get('/login/').wsgi_request
        
        result = AuthServiceImpl.get_current_user(request)
        self.assertIsNone(result)


class RequireLoginDecoratorTestCase(TestCase):
    """Test require_login decorator"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

    def test_require_login_redirects_when_not_logged_in(self):
        """Test that require_login decorator redirects to login when not logged in"""
        from Account.services.auth_service_impl import AuthServiceImpl
        
        @AuthServiceImpl.require_login
        def test_view(request):
            return 'success'
        
        request = self.client.get('/login/').wsgi_request
        response = test_view(request)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    def test_require_login_allows_when_logged_in(self):
        """Test that require_login decorator allows access when logged in"""
        from Account.services.auth_service_impl import AuthServiceImpl
        
        @AuthServiceImpl.require_login
        def test_view(request):
            from django.http import HttpResponse
            return HttpResponse('success')
        
        request = self.client.get('/login/').wsgi_request
        request.session['is_login'] = True
        request.session['username'] = 'test_user'
        
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'success')

