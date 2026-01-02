"""
User service interface.

This interface provides unified access to user information (students, teachers, admins).
Modules should use this interface instead of directly importing Account.models.
"""
from typing import Optional, List
from abc import ABC, abstractmethod


class UserService(ABC):
    """用户信息服务接口"""
    
    @staticmethod
    @abstractmethod
    def get_student_by_username(username: str) -> Optional['Students']:
        """
        根据用户名获取学生对象
        
        Args:
            username: 学生用户名
            
        Returns:
            Students 对象或 None（如果不存在）
            
        Raises:
            UserNotFoundError: 当用户不存在时（可选，取决于实现）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_teacher_by_username(username: str) -> Optional['Teachers']:
        """
        根据用户名获取教师对象
        
        Args:
            username: 教师用户名
            
        Returns:
            Teachers 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_student_by_id(student_id: int) -> Optional['Students']:
        """
        根据ID获取学生对象
        
        Args:
            student_id: 学生ID
            
        Returns:
            Students 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_teacher_by_id(teacher_id: int) -> Optional['Teachers']:
        """
        根据ID获取教师对象
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            Teachers 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_student_class(student_id: int) -> Optional['Class']:
        """
        获取学生所在班级
        
        Args:
            student_id: 学生ID
            
        Returns:
            Class 对象或 None（如果学生不存在或没有班级）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_teacher_classes(teacher_id: int) -> List['Class']:
        """
        获取教师负责的班级列表
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            Class 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_class_students(class_id: int) -> List['Students']:
        """
        获取班级的所有学生
        
        Args:
            class_id: 班级ID
            
        Returns:
            Students 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_class_by_id(class_id: int) -> Optional['Class']:
        """
        根据ID获取班级对象
        
        Args:
            class_id: 班级ID
            
        Returns:
            Class 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_all_students() -> List['Students']:
        """
        获取所有学生
        
        Returns:
            Students 对象列表
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_students_by_class(class_instance: 'Class') -> List['Students']:
        """
        根据班级实例获取学生列表
        
        Args:
            class_instance: Class 对象
            
        Returns:
            Students 对象列表（可能为空）
        """
        pass

