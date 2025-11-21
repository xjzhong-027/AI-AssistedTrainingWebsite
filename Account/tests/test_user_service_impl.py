"""
Tests for UserService implementation.

These tests verify that UserServiceImpl correctly implements the UserService interface.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from Account.models import Students, Teachers, Class, Course, Attendance
from Account.services.user_service_impl import UserServiceImpl
from common.exceptions import UserNotFoundError


class UserServiceImplTestCase(TestCase):
    """Test UserService implementation"""

    def setUp(self):
        """Set up test data"""
        # Create test course
        self.course = Course.objects.create(
            year=2024,
            grade=1,
            semester=1
        )
        
        # Create test teacher
        self.teacher_user = User.objects.create_user(
            username='test_teacher_user',
            password='teacher123'
        )
        self.teacher = Teachers.objects.create(
            username='test_teacher',
            name='Test Teacher',
            password='teacher123',
            user=self.teacher_user
        )
        
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
            username='test_student_user',
            password='student123'
        )
        self.student = Students.objects.create(
            class_instance=self.class_instance,
            username='test_student',
            name='Test Student',
            password='student123',
            user=self.student_user
        )
        
        # Create initial attendance for student
        Attendance.objects.create(
            student=self.student,
            week=0,
            status='absent'
        )

    def test_get_student_by_username_success(self):
        """Test successful retrieval of student by username"""
        student = UserServiceImpl.get_student_by_username('test_student')
        self.assertIsNotNone(student)
        self.assertEqual(student.username, 'test_student')
        self.assertEqual(student.name, 'Test Student')

    def test_get_student_by_username_not_found(self):
        """Test retrieval of non-existent student"""
        student = UserServiceImpl.get_student_by_username('nonexistent')
        self.assertIsNone(student)

    def test_get_teacher_by_username_success(self):
        """Test successful retrieval of teacher by username"""
        teacher = UserServiceImpl.get_teacher_by_username('test_teacher')
        self.assertIsNotNone(teacher)
        self.assertEqual(teacher.username, 'test_teacher')
        self.assertEqual(teacher.name, 'Test Teacher')

    def test_get_teacher_by_username_not_found(self):
        """Test retrieval of non-existent teacher"""
        teacher = UserServiceImpl.get_teacher_by_username('nonexistent')
        self.assertIsNone(teacher)

    def test_get_student_by_id_success(self):
        """Test successful retrieval of student by ID"""
        student = UserServiceImpl.get_student_by_id(self.student.id)
        self.assertIsNotNone(student)
        self.assertEqual(student.id, self.student.id)
        self.assertEqual(student.username, 'test_student')

    def test_get_student_by_id_not_found(self):
        """Test retrieval of non-existent student by ID"""
        student = UserServiceImpl.get_student_by_id(99999)
        self.assertIsNone(student)

    def test_get_teacher_by_id_success(self):
        """Test successful retrieval of teacher by ID"""
        teacher = UserServiceImpl.get_teacher_by_id(self.teacher.id)
        self.assertIsNotNone(teacher)
        self.assertEqual(teacher.id, self.teacher.id)
        self.assertEqual(teacher.username, 'test_teacher')

    def test_get_teacher_by_id_not_found(self):
        """Test retrieval of non-existent teacher by ID"""
        teacher = UserServiceImpl.get_teacher_by_id(99999)
        self.assertIsNone(teacher)

    def test_get_student_class_success(self):
        """Test successful retrieval of student's class"""
        class_obj = UserServiceImpl.get_student_class(self.student.id)
        self.assertIsNotNone(class_obj)
        self.assertEqual(class_obj.id, self.class_instance.id)

    def test_get_student_class_student_not_found(self):
        """Test retrieval of class for non-existent student"""
        class_obj = UserServiceImpl.get_student_class(99999)
        self.assertIsNone(class_obj)

    def test_get_teacher_classes_success(self):
        """Test successful retrieval of teacher's classes"""
        classes = UserServiceImpl.get_teacher_classes(self.teacher.id)
        self.assertIsNotNone(classes)
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].id, self.class_instance.id)

    def test_get_teacher_classes_empty(self):
        """Test retrieval of classes for teacher with no classes"""
        # Create a teacher with no classes
        teacher2 = Teachers.objects.create(
            username='teacher2',
            name='Teacher 2',
            password='password'
        )
        classes = UserServiceImpl.get_teacher_classes(teacher2.id)
        self.assertIsNotNone(classes)
        self.assertEqual(len(classes), 0)

    def test_get_teacher_classes_teacher_not_found(self):
        """Test retrieval of classes for non-existent teacher"""
        classes = UserServiceImpl.get_teacher_classes(99999)
        self.assertIsNotNone(classes)
        self.assertEqual(len(classes), 0)

    def test_get_class_students_success(self):
        """Test successful retrieval of class students"""
        students = UserServiceImpl.get_class_students(self.class_instance.id)
        self.assertIsNotNone(students)
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].id, self.student.id)

    def test_get_class_students_empty(self):
        """Test retrieval of students for class with no students"""
        # Create a class with no students
        class2 = Class.objects.create(
            course=self.course,
            teacher=self.teacher,
            start_date='2024-01-01',
            week=2,
            start_time='10:00:00',
            end_time='12:00:00'
        )
        students = UserServiceImpl.get_class_students(class2.id)
        self.assertIsNotNone(students)
        self.assertEqual(len(students), 0)

    def test_get_class_students_class_not_found(self):
        """Test retrieval of students for non-existent class"""
        students = UserServiceImpl.get_class_students(99999)
        self.assertIsNotNone(students)
        self.assertEqual(len(students), 0)

