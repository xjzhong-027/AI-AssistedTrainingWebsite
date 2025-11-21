"""
AuthService implementation for Account module.

This module implements the AuthService interface, providing authentication
and authorization functionality.
"""
from typing import Optional, Dict
from functools import wraps
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth import login as django_login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from common.services.auth_service import AuthService
from common.exceptions import AuthenticationError, UserNotFoundError
from Account.models import Students, Teachers, Admins, LoginInfo


class AuthServiceImpl(AuthService):
    """认证服务实现"""
    
    @staticmethod
    def authenticate_student(username: str, password: str) -> Optional[Dict]:
        """
        验证学生登录
        
        Args:
            username: 学生用户名
            password: 密码
            
        Returns:
            {'student': Students对象, 'user': User对象} 或 None（如果认证失败）
        """
        try:
            student = Students.objects.get(username=username)
            # 验证密码（当前使用明文密码，后续应改为哈希验证）
            if student.password != password:
                return None
            
            return {
                'student': student,
                'user': student.user
            }
        except Students.DoesNotExist:
            return None
    
    @staticmethod
    def authenticate_teacher(username: str, password: str) -> Optional[Dict]:
        """
        验证教师登录
        
        Args:
            username: 教师用户名
            password: 密码
            
        Returns:
            {'teacher': Teachers对象, 'user': User对象} 或 None（如果认证失败）
        """
        try:
            teacher = Teachers.objects.get(username=username, password=password)
            return {
                'teacher': teacher,
                'user': teacher.user
            }
        except Teachers.DoesNotExist:
            return None
    
    @staticmethod
    def authenticate_admin(username: str, password: str) -> Optional[Dict]:
        """
        验证管理员登录
        
        Args:
            username: 管理员用户名
            password: 密码
            
        Returns:
            {'admin': Admins对象, 'user': User对象} 或 None（如果认证失败）
        """
        try:
            admin = Admins.objects.get(username=username)
            # 验证密码（当前使用明文密码，后续应改为哈希验证）
            if admin.password != password:
                return None
            
            return {
                'admin': admin,
                'user': None  # Admins 可能没有关联的 User 对象
            }
        except Admins.DoesNotExist:
            return None
    
    @staticmethod
    def create_login_record(username: str, role: str, request: HttpRequest) -> LoginInfo:
        """
        创建登录记录
        
        Args:
            username: 用户名
            role: 角色（'student', 'teacher', 'admin'）
            request: HTTP请求对象
            
        Returns:
            LoginInfo 对象
        """
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return LoginInfo.objects.create(
            username=username,
            week=0,  # LoginInfo 模型需要 week 字段
            action='login',
            action_time=timezone.now(),
            last_active_time='',
            device_info=user_agent,
        )
    
    @staticmethod
    def update_last_activity(username: str, request: HttpRequest) -> None:
        """
        更新用户最后活跃时间
        
        Args:
            username: 用户名
            request: HTTP请求对象
        """
        if request.session.get('is_login', False):
            request.session['last_active_time'] = timezone.now().isoformat()
    
    @staticmethod
    def is_authenticated(request: HttpRequest) -> bool:
        """
        检查用户是否已登录
        
        Args:
            request: HTTP请求对象
            
        Returns:
            True 如果已登录，False 否则
        """
        return request.session.get('is_login', False)
    
    @staticmethod
    def get_current_user(request: HttpRequest) -> Optional[Dict]:
        """
        获取当前登录用户信息
        
        Args:
            request: HTTP请求对象
            
        Returns:
            {'username': str, 'role': str, 'user': User对象} 或 None
        """
        if not request.session.get('is_login', False):
            return None
        
        username = request.session.get('username')
        role = request.session.get('role')
        
        if not username or not role:
            return None
        
        # 根据角色获取用户对象
        user = None
        if role == 'student':
            try:
                student = Students.objects.get(username=username)
                user = student.user
            except Students.DoesNotExist:
                pass
        elif role == 'teacher':
            try:
                teacher = Teachers.objects.get(username=username)
                user = teacher.user
            except Teachers.DoesNotExist:
                pass
        
        return {
            'username': username,
            'role': role,
            'user': user
        }
    
    @staticmethod
    def require_login(view_func):
        """
        登录检查装饰器
        
        用法:
            @AuthServiceImpl.require_login
            def my_view(request):
                ...
        
        Args:
            view_func: 视图函数
            
        Returns:
            装饰后的视图函数
        """
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not AuthServiceImpl.is_authenticated(request):
                return redirect(reverse('login'))
            return view_func(request, *args, **kwargs)
        return wrapper

