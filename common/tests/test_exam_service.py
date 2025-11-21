"""
Tests for ExamService interface.
"""
import unittest
from typing import Optional
from abc import ABC
from unittest.mock import Mock
from common.services.exam_service import ExamService


class TestExamServiceInterface(unittest.TestCase):
    """Test ExamService interface definition"""

    def test_exam_service_is_abstract(self):
        """Test that ExamService is an abstract class"""
        self.assertTrue(issubclass(ExamService, ABC))
        
        # Should not be able to instantiate directly
        with self.assertRaises(TypeError):
            ExamService()

    def test_exam_service_has_required_methods(self):
        """Test that ExamService has all required methods"""
        required_methods = [
            'create_exam_record',
            'get_exam_record',
            'get_or_create_page_record',
            'save_answer',
            'get_answers_by_page_record',
            'update_media_play_record',
            'get_media_play_record',
            'submit_exam',
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(ExamService, method_name),
                          f"ExamService should have {method_name} method")
            self.assertTrue(callable(getattr(ExamService, method_name)),
                          f"{method_name} should be callable")


class MockExamService(ExamService):
    """Mock implementation for testing"""
    
    @staticmethod
    def create_exam_record(student_id: int, unit_id: int):
        return Mock()
    
    @staticmethod
    def get_exam_record(student_id: int, unit_id: int):
        return None
    
    @staticmethod
    def get_or_create_page_record(exam_record_id: int, page_id: int):
        return Mock()
    
    @staticmethod
    def save_answer(student_page_record_id: int, sub_question_id: int, 
                   answer_text: str, is_correct: Optional[bool] = None):
        return Mock()
    
    @staticmethod
    def get_answers_by_page_record(page_record_id: int):
        return []
    
    @staticmethod
    def update_media_play_record(exam_record_id: int, main_question_id: int,
                                 play_count: int, last_pause_time: float):
        return Mock()
    
    @staticmethod
    def get_media_play_record(exam_record_id: int, main_question_id: int):
        return None
    
    @staticmethod
    def submit_exam(exam_record_id: int):
        return True


class TestMockExamService(unittest.TestCase):
    """Test that ExamService can be implemented"""

    def test_mock_implementation_works(self):
        """Test that a mock implementation can be instantiated"""
        service = MockExamService()
        self.assertIsNotNone(service)
        
        # Should be able to call methods
        result = MockExamService.create_exam_record(1, 1)
        self.assertIsNotNone(result)
        
        result = MockExamService.get_answers_by_page_record(1)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()

