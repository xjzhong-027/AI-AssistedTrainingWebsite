"""
Tests for ContentService implementation.

These tests verify that ContentServiceImpl correctly implements the ContentService interface.
"""
from django.test import TestCase
from Account.models import Class, Course, Teachers
from django.contrib.auth.models import User
from ELW.models import (
    MediaMaterial, MainQuestion, SubQuestion, Unit, PaperPage
)
from ELW.services.content_service_impl import ContentServiceImpl


class ContentServiceImplTestCase(TestCase):
    """Test ContentService implementation"""

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
        
        # Create test media material
        self.media = MediaMaterial.objects.create(
            title='Test Media',
            theme='Test Theme',
            abstract='Test Abstract',
            media_url='test.mp4'
        )
        
        # Create test main question
        self.main_question = MainQuestion.objects.create(
            media_material=self.media,
            question_type='choice',
            question_text='Test Question'
        )
        
        # Create test sub question
        self.sub_question = SubQuestion.objects.create(
            main_question=self.main_question,
            question_text='Test Sub Question',
            answer='Test Answer'
        )
        
        # Create test unit
        self.unit = Unit.objects.create(
            class_instance=self.class_instance,
            order=1,
            title='Test Unit',
            type='practice'
        )
        
        # Create test paper page
        self.paper_page = PaperPage.objects.create(
            unit=self.unit,
            order=1,
            text='Test Page'
        )

    def test_get_unit_by_id_success(self):
        """Test get_unit_by_id with valid ID"""
        result = ContentServiceImpl.get_unit_by_id(self.unit.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.unit.id)
        self.assertEqual(result.title, 'Test Unit')

    def test_get_unit_by_id_not_found(self):
        """Test get_unit_by_id with invalid ID"""
        result = ContentServiceImpl.get_unit_by_id(99999)
        self.assertIsNone(result)

    def test_get_paper_page_by_id_success(self):
        """Test get_paper_page_by_id with valid ID"""
        result = ContentServiceImpl.get_paper_page_by_id(self.paper_page.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.paper_page.id)
        self.assertEqual(result.text, 'Test Page')

    def test_get_paper_page_by_id_not_found(self):
        """Test get_paper_page_by_id with invalid ID"""
        result = ContentServiceImpl.get_paper_page_by_id(99999)
        self.assertIsNone(result)

    def test_get_main_question_by_id_success(self):
        """Test get_main_question_by_id with valid ID"""
        result = ContentServiceImpl.get_main_question_by_id(self.main_question.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.main_question.id)
        self.assertEqual(result.question_text, 'Test Question')

    def test_get_main_question_by_id_not_found(self):
        """Test get_main_question_by_id with invalid ID"""
        result = ContentServiceImpl.get_main_question_by_id(99999)
        self.assertIsNone(result)

    def test_get_sub_question_by_id_success(self):
        """Test get_sub_question_by_id with valid ID"""
        result = ContentServiceImpl.get_sub_question_by_id(self.sub_question.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.sub_question.id)
        self.assertEqual(result.question_text, 'Test Sub Question')

    def test_get_sub_question_by_id_not_found(self):
        """Test get_sub_question_by_id with invalid ID"""
        result = ContentServiceImpl.get_sub_question_by_id(99999)
        self.assertIsNone(result)

    def test_get_sub_questions_by_main_success(self):
        """Test get_sub_questions_by_main with valid main question ID"""
        result = ContentServiceImpl.get_sub_questions_by_main(self.main_question.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.sub_question.id)

    def test_get_sub_questions_by_main_empty(self):
        """Test get_sub_questions_by_main with main question that has no sub questions"""
        # Create a new main question without sub questions
        new_main = MainQuestion.objects.create(
            media_material=self.media,
            question_type='choice',
            question_text='New Question'
        )
        result = ContentServiceImpl.get_sub_questions_by_main(new_main.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_sub_questions_by_main_not_found(self):
        """Test get_sub_questions_by_main with invalid main question ID"""
        result = ContentServiceImpl.get_sub_questions_by_main(99999)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_media_material_by_id_success(self):
        """Test get_media_material_by_id with valid ID"""
        result = ContentServiceImpl.get_media_material_by_id(self.media.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.media.id)
        self.assertEqual(result.title, 'Test Media')

    def test_get_media_material_by_id_not_found(self):
        """Test get_media_material_by_id with invalid ID"""
        result = ContentServiceImpl.get_media_material_by_id(99999)
        self.assertIsNone(result)

    def test_get_units_by_class_success(self):
        """Test get_units_by_class with valid class ID"""
        result = ContentServiceImpl.get_units_by_class(self.class_instance.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.unit.id)

    def test_get_units_by_class_empty(self):
        """Test get_units_by_class with class that has no units"""
        # Create a new class without units
        new_class = Class.objects.create(
            course=self.course,
            teacher=self.teacher,
            start_date='2024-01-01',
            week=2,
            start_time='10:00:00',
            end_time='12:00:00'
        )
        result = ContentServiceImpl.get_units_by_class(new_class.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_units_by_class_not_found(self):
        """Test get_units_by_class with invalid class ID"""
        result = ContentServiceImpl.get_units_by_class(99999)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_pages_by_unit_success(self):
        """Test get_pages_by_unit with valid unit ID"""
        result = ContentServiceImpl.get_pages_by_unit(self.unit.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.paper_page.id)

    def test_get_pages_by_unit_empty(self):
        """Test get_pages_by_unit with unit that has no pages"""
        # Create a new unit without pages
        new_unit = Unit.objects.create(
            class_instance=self.class_instance,
            order=2,
            title='New Unit',
            type='practice'
        )
        result = ContentServiceImpl.get_pages_by_unit(new_unit.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_pages_by_unit_not_found(self):
        """Test get_pages_by_unit with invalid unit ID"""
        result = ContentServiceImpl.get_pages_by_unit(99999)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_questions_by_page_success(self):
        """Test get_questions_by_page with valid page ID"""
        # Link main question to paper page
        from ELW.models import PageMainQuestion
        PageMainQuestion.objects.create(
            page=self.paper_page,
            main_question=self.main_question
        )
        
        result = ContentServiceImpl.get_questions_by_page(self.paper_page.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.main_question.id)

    def test_get_questions_by_page_empty(self):
        """Test get_questions_by_page with page that has no questions"""
        # Create a new paper page without questions
        new_page = PaperPage.objects.create(
            unit=self.unit,
            order=2,
            text='New Page'
        )
        result = ContentServiceImpl.get_questions_by_page(new_page.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

    def test_get_questions_by_page_not_found(self):
        """Test get_questions_by_page with invalid page ID"""
        result = ContentServiceImpl.get_questions_by_page(99999)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)

