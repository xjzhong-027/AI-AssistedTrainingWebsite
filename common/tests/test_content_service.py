"""
Tests for ContentService interface.
"""
import unittest
from abc import ABC
from common.services.content_service import ContentService


class TestContentServiceInterface(unittest.TestCase):
    """Test ContentService interface definition"""

    def test_content_service_is_abstract(self):
        """Test that ContentService is an abstract class"""
        self.assertTrue(issubclass(ContentService, ABC))
        
        # Should not be able to instantiate directly
        with self.assertRaises(TypeError):
            ContentService()

    def test_content_service_has_required_methods(self):
        """Test that ContentService has all required methods"""
        required_methods = [
            'get_unit_by_id',
            'get_paper_page_by_id',
            'get_main_question_by_id',
            'get_sub_question_by_id',
            'get_sub_questions_by_main',
            'get_media_material_by_id',
            'get_units_by_class',
            'get_pages_by_unit',
            'get_questions_by_page',
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(ContentService, method_name),
                          f"ContentService should have {method_name} method")
            self.assertTrue(callable(getattr(ContentService, method_name)),
                          f"{method_name} should be callable")


class MockContentService(ContentService):
    """Mock implementation for testing"""
    
    @staticmethod
    def get_unit_by_id(unit_id: int):
        return None
    
    @staticmethod
    def get_paper_page_by_id(page_id: int):
        return None
    
    @staticmethod
    def get_main_question_by_id(question_id: int):
        return None
    
    @staticmethod
    def get_sub_question_by_id(sub_question_id: int):
        return None
    
    @staticmethod
    def get_sub_questions_by_main(main_question_id: int):
        return []
    
    @staticmethod
    def get_media_material_by_id(material_id: int):
        return None
    
    @staticmethod
    def get_units_by_class(class_id: int):
        return []
    
    @staticmethod
    def get_pages_by_unit(unit_id: int):
        return []
    
    @staticmethod
    def get_questions_by_page(page_id: int):
        return []


class TestMockContentService(unittest.TestCase):
    """Test that ContentService can be implemented"""

    def test_mock_implementation_works(self):
        """Test that a mock implementation can be instantiated"""
        service = MockContentService()
        self.assertIsNotNone(service)
        
        # Should be able to call methods
        result = MockContentService.get_unit_by_id(1)
        self.assertIsNone(result)
        
        result = MockContentService.get_units_by_class(1)
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()

