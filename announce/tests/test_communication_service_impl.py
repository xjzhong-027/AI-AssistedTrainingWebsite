"""
Tests for CommunicationService implementation (announce part).

These tests verify that CommunicationServiceImpl correctly implements the CommunicationService interface
for announcement-related functionality (Announcement, Message).
"""
from django.test import TestCase
from django.contrib.auth.models import User
from Account.models import Students, Teachers, Class, Course
from announce.models import Announcement, Message
from announce.services.communication_service_impl import CommunicationServiceImpl
from Account.services.user_service_impl import UserServiceImpl


class CommunicationServiceImplAnnounceTestCase(TestCase):
    """Test CommunicationService implementation for announcement functionality"""

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
        
        # Create test students
        self.student1_user = User.objects.create_user(
            username='test_student1_user',
            password='student123'
        )
        self.student1 = Students.objects.create(
            username='test_student1',
            name='Test Student 1',
            password='student123',
            class_instance=self.class_instance,
            user=self.student1_user
        )
        
        self.student2_user = User.objects.create_user(
            username='test_student2_user',
            password='student123'
        )
        self.student2 = Students.objects.create(
            username='test_student2',
            name='Test Student 2',
            password='student123',
            class_instance=self.class_instance,
            user=self.student2_user
        )

    def test_create_announcement_success(self):
        """Test creating an announcement successfully"""
        announcement = CommunicationServiceImpl.create_announcement(
            title='Test Announcement',
            content='Test content',
            teacher_id=self.teacher.id
        )
        
        self.assertIsNotNone(announcement)
        self.assertEqual(announcement.a_title, 'Test Announcement')
        self.assertEqual(announcement.a_content, 'Test content')
        self.assertEqual(announcement.teachers, self.teacher)

    def test_create_announcement_with_receivers(self):
        """Test creating an announcement with specific receivers"""
        announcement = CommunicationServiceImpl.create_announcement(
            title='Test Announcement',
            content='Test content',
            teacher_id=self.teacher.id,
            receiver_student_ids=[self.student1.id, self.student2.id]
        )
        
        self.assertIsNotNone(announcement)
        self.assertEqual(announcement.receivers.count(), 2)
        self.assertIn(self.student1, announcement.receivers.all())
        self.assertIn(self.student2, announcement.receivers.all())

    def test_create_announcement_no_receivers(self):
        """Test creating an announcement without receivers"""
        announcement = CommunicationServiceImpl.create_announcement(
            title='Test Announcement',
            content='Test content',
            teacher_id=self.teacher.id,
            receiver_student_ids=None
        )
        
        self.assertIsNotNone(announcement)
        self.assertEqual(announcement.receivers.count(), 0)

    def test_get_announcements_for_student_success(self):
        """Test getting announcements for a student"""
        # Create announcements
        announcement1 = CommunicationServiceImpl.create_announcement(
            title='Announcement 1',
            content='Content 1',
            teacher_id=self.teacher.id,
            receiver_student_ids=[self.student1.id]
        )
        announcement2 = CommunicationServiceImpl.create_announcement(
            title='Announcement 2',
            content='Content 2',
            teacher_id=self.teacher.id,
            receiver_student_ids=[self.student1.id, self.student2.id]
        )
        announcement3 = CommunicationServiceImpl.create_announcement(
            title='Announcement 3',
            content='Content 3',
            teacher_id=self.teacher.id,
            receiver_student_ids=[self.student2.id]
        )
        
        announcements = CommunicationServiceImpl.get_announcements_for_student(
            student_id=self.student1.id
        )
        
        self.assertEqual(len(announcements), 2)
        self.assertIn(announcement1, announcements)
        self.assertIn(announcement2, announcements)
        self.assertNotIn(announcement3, announcements)

    def test_get_announcements_for_student_no_announcements(self):
        """Test getting announcements for a student with no announcements"""
        announcements = CommunicationServiceImpl.get_announcements_for_student(
            student_id=self.student1.id
        )
        
        self.assertEqual(len(announcements), 0)

    def test_send_message_success(self):
        """Test sending a message successfully"""
        message = CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Test message',
            message_type='private'
        )
        
        self.assertIsNotNone(message)
        self.assertEqual(message.sender, 'test_teacher')
        self.assertEqual(message.receiver, 'test_student1')
        self.assertEqual(message.content, 'Test message')
        self.assertFalse(message.is_read)

    def test_send_message_multiple_messages(self):
        """Test sending multiple messages"""
        message1 = CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Message 1'
        )
        message2 = CommunicationServiceImpl.send_message(
            sender_username='test_student1',
            receiver_username='test_teacher',
            content='Message 2'
        )
        
        self.assertIsNotNone(message1)
        self.assertIsNotNone(message2)
        self.assertEqual(message1.sender, 'test_teacher')
        self.assertEqual(message2.sender, 'test_student1')

    def test_send_message_default_type(self):
        """Test sending a message with default type"""
        message = CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Test message'
        )
        
        self.assertIsNotNone(message)
        self.assertEqual(message.sender, 'test_teacher')
        self.assertEqual(message.receiver, 'test_student1')
        self.assertEqual(message.content, 'Test message')

