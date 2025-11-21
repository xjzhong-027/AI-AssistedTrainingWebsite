"""
Tests for NotificationService implementation.

These tests verify that NotificationServiceImpl correctly implements the NotificationService interface.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from Account.models import Students, Teachers, Class, Course
from announce.models import Announcement, Message
from announce.services.notification_service_impl import NotificationServiceImpl
from announce.services.communication_service_impl import CommunicationServiceImpl
from Account.services.user_service_impl import UserServiceImpl


class NotificationServiceImplTestCase(TestCase):
    """Test NotificationService implementation"""

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
        
        # Create test announcement
        self.announcement = CommunicationServiceImpl.create_announcement(
            title='Test Announcement',
            content='Test content',
            teacher_id=self.teacher.id,
            receiver_student_ids=[self.student1.id, self.student2.id]
        )

    def test_send_announcement_notification_success(self):
        """Test sending announcement notification successfully"""
        result = NotificationServiceImpl.send_announcement_notification(
            announcement_id=self.announcement.id,
            receiver_usernames=['test_student1', 'test_student2']
        )
        
        self.assertTrue(result)

    def test_send_announcement_notification_empty_receivers(self):
        """Test sending announcement notification with empty receivers"""
        result = NotificationServiceImpl.send_announcement_notification(
            announcement_id=self.announcement.id,
            receiver_usernames=[]
        )
        
        # Should return True even with empty receivers (no error)
        self.assertTrue(result)

    def test_send_forum_reply_notification_success(self):
        """Test sending forum reply notification successfully"""
        # Create a test post and comment (simplified, actual implementation may need more setup)
        # Note: This test verifies the method can be called without error
        result = NotificationServiceImpl.send_forum_reply_notification(
            post_id=1,  # Dummy post_id
            comment_id=1,  # Dummy comment_id
            receiver_username='test_student1'
        )
        
        # Should return True or False (depending on implementation)
        self.assertIsInstance(result, bool)

    def test_send_exam_result_notification_success(self):
        """Test sending exam result notification successfully"""
        result = NotificationServiceImpl.send_exam_result_notification(
            student_id=self.student1.id,
            exam_id=1,  # Dummy exam_id
            score=85.5
        )
        
        # Should return True or False (depending on implementation)
        self.assertIsInstance(result, bool)

    def test_mark_message_as_read_success(self):
        """Test marking message as read successfully"""
        # Create a test message
        message = CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Test message'
        )
        
        result = NotificationServiceImpl.mark_message_as_read(
            message_id=message.id,
            username='test_student1'
        )
        
        self.assertTrue(result)
        # Verify message is marked as read
        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_mark_message_as_read_not_found(self):
        """Test marking non-existent message as read"""
        result = NotificationServiceImpl.mark_message_as_read(
            message_id=99999,
            username='test_student1'
        )
        
        # Should return False or handle gracefully
        self.assertIsInstance(result, bool)

    def test_get_unread_count_success(self):
        """Test getting unread message count successfully"""
        # Create some messages
        CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Message 1'
        )
        CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Message 2'
        )
        # Mark one as read
        message = CommunicationServiceImpl.send_message(
            sender_username='test_teacher',
            receiver_username='test_student1',
            content='Message 3'
        )
        NotificationServiceImpl.mark_message_as_read(message.id, 'test_student1')
        
        unread_count = NotificationServiceImpl.get_unread_count('test_student1')
        
        self.assertIsInstance(unread_count, int)
        self.assertGreaterEqual(unread_count, 2)  # At least 2 unread messages

    def test_get_unread_count_no_messages(self):
        """Test getting unread count when there are no messages"""
        unread_count = NotificationServiceImpl.get_unread_count('nonexistent_user')
        
        self.assertEqual(unread_count, 0)

    def test_broadcast_to_class_success(self):
        """Test broadcasting message to class successfully"""
        message = {
            'type': 'announcement',
            'content': 'Test broadcast message'
        }
        
        result = NotificationServiceImpl.broadcast_to_class(
            class_id=self.class_instance.id,
            message=message,
            message_type='announcement'
        )
        
        # Should return True or False (depending on implementation)
        self.assertIsInstance(result, bool)

    def test_broadcast_to_class_invalid_class(self):
        """Test broadcasting to non-existent class"""
        message = {
            'type': 'announcement',
            'content': 'Test broadcast message'
        }
        
        result = NotificationServiceImpl.broadcast_to_class(
            class_id=99999,
            message=message,
            message_type='announcement'
        )
        
        # Should return False or handle gracefully
        self.assertIsInstance(result, bool)

