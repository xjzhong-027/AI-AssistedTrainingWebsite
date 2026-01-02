"""
Tests for JWT authentication API.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from Account.models import Students, Teachers, Admins, Class, Course
from Account.services.user_service_impl import UserServiceImpl


class JWTAuthTestCase(TestCase):
    """Test JWT authentication API"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test course
        self.course = Course.objects.create(
            year=2024,
            grade='1',
            semester='上'
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
            password='test123'
        )
        self.student = Students.objects.create(
            username='test_student',
            name='Test Student',
            password='test123',
            class_instance=self.class_instance
        )
        self.student.user = self.student_user
        self.student.save()
        
        # Create test admin
        self.admin = Admins.objects.create(
            username='test_admin',
            password='admin123'
        )
        self.admin_user = User.objects.create_user(
            username='test_admin',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        self.admin.user = self.admin_user
        self.admin.save()
    
    def test_student_login_success(self):
        """Test successful student login"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_student',
            'password': 'test123',
            'role': 'student'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['username'], 'test_student')
        self.assertEqual(response.data['data']['role'], 'student')
        self.assertEqual(response.data['data']['user_id'], self.student.id)
    
    def test_student_login_invalid_password(self):
        """Test student login with invalid password"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_student',
            'password': 'wrong_password',
            'role': 'student'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 401)
    
    def test_student_login_missing_role(self):
        """Test student login without role"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_student',
            'password': 'test123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 400)
    
    def test_teacher_login_success(self):
        """Test successful teacher login"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_teacher',
            'password': 'teacher123',
            'role': 'teacher'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['username'], 'test_teacher')
        self.assertEqual(response.data['data']['role'], 'teacher')
        self.assertEqual(response.data['data']['user_id'], self.teacher.id)
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_admin',
            'password': 'admin123',
            'role': 'admin'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['username'], 'test_admin')
        self.assertEqual(response.data['data']['role'], 'admin')
        self.assertEqual(response.data['data']['user_id'], self.admin.id)
    
    def test_token_refresh(self):
        """Test token refresh"""
        # First login to get tokens
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_student',
            'password': 'test123',
            'role': 'student'
        }, format='json')
        
        refresh_token = login_response.data['data']['refresh']
        
        # Refresh token
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertIn('access', response.data['data'])
    
    def test_get_current_user(self):
        """Test get current user info"""
        # First login to get token
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_student',
            'password': 'test123',
            'role': 'student'
        }, format='json')
        
        # Debug: Check login response
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('data', login_response.data)
        self.assertIn('access', login_response.data['data'])
        
        access_token = login_response.data['data']['access']
        self.assertIsNotNone(access_token)
        self.assertIsInstance(access_token, str)
        
        # Debug: Print token for debugging
        print(f"\n=== Debug Info ===")
        print(f"Login response status: {login_response.status_code}")
        print(f"Access token length: {len(access_token)}")
        print(f"Access token preview: {access_token[:50]}...")
        
        # Get current user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/v1/auth/user/')
        
        # Debug: Print response for debugging
        print(f"User response status: {response.status_code}")
        print(f"User response data: {response.data}")
        print(f"==================\n")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['username'], 'test_student')
        self.assertEqual(response.data['data']['role'], 'student')
    
    def test_logout(self):
        """Test logout"""
        # First login to get token
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'test_student',
            'password': 'test123',
            'role': 'student'
        }, format='json')
        
        access_token = login_response.data['data']['access']
        refresh_token = login_response.data['data']['refresh']
        
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/v1/auth/logout/', {
            'refresh_token': refresh_token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)

