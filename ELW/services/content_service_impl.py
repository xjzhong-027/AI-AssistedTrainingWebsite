"""
ContentService implementation for ELW module.

This module implements the ContentService interface, providing unified access
to content (questions, media materials, units, etc.).
"""
from typing import Optional, List
from common.services.content_service import ContentService
from ELW.models import (
    Unit, PaperPage, MainQuestion, SubQuestion, MediaMaterial, PageMainQuestion
)


class ContentServiceImpl(ContentService):
    """内容服务实现"""

    @staticmethod
    def get_unit_by_id(unit_id: int) -> Optional['Unit']:
        """
        根据ID获取单元
        
        Args:
            unit_id: 单元ID
            
        Returns:
            Unit 对象或 None（如果不存在）
        """
        try:
            return Unit.objects.get(id=unit_id)
        except Unit.DoesNotExist:
            return None

    @staticmethod
    def get_paper_page_by_id(page_id: int) -> Optional['PaperPage']:
        """
        根据ID获取试卷页面
        
        Args:
            page_id: 试卷页面ID
            
        Returns:
            PaperPage 对象或 None（如果不存在）
        """
        try:
            return PaperPage.objects.get(id=page_id)
        except PaperPage.DoesNotExist:
            return None

    @staticmethod
    def get_main_question_by_id(question_id: int) -> Optional['MainQuestion']:
        """
        根据ID获取大题
        
        Args:
            question_id: 大题ID
            
        Returns:
            MainQuestion 对象或 None（如果不存在）
        """
        try:
            return MainQuestion.objects.get(id=question_id)
        except MainQuestion.DoesNotExist:
            return None

    @staticmethod
    def get_sub_question_by_id(sub_question_id: int) -> Optional['SubQuestion']:
        """
        根据ID获取小题
        
        Args:
            sub_question_id: 小题ID
            
        Returns:
            SubQuestion 对象或 None（如果不存在）
        """
        try:
            return SubQuestion.objects.get(id=sub_question_id)
        except SubQuestion.DoesNotExist:
            return None

    @staticmethod
    def get_sub_questions_by_main(main_question_id: int) -> List['SubQuestion']:
        """
        获取大题下的小题列表
        
        Args:
            main_question_id: 大题ID
            
        Returns:
            SubQuestion 对象列表（可能为空）
        """
        try:
            main_question = MainQuestion.objects.get(id=main_question_id)
            return list(main_question.sub_questions.all())
        except MainQuestion.DoesNotExist:
            return []

    @staticmethod
    def get_media_material_by_id(material_id: int) -> Optional['MediaMaterial']:
        """
        根据ID获取媒体素材
        
        Args:
            material_id: 媒体素材ID
            
        Returns:
            MediaMaterial 对象或 None（如果不存在）
        """
        try:
            return MediaMaterial.objects.get(id=material_id)
        except MediaMaterial.DoesNotExist:
            return None

    @staticmethod
    def get_units_by_class(class_id: int) -> List['Unit']:
        """
        获取班级的所有单元
        
        Args:
            class_id: 班级ID
            
        Returns:
            Unit 对象列表（可能为空）
        """
        try:
            from Account.models import Class
            class_instance = Class.objects.get(id=class_id)
            return list(class_instance.units.all().order_by('order'))
        except Class.DoesNotExist:
            return []

    @staticmethod
    def get_pages_by_unit(unit_id: int) -> List['PaperPage']:
        """
        获取单元的所有试卷页面
        
        Args:
            unit_id: 单元ID
            
        Returns:
            PaperPage 对象列表（可能为空）
        """
        try:
            unit = Unit.objects.get(id=unit_id)
            return list(unit.paper_pages.all().order_by('order'))
        except Unit.DoesNotExist:
            return []

    @staticmethod
    def get_questions_by_page(page_id: int) -> List['MainQuestion']:
        """
        获取试卷页面的所有大题
        
        Args:
            page_id: 试卷页面ID
            
        Returns:
            MainQuestion 对象列表（可能为空）
        """
        try:
            page = PaperPage.objects.get(id=page_id)
            # 通过 PageMainQuestion 关联获取大题
            page_main_questions = page.page_main_questions.all()
            main_questions = [pmq.main_question for pmq in page_main_questions]
            return main_questions
        except PaperPage.DoesNotExist:
            return []

