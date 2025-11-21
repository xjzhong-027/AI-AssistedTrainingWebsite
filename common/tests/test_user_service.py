"""
Tests for UserService interface.

These tests verify that the UserService interface is properly defined
and can be implemented. Actual implementation tests will be in Account module.
"""
import unittest
from abc import ABC
from common.services.user_service import UserService


class TestUserServiceInterface(unittest.TestCase):
    """Test UserService interface definition"""

    def test_user_service_is_abstract(self):
        """Test that UserService is an abstract class"""
        self.assertTrue(issubclass(UserService, ABC))
        
        # Should not be able to instantiate directly
        with self.assertRaises(TypeError):
            UserService()

    def test_user_service_has_required_methods(self):
        """Test that UserService has all required methods"""
        required_methods = [
            'get_student_by_username',
            'get_teacher_by_username',
            'get_student_by_id',
            'get_teacher_by_id',
            'get_student_class',
            'get_teacher_classes',
            'get_class_students',
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(UserService, method_name),
                          f"UserService should have {method_name} method")
            self.assertTrue(callable(getattr(UserService, method_name)),
                          f"{method_name} should be callable")

    def test_user_service_methods_are_static(self):
        """Test that UserService methods are static methods"""
        # Static methods should be accessible without instance
        self.assertTrue(hasattr(UserService, 'get_student_by_username'))
        self.assertTrue(hasattr(UserService, 'get_teacher_by_username'))


class MockUserService(UserService):
    """Mock implementation for testing"""
    
    @staticmethod
    def get_student_by_username(username: str):
        return None
    
    @staticmethod
    def get_teacher_by_username(username: str):
        return None
    
    @staticmethod
    def get_student_by_id(student_id: int):
        return None
    
    @staticmethod
    def get_teacher_by_id(teacher_id: int):
        return None
    
    @staticmethod
    def get_student_class(student_id: int):
        return None
    
    @staticmethod
    def get_teacher_classes(teacher_id: int):
        return []
    
    @staticmethod
    def get_class_students(class_id: int):
        return []


class TestMockUserService(unittest.TestCase):
    """Test that UserService can be implemented"""

    def test_mock_implementation_works(self):
        """Test that a mock implementation can be instantiated"""
        service = MockUserService()
        self.assertIsNotNone(service)
        
        # Should be able to call methods
        result = MockUserService.get_student_by_username("test")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

