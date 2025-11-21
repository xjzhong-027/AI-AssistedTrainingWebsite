"""
Tests for ELW models to ensure they work correctly after LoginInfo migration.
"""
from django.test import TestCase
from ELW.models import MediaMaterial, MainQuestion, SubQuestion, Unit, PaperPage
from Account.models import Class, Course, Teachers


class ELWModelsTestCase(TestCase):
    """Test ELW models basic functionality"""

    def setUp(self):
        """Set up test data"""
        # Create a teacher
        self.teacher = Teachers.objects.create(
            username='test_teacher',
            name='Test Teacher',
            password='test123'
        )
        
        # Create a course
        self.course = Course.objects.create(
            year=2024,
            grade=1,
            semester=1
        )
        
        # Create a class
        self.class_instance = Class.objects.create(
            course=self.course,
            teacher=self.teacher,
            start_date='2024-01-01',
            week=1,
            start_time='08:00:00',
            end_time='10:00:00'
        )

    def test_media_material_creation(self):
        """Test MediaMaterial model can be created"""
        media = MediaMaterial.objects.create(
            title='Test Media',
            theme='Test Theme',
            abstract='Test Abstract',
            media_url='test.mp4'
        )
        self.assertEqual(media.title, 'Test Media')
        self.assertEqual(str(media), 'Test Media')

    def test_main_question_creation(self):
        """Test MainQuestion model can be created"""
        media = MediaMaterial.objects.create(
            title='Test Media',
            theme='Test Theme',
            abstract='Test Abstract',
            media_url='test.mp4'
        )
        question = MainQuestion.objects.create(
            media_material=media,
            question_type='choice',
            question_text='Test Question'
        )
        self.assertEqual(question.question_type, 'choice')
        self.assertEqual(question.question_text, 'Test Question')

    def test_unit_creation(self):
        """Test Unit model can be created"""
        unit = Unit.objects.create(
            class_instance=self.class_instance,
            order=1,
            title='Test Unit',
            type='practice'
        )
        self.assertEqual(unit.title, 'Test Unit')
        self.assertEqual(unit.type, 'practice')
        self.assertEqual(str(unit), f"practice - Test Unit for {self.class_instance}")

    def test_models_import_correctly(self):
        """Test that all models can be imported without errors"""
        from ELW.models import (
            MediaMaterial, MainQuestion, SubQuestion,
            ChoiceOption, MatchingOption, Correction,
            Unit, PaperPage, Document, Blank, TimeManagement
        )
        # If we get here, imports are successful
        self.assertTrue(True)


class ELWLoginInfoRemovedTestCase(TestCase):
    """Test that LoginInfo is no longer in ELW models"""

    def test_logininfo_not_in_elw_models(self):
        """Test that LoginInfo is not accessible from ELW.models"""
        from ELW import models
        
        # LoginInfo should not exist in ELW.models
        self.assertFalse(hasattr(models, 'LoginInfo'), 
                        "LoginInfo should not be in ELW.models after migration")

