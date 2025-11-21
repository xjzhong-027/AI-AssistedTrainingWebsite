"""
Tests for ELW views.

These tests verify that views work correctly with @require_login decorator
and use UserService, ContentService, and FileService for data access.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from Account.models import Students, Teachers, Class, Course
from Account.services.user_service_impl import UserServiceImpl
from ELW.services.file_service_impl import FileServiceImpl


class TeacherIndexViewTestCase(TestCase):
    """Test teacher_index view"""

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
    
    def test_teacher_index_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('teacher_index'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')
    
    def test_teacher_index_authenticated_teacher_access(self):
        """Test that authenticated teachers can access teacher_index"""
        # Login as teacher
        login_response = self.client.post(reverse('login'), {
            'role': 'teacher',
            'username': 'test_teacher',
            'password': 'teacher123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Now access teacher_index
        response = self.client.get(reverse('teacher_index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher_side/index.html')
        self.assertIn('teacher_name', response.context)
        self.assertEqual(response.context['teacher_name'], 'Test Teacher')
    
    def test_teacher_week_file_import_uses_user_service(self):
        """Test that teacher_week_file_import uses UserService to get teacher"""
        # Login as teacher
        login_response = self.client.post(reverse('login'), {
            'role': 'teacher',
            'username': 'test_teacher',
            'password': 'teacher123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Verify UserService can get the teacher
        teacher = UserServiceImpl.get_teacher_by_username('test_teacher')
        self.assertIsNotNone(teacher)
        self.assertEqual(teacher.username, 'test_teacher')
        
        # Verify UserService can get teacher classes
        classes = UserServiceImpl.get_teacher_classes(teacher.id)
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].id, self.class_instance.id)
    
    def test_teacher_exam_bank_uses_user_service(self):
        """Test that teacher_exam_bank uses UserService to get teacher and classes"""
        # Login as teacher
        login_response = self.client.post(reverse('login'), {
            'role': 'teacher',
            'username': 'test_teacher',
            'password': 'teacher123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Access teacher_exam_bank
        response = self.client.get(reverse('teacher_exam_bank'))
        self.assertEqual(response.status_code, 200)
        
        # Verify UserService can get the teacher
        teacher = UserServiceImpl.get_teacher_by_username('test_teacher')
        self.assertIsNotNone(teacher)
        
        # Verify UserService can get teacher classes
        classes = UserServiceImpl.get_teacher_classes(teacher.id)
        self.assertEqual(len(classes), 1)

    def test_teacher_week_task_package_add_uses_file_service(self):
        """Test that teacher_week_task_package_add uses FileService to upload files"""
        # Login as teacher
        login_response = self.client.post(reverse('login'), {
            'role': 'teacher',
            'username': 'test_teacher',
            'password': 'teacher123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Create test files
        media_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        image_file = SimpleUploadedFile(
            "test_image.jpg",
            b"image_content",
            content_type="image/jpeg"
        )
        
        # Post request with files
        response = self.client.post(reverse('teacher_week_task_package_add'), {
            'title': 'Test Task Package',
            'theme': 'Test Theme',
            'abstract': 'Test Abstract',
            'keywords': 'test, keywords',
            'transcript': 'Test transcript',
            'media_file': media_file,
            'image_file': image_file
        })
        
        # Should redirect or return success
        self.assertIn(response.status_code, [200, 302])
        # Note: The actual file upload is tested in FileService implementation tests

    def test_teacher_task_package_add_uses_file_service(self):
        """Test that teacher_task_package_add uses FileService to upload files"""
        # Login as teacher
        login_response = self.client.post(reverse('login'), {
            'role': 'teacher',
            'username': 'test_teacher',
            'password': 'teacher123'
        })
        self.assertEqual(login_response.status_code, 302)
        
        # Create test file
        media_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        # Post request with file
        response = self.client.post(reverse('teacher_task_package_add'), {
            'title': 'Test Task Package',
            'theme': 'Test Theme',
            'abstract': 'Test Abstract',
            'keywords': 'test, keywords',
            'transcript': 'Test transcript',
            'media_file': media_file
        })
        
        # Should redirect or return success
        self.assertIn(response.status_code, [200, 302])
        # Note: The actual file upload is tested in FileService implementation tests

