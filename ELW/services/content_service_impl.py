"""
ContentService implementation for ELW module.

This module implements the ContentService interface, providing unified access
to content (questions, media materials, units, etc.).
"""
from typing import Optional, List, Dict
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
    
    @staticmethod
    def create_media_material(data: Dict) -> MediaMaterial:
        """创建媒体素材"""
        return MediaMaterial.objects.create(
            title=data.get('title', ''),
            theme=data.get('theme', ''),
            abstract=data.get('abstract', ''),
            keywords=data.get('keywords', ''),
            transcript=data.get('transcript', ''),
            media_url=data.get('media_url', ''),
            image_url=data.get('image_url', '')
        )
    
    @staticmethod
    def update_media_material(material_id: int, data: Dict) -> Optional[MediaMaterial]:
        """更新媒体素材"""
        try:
            material = MediaMaterial.objects.get(id=material_id)
            for key, value in data.items():
                if hasattr(material, key):
                    setattr(material, key, value)
            material.save()
            return material
        except MediaMaterial.DoesNotExist:
            return None
    
    @staticmethod
    def delete_media_material(material_id: int) -> bool:
        """删除媒体素材"""
        try:
            material = MediaMaterial.objects.get(id=material_id)
            material.delete()
            return True
        except MediaMaterial.DoesNotExist:
            return False
    
    @staticmethod
    def create_main_question(media_material_id: int, data: Dict) -> MainQuestion:
        """创建大题"""
        media_material = ContentServiceImpl.get_media_material_by_id(media_material_id)
        if not media_material:
            raise ValueError(f"Media material {media_material_id} not found")
        
        return MainQuestion.objects.create(
            media_material=media_material,
            question_type=data.get('question_type', 'choice'),
            question_text=data.get('question_text', ''),
            image_url=data.get('image_url', ''),
            maximum_play=data.get('maximum_play', 3),
            minimum_play=data.get('minimum_play', 0),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            allow_pause=data.get('allow_pause', False),
            limited_time=data.get('limited_time'),
            no_media=data.get('no_media', False)
        )
    
    @staticmethod
    def update_main_question(question_id: int, data: Dict) -> Optional[MainQuestion]:
        """更新大题"""
        try:
            question = MainQuestion.objects.get(id=question_id)
            for key, value in data.items():
                if hasattr(question, key):
                    setattr(question, key, value)
            question.save()
            return question
        except MainQuestion.DoesNotExist:
            return None
    
    @staticmethod
    def delete_main_question(question_id: int) -> bool:
        """删除大题"""
        try:
            question = MainQuestion.objects.get(id=question_id)
            question.delete()
            return True
        except MainQuestion.DoesNotExist:
            return False
    
    @staticmethod
    def create_sub_question(main_question_id: int, data: Dict) -> SubQuestion:
        """创建小题"""
        main_question = ContentServiceImpl.get_main_question_by_id(main_question_id)
        if not main_question:
            raise ValueError(f"Main question {main_question_id} not found")
        
        return SubQuestion.objects.create(
            main_question=main_question,
            question_text=data.get('question_text', ''),
            image_url=data.get('image_url', ''),
            tips=data.get('tips'),
            answer=data.get('answer', ''),
            analysis=data.get('analysis'),
            score=data.get('score', 1.0)
        )
    
    @staticmethod
    def update_sub_question(question_id: int, data: Dict) -> Optional[SubQuestion]:
        """更新小题"""
        try:
            question = SubQuestion.objects.get(id=question_id)
            for key, value in data.items():
                if hasattr(question, key):
                    setattr(question, key, value)
            question.save()
            return question
        except SubQuestion.DoesNotExist:
            return None
    
    @staticmethod
    def delete_sub_question(question_id: int) -> bool:
        """删除小题"""
        try:
            question = SubQuestion.objects.get(id=question_id)
            question.delete()
            return True
        except SubQuestion.DoesNotExist:
            return False
    
    @staticmethod
    def create_unit(class_id: int, data: Dict) -> Unit:
        """创建单元"""
        from Account.services.user_service_impl import UserServiceImpl
        class_instance = UserServiceImpl.get_class_by_id(class_id)
        if not class_instance:
            raise ValueError(f"Class {class_id} not found")
        
        from Query.models import OverdueDeductionRule
        overdue_rule = None
        if data.get('overdue_rule_id'):
            try:
                overdue_rule = OverdueDeductionRule.objects.get(id=data.get('overdue_rule_id'))
            except OverdueDeductionRule.DoesNotExist:
                pass
        
        return Unit.objects.create(
            class_instance=class_instance,
            order=data.get('order', 1),
            title=data.get('title', ''),
            type=data.get('type', 'practice'),
            overdue_rule=overdue_rule
        )
    
    @staticmethod
    def update_unit(unit_id: int, data: Dict) -> Optional[Unit]:
        """更新单元"""
        try:
            unit = Unit.objects.get(id=unit_id)
            for key, value in data.items():
                if key == 'overdue_rule_id':
                    from Query.models import OverdueDeductionRule
                    if value:
                        try:
                            unit.overdue_rule = OverdueDeductionRule.objects.get(id=value)
                        except OverdueDeductionRule.DoesNotExist:
                            unit.overdue_rule = None
                    else:
                        unit.overdue_rule = None
                elif hasattr(unit, key):
                    setattr(unit, key, value)
            unit.save()
            return unit
        except Unit.DoesNotExist:
            return None
    
    @staticmethod
    def delete_unit(unit_id: int) -> bool:
        """删除单元"""
        try:
            unit = Unit.objects.get(id=unit_id)
            unit.delete()
            return True
        except Unit.DoesNotExist:
            return False
    
    @staticmethod
    def create_paper_page(unit_id: int, data: Dict) -> PaperPage:
        """创建试卷页面"""
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            raise ValueError(f"Unit {unit_id} not found")
        
        return PaperPage.objects.create(
            unit=unit,
            order=data.get('order', 1),
            can_modify=data.get('can_modify', False),
            limited_time=data.get('limited_time')
        )
    
    @staticmethod
    def update_paper_page(page_id: int, data: Dict) -> Optional[PaperPage]:
        """更新试卷页面"""
        try:
            page = PaperPage.objects.get(id=page_id)
            for key, value in data.items():
                if hasattr(page, key):
                    setattr(page, key, value)
            page.save()
            return page
        except PaperPage.DoesNotExist:
            return None
    
    @staticmethod
    def delete_paper_page(page_id: int) -> bool:
        """删除试卷页面"""
        try:
            page = PaperPage.objects.get(id=page_id)
            page.delete()
            return True
        except PaperPage.DoesNotExist:
            return False

