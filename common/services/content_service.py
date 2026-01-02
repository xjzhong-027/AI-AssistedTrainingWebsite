"""
Content service interface.

This interface provides unified access to content (questions, media materials, units, etc.).
Modules should use this interface instead of directly importing ELW.models.
"""
from typing import Optional, List, Dict
from abc import ABC, abstractmethod


class ContentService(ABC):
    """内容服务接口"""
    
    @staticmethod
    @abstractmethod
    def get_unit_by_id(unit_id: int) -> Optional['Unit']:
        """
        根据ID获取单元
        
        Args:
            unit_id: 单元ID
            
        Returns:
            Unit 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_paper_page_by_id(page_id: int) -> Optional['PaperPage']:
        """
        根据ID获取试卷页面
        
        Args:
            page_id: 试卷页面ID
            
        Returns:
            PaperPage 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_main_question_by_id(question_id: int) -> Optional['MainQuestion']:
        """
        根据ID获取大题
        
        Args:
            question_id: 大题ID
            
        Returns:
            MainQuestion 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_sub_question_by_id(sub_question_id: int) -> Optional['SubQuestion']:
        """
        根据ID获取小题
        
        Args:
            sub_question_id: 小题ID
            
        Returns:
            SubQuestion 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_sub_questions_by_main(main_question_id: int) -> List['SubQuestion']:
        """
        获取大题下的小题列表
        
        Args:
            main_question_id: 大题ID
            
        Returns:
            SubQuestion 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_media_material_by_id(material_id: int) -> Optional['MediaMaterial']:
        """
        根据ID获取媒体素材
        
        Args:
            material_id: 媒体素材ID
            
        Returns:
            MediaMaterial 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_units_by_class(class_id: int) -> List['Unit']:
        """
        获取班级的所有单元
        
        Args:
            class_id: 班级ID
            
        Returns:
            Unit 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_pages_by_unit(unit_id: int) -> List['PaperPage']:
        """
        获取单元的所有试卷页面
        
        Args:
            unit_id: 单元ID
            
        Returns:
            PaperPage 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_questions_by_page(page_id: int) -> List['MainQuestion']:
        """
        获取试卷页面的所有大题
        
        Args:
            page_id: 试卷页面ID
            
        Returns:
            MainQuestion 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_media_material(data: Dict) -> 'MediaMaterial':
        """
        创建媒体素材
        
        Args:
            data: 媒体素材数据字典
            
        Returns:
            MediaMaterial 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_media_material(material_id: int, data: Dict) -> Optional['MediaMaterial']:
        """
        更新媒体素材
        
        Args:
            material_id: 媒体素材ID
            data: 更新的数据字典
            
        Returns:
            MediaMaterial 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def delete_media_material(material_id: int) -> bool:
        """
        删除媒体素材
        
        Args:
            material_id: 媒体素材ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_main_question(media_material_id: int, data: Dict) -> 'MainQuestion':
        """
        创建大题
        
        Args:
            media_material_id: 媒体素材ID
            data: 大题数据字典
            
        Returns:
            MainQuestion 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_main_question(question_id: int, data: Dict) -> Optional['MainQuestion']:
        """
        更新大题
        
        Args:
            question_id: 大题ID
            data: 更新的数据字典
            
        Returns:
            MainQuestion 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def delete_main_question(question_id: int) -> bool:
        """
        删除大题
        
        Args:
            question_id: 大题ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_sub_question(main_question_id: int, data: Dict) -> 'SubQuestion':
        """
        创建小题
        
        Args:
            main_question_id: 大题ID
            data: 小题数据字典
            
        Returns:
            SubQuestion 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_sub_question(question_id: int, data: Dict) -> Optional['SubQuestion']:
        """
        更新小题
        
        Args:
            question_id: 小题ID
            data: 更新的数据字典
            
        Returns:
            SubQuestion 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def delete_sub_question(question_id: int) -> bool:
        """
        删除小题
        
        Args:
            question_id: 小题ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_unit(class_id: int, data: Dict) -> 'Unit':
        """
        创建单元
        
        Args:
            class_id: 班级ID
            data: 单元数据字典
            
        Returns:
            Unit 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_unit(unit_id: int, data: Dict) -> Optional['Unit']:
        """
        更新单元
        
        Args:
            unit_id: 单元ID
            data: 更新的数据字典
            
        Returns:
            Unit 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def delete_unit(unit_id: int) -> bool:
        """
        删除单元
        
        Args:
            unit_id: 单元ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_paper_page(unit_id: int, data: Dict) -> 'PaperPage':
        """
        创建试卷页面
        
        Args:
            unit_id: 单元ID
            data: 页面数据字典
            
        Returns:
            PaperPage 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_paper_page(page_id: int, data: Dict) -> Optional['PaperPage']:
        """
        更新试卷页面
        
        Args:
            page_id: 页面ID
            data: 更新的数据字典
            
        Returns:
            PaperPage 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def delete_paper_page(page_id: int) -> bool:
        """
        删除试卷页面
        
        Args:
            page_id: 页面ID
            
        Returns:
            是否删除成功
        """
        pass

