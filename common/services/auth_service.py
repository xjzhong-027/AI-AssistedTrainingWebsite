"""
Authentication service interface.

This interface provides unified authentication and authorization functionality.
Modules should use this interface instead of directly implementing login logic.
"""
from typing import Optional, Dict
from abc import ABC, abstractmethod
from django.http import HttpRequest


class AuthService(ABC):
    """认证服务接口"""
    
    @staticmethod
    @abstractmethod
    def authenticate_student(username: str, password: str) -> Optional[Dict]:
        """
        验证学生登录
        
        Args:
            username: 学生用户名
            password: 密码
            
        Returns:
            {'student': Students对象, 'user': User对象} 或 None（如果认证失败）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def authenticate_teacher(username: str, password: str) -> Optional[Dict]:
        """
        验证教师登录
        
        Args:
            username: 教师用户名
            password: 密码
            
        Returns:
            {'teacher': Teachers对象, 'user': User对象} 或 None（如果认证失败）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def authenticate_admin(username: str, password: str) -> Optional[Dict]:
        """
        验证管理员登录
        
        Args:
            username: 管理员用户名
            password: 密码
            
        Returns:
            {'admin': Admins对象, 'user': User对象} 或 None（如果认证失败）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def create_login_record(username: str, role: str, request: HttpRequest) -> 'LoginInfo':
        """
        创建登录记录
        
        Args:
            username: 用户名
            role: 角色（'student', 'teacher', 'admin'）
            request: HTTP请求对象
            
        Returns:
            LoginInfo 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_last_activity(username: str, request: HttpRequest) -> None:
        """
        更新用户最后活跃时间
        
        Args:
            username: 用户名
            request: HTTP请求对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def is_authenticated(request: HttpRequest) -> bool:
        """
        检查用户是否已登录
        
        Args:
            request: HTTP请求对象
            
        Returns:
            True 如果已登录，False 否则
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_current_user(request: HttpRequest) -> Optional[Dict]:
        """
        获取当前登录用户信息
        
        Args:
            request: HTTP请求对象
            
        Returns:
            {'username': str, 'role': str, 'user': User对象} 或 None
        """
        pass
    
    @staticmethod
    def require_login(view_func):
        """
        登录检查装饰器
        
        用法:
            @AuthService.require_login
            def my_view(request):
                ...
        
        注意：这是一个装饰器工厂，需要在实现类中提供具体实现
        """
        # 这个装饰器需要在实现类中具体实现
        # 这里只是接口定义
        pass

