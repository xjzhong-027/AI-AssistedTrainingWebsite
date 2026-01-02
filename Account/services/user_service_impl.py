"""
UserService implementation for Account module.

This module implements the UserService interface, providing unified access
to user information (students, teachers, admins).
"""
from typing import Optional, List
from common.services.user_service import UserService
from common.exceptions import UserNotFoundError
from Account.models import Students, Teachers, Admins, Class


class UserServiceImpl(UserService):
    """用户信息服务实现"""

    @staticmethod
    def get_student_by_username(username: str) -> Optional['Students']:
        """
        根据用户名获取学生对象
        
        Args:
            username: 学生用户名
            
        Returns:
            Students 对象或 None（如果不存在）
        """
        try:
            return Students.objects.get(username=username)
        except Students.DoesNotExist:
            return None

    @staticmethod
    def get_teacher_by_username(username: str) -> Optional['Teachers']:
        """
        根据用户名获取教师对象
        
        Args:
            username: 教师用户名
            
        Returns:
            Teachers 对象或 None（如果不存在）
        """
        try:
            return Teachers.objects.get(username=username)
        except Teachers.DoesNotExist:
            return None

    @staticmethod
    def get_student_by_id(student_id: int) -> Optional['Students']:
        """
        根据ID获取学生对象
        
        Args:
            student_id: 学生ID
            
        Returns:
            Students 对象或 None（如果不存在）
        """
        try:
            return Students.objects.get(id=student_id)
        except Students.DoesNotExist:
            return None

    @staticmethod
    def get_teacher_by_id(teacher_id: int) -> Optional['Teachers']:
        """
        根据ID获取教师对象
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            Teachers 对象或 None（如果不存在）
        """
        try:
            return Teachers.objects.get(id=teacher_id)
        except Teachers.DoesNotExist:
            return None

    @staticmethod
    def get_student_class(student_id: int) -> Optional['Class']:
        """
        获取学生所在班级
        
        Args:
            student_id: 学生ID
            
        Returns:
            Class 对象或 None（如果学生不存在或没有班级）
        """
        try:
            student = Students.objects.get(id=student_id)
            return student.class_instance
        except Students.DoesNotExist:
            return None

    @staticmethod
    def get_teacher_classes(teacher_id: int) -> List['Class']:
        """
        获取教师负责的班级列表
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            Class 对象列表（可能为空）
        """
        try:
            teacher = Teachers.objects.get(id=teacher_id)
            return list(Class.objects.filter(teacher=teacher))
        except Teachers.DoesNotExist:
            return []

    @staticmethod
    def get_class_students(class_id: int) -> List['Students']:
        """
        获取班级的所有学生
        
        Args:
            class_id: 班级ID
            
        Returns:
            Students 对象列表（可能为空）
        """
        try:
            class_instance = Class.objects.get(id=class_id)
            return list(Students.objects.filter(class_instance=class_instance))
        except Class.DoesNotExist:
            return []
    
    @staticmethod
    def get_class_by_id(class_id: int) -> Optional['Class']:
        """
        根据ID获取班级对象
        
        Args:
            class_id: 班级ID
            
        Returns:
            Class 对象或 None（如果不存在）
        """
        try:
            return Class.objects.get(id=class_id)
        except Class.DoesNotExist:
            return None
    
    @staticmethod
    def get_all_students() -> List['Students']:
        """
        获取所有学生
        
        Returns:
            Students 对象列表
        """
        return list(Students.objects.all().order_by('class_instance', 'id'))
    
    @staticmethod
    def get_students_by_class(class_instance: 'Class') -> List['Students']:
        """
        根据班级实例获取学生列表
        
        Args:
            class_instance: Class 对象
            
        Returns:
            Students 对象列表（可能为空）
        """
        return list(Students.objects.filter(class_instance=class_instance))

