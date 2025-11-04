from django.contrib.auth import logout
from django.conf import settings
from django.utils.timezone import now
from ELW import models
import datetime
from django.shortcuts import redirect

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 如果用户已登录，检查其 session 超时
        if request.session.get('is_login') is True:
            last_active_time = request.session.get('last_active_time', None)
            # 判断未活跃时间
            if (last_active_time and
                    (datetime.datetime.now() - datetime.datetime.fromisoformat(last_active_time)).total_seconds() > 60 * 30):
                # 记录强制登出日志
                models.LoginInfo.objects.create(
                    username=request.session.get('username'),
                    action='forced_logout',
                    action_time=datetime.datetime.now(),
                    last_active_time=request.session.get('last_active_time'),  # 待修改
                    device_info=request.META.get('HTTP_USER_AGENT', ''),
                )
                # 强制登出
                logout(request)
                # 重定向到登录页面或者提示页面
                return redirect('login')  # 这里重定向到登录页面
        response = self.get_response(request)
        return response


class StaticFileContentTypeMiddleware:
    """确保静态文件的Content-Type正确"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # 如果是静态CSS文件，确保Content-Type正确
        if request.path.endswith('.css'):
            # 确保Content-Type正确，并设置编码
            try:
                response['Content-Type'] = 'text/css; charset=utf-8'
            except Exception:
                pass

            # 开发环境避免缓存粘连（曾被错误 MIME 缓存时）
            try:
                if getattr(settings, 'DEBUG', False):
                    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response['Pragma'] = 'no-cache'
                    response['Expires'] = '0'
            except Exception:
                pass
        return response