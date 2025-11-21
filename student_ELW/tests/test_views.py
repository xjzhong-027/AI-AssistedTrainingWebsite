"""
Tests for student_ELW views.

These tests verify that views work correctly with @require_login decorator.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from Account.models import Students, Teachers, Class, Course, Attendance


class StudentIndexViewTestCase(TestCase):
    """Test student_index view"""

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
    
    def test_student_index_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('student_ELW:student_index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')
    
    def test_student_index_authenticated_student_access(self):
        """Test that authenticated students can access student_index"""
        # Login as student
        login_response = self.client.post(reverse('login'), {
            'role': 'student',
            'username': 'test_student',
            'password': 'test123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Now access student_index
        response = self.client.get(reverse('student_ELW:student_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'students/index.html')
        self.assertIn('username', response.context)
        self.assertEqual(response.context['username'], 'test_student')
    
    def test_student_index_authenticated_non_student_redirects(self):
        """Test that authenticated non-students are redirected to login"""
        # Login as teacher
        login_response = self.client.post(reverse('login'), {
            'role': 'teacher',
            'username': 'test_teacher',
            'password': 'teacher123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Try to access student_index (should redirect because role is not 'student')
        response = self.client.get(reverse('student_ELW:student_index'))
        # Note: The view checks role == 'student', so non-students will be redirected
        # This behavior is preserved in the refactored version
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

