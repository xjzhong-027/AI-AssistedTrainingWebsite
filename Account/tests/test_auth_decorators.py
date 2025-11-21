"""
Tests for authentication decorators in Account module.

These tests verify that the @require_login decorator works correctly.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from Account.models import Students, Teachers, Class, Course, Attendance
from Account.services.auth_service_impl import AuthServiceImpl
from django.shortcuts import redirect


class RequireLoginDecoratorTestCase(TestCase):
    """Test @require_login decorator"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
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
        
        # Create attendance records
        import datetime
        start_date = datetime.date.fromisoformat(self.class_instance.start_date)
        this_date = datetime.date.today()
        if ((this_date - start_date).days) % 7 == 0:
            week = (this_date - start_date).days // 7
            Attendance.objects.create(
                student=self.student,
                week=week,
                status='absent'
            )
        Attendance.objects.create(
            student=self.student,
            week=0,
            status='absent'
        )
    
    def test_require_login_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected to login page"""
        # Create a test view function with @require_login decorator
        @AuthServiceImpl.require_login
        def protected_view(request):
            return HttpResponse("Protected content")
        
        # Make request without logging in
        response = self.client.get('/some-protected-url/')
        
        # Should redirect to login (status 302)
        # Note: Since we're not using actual URL routing, we'll test the decorator directly
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/protected/')
        request.session = self.client.session
        
        # Unauthenticated request
        request.session['is_login'] = False
        request.session.save()
        
        response = protected_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')
    
    def test_require_login_authenticated_allows_access(self):
        """Test that authenticated users can access protected views"""
        # Create a test view function with @require_login decorator
        @AuthServiceImpl.require_login
        def protected_view(request):
            return HttpResponse("Protected content")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/protected/')
        request.session = self.client.session
        
        # Authenticated request
        request.session['is_login'] = True
        request.session['username'] = 'test_student'
        request.session.save()
        
        response = protected_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Protected content")
    
    def test_require_login_preserves_view_arguments(self):
        """Test that decorator correctly passes arguments to view function"""
        @AuthServiceImpl.require_login
        def protected_view_with_args(request, arg1, arg2=None):
            return HttpResponse(f"Protected: {arg1}, {arg2}")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/protected/')
        request.session = self.client.session
        
        # Authenticated request
        request.session['is_login'] = True
        request.session.save()
        
        response = protected_view_with_args(request, 'value1', arg2='value2')
        self.assertEqual(response.status_code, 200)
        self.assertIn('value1', response.content.decode())
        self.assertIn('value2', response.content.decode())
    
    def test_require_login_preserves_view_kwargs(self):
        """Test that decorator correctly passes keyword arguments to view function"""
        @AuthServiceImpl.require_login
        def protected_view_with_kwargs(request, **kwargs):
            return HttpResponse(f"Protected: {kwargs.get('id', 'no-id')}")
        
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/protected/')
        request.session = self.client.session
        
        # Authenticated request
        request.session['is_login'] = True
        request.session.save()
        
        response = protected_view_with_kwargs(request, id='123')
        self.assertEqual(response.status_code, 200)
        self.assertIn('123', response.content.decode())

