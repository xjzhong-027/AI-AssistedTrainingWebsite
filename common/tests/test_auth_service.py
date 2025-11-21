"""
Tests for AuthService interface.
"""
import unittest
from abc import ABC
from unittest.mock import Mock
from common.services.auth_service import AuthService


class TestAuthServiceInterface(unittest.TestCase):
    """Test AuthService interface definition"""

    def test_auth_service_is_abstract(self):
        """Test that AuthService is an abstract class"""
        self.assertTrue(issubclass(AuthService, ABC))
        
        # Should not be able to instantiate directly
        with self.assertRaises(TypeError):
            AuthService()

    def test_auth_service_has_required_methods(self):
        """Test that AuthService has all required methods"""
        required_methods = [
            'authenticate_student',
            'authenticate_teacher',
            'authenticate_admin',
            'create_login_record',
            'update_last_activity',
            'is_authenticated',
            'get_current_user',
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(AuthService, method_name),
                          f"AuthService should have {method_name} method")
            self.assertTrue(callable(getattr(AuthService, method_name)),
                          f"{method_name} should be callable")

    def test_authenticate_student_signature(self):
        """Test authenticate_student method signature"""
        # Should accept username and password
        method = AuthService.authenticate_student
        self.assertIsNotNone(method)


class MockAuthService(AuthService):
    """Mock implementation for testing"""
    
    @staticmethod
    def authenticate_student(username: str, password: str):
        return None
    
    @staticmethod
    def authenticate_teacher(username: str, password: str):
        return None
    
    @staticmethod
    def authenticate_admin(username: str, password: str):
        return None
    
    @staticmethod
    def create_login_record(username: str, role: str, request):
        return Mock()
    
    @staticmethod
    def update_last_activity(username: str, request):
        pass
    
    @staticmethod
    def is_authenticated(request):
        return False
    
    @staticmethod
    def get_current_user(request):
        return None


class TestMockAuthService(unittest.TestCase):
    """Test that AuthService can be implemented"""

    def test_mock_implementation_works(self):
        """Test that a mock implementation can be instantiated"""
        service = MockAuthService()
        self.assertIsNotNone(service)
        
        # Should be able to call methods
        result = MockAuthService.authenticate_student("test", "password")
        self.assertIsNone(result)
        
        result = MockAuthService.is_authenticated(Mock())
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

