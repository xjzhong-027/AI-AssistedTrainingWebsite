"""
Service interfaces for inter-module communication.

This package contains service interface definitions that modules should use
to communicate with each other, instead of directly importing models.

Available services:
- UserService: User information access
- AuthService: Authentication and authorization
- ContentService: Content (questions, media) access
- ExamService: Exam/practice functionality
- CommunicationService: Forum, announcement, messaging
- AIService: AI functionality
- FileService: File upload and storage
- NotificationService: Real-time notifications
- LogService: Operation logging
- DataService: Data query and statistics
"""

# Import all service interfaces for easy access
from common.services.user_service import UserService
from common.services.auth_service import AuthService
from common.services.content_service import ContentService
from common.services.exam_service import ExamService
from common.services.communication_service import CommunicationService
from common.services.ai_service import AIService
from common.services.file_service import FileService
from common.services.notification_service import NotificationService
from common.services.log_service import LogService
from common.services.data_service import DataService

__all__ = [
    'UserService',
    'AuthService',
    'ContentService',
    'ExamService',
    'CommunicationService',
    'AIService',
    'FileService',
    'NotificationService',
    'LogService',
    'DataService',
]

