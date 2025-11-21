"""
Tests for common exceptions.
"""
import unittest
from common.exceptions import (
    ServiceException,
    UserNotFoundError,
    AuthenticationError,
    PermissionDeniedError,
    ContentNotFoundError,
    FileOperationError,
    AIServiceError,
    NotificationError,
)


class TestExceptions(unittest.TestCase):
    """Test exception classes"""

    def test_service_exception_is_base(self):
        """Test that ServiceException is the base exception"""
        self.assertTrue(issubclass(UserNotFoundError, ServiceException))
        self.assertTrue(issubclass(AuthenticationError, ServiceException))
        self.assertTrue(issubclass(PermissionDeniedError, ServiceException))

    def test_user_not_found_error(self):
        """Test UserNotFoundError can be raised and caught"""
        with self.assertRaises(UserNotFoundError):
            raise UserNotFoundError("User not found")
        
        try:
            raise UserNotFoundError("User not found")
        except ServiceException as e:
            self.assertIsInstance(e, UserNotFoundError)
            self.assertEqual(str(e), "User not found")

    def test_authentication_error(self):
        """Test AuthenticationError can be raised and caught"""
        with self.assertRaises(AuthenticationError):
            raise AuthenticationError("Authentication failed")
        
        try:
            raise AuthenticationError("Invalid credentials")
        except ServiceException as e:
            self.assertIsInstance(e, AuthenticationError)

    def test_permission_denied_error(self):
        """Test PermissionDeniedError can be raised and caught"""
        with self.assertRaises(PermissionDeniedError):
            raise PermissionDeniedError("Permission denied")
        
        try:
            raise PermissionDeniedError("Insufficient permissions")
        except ServiceException as e:
            self.assertIsInstance(e, PermissionDeniedError)

    def test_content_not_found_error(self):
        """Test ContentNotFoundError can be raised and caught"""
        with self.assertRaises(ContentNotFoundError):
            raise ContentNotFoundError("Content not found")
        
        try:
            raise ContentNotFoundError("Question not found")
        except ServiceException as e:
            self.assertIsInstance(e, ContentNotFoundError)

    def test_file_operation_error(self):
        """Test FileOperationError can be raised and caught"""
        with self.assertRaises(FileOperationError):
            raise FileOperationError("File operation failed")
        
        try:
            raise FileOperationError("Failed to upload file")
        except ServiceException as e:
            self.assertIsInstance(e, FileOperationError)

    def test_ai_service_error(self):
        """Test AIServiceError can be raised and caught"""
        with self.assertRaises(AIServiceError):
            raise AIServiceError("AI service error")
        
        try:
            raise AIServiceError("AI API timeout")
        except ServiceException as e:
            self.assertIsInstance(e, AIServiceError)

    def test_notification_error(self):
        """Test NotificationError can be raised and caught"""
        with self.assertRaises(NotificationError):
            raise NotificationError("Notification failed")
        
        try:
            raise NotificationError("Failed to send notification")
        except ServiceException as e:
            self.assertIsInstance(e, NotificationError)


if __name__ == '__main__':
    unittest.main()

