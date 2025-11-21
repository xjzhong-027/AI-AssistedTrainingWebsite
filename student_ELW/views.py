from django.shortcuts import render
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from Account.services.auth_service_impl import AuthServiceImpl


# Create your views here.
# 学生端主页展示
@AuthServiceImpl.require_login
def student_index(request):
    """
    学生端主页展示
    
    使用 @require_login 装饰器确保用户已登录。
    同时检查用户角色是否为 'student'。
    """
    role = request.session.get('role', 'none')
    if role == 'student':
        return render(request, 'students/index.html', {
            'username': request.session['username'],
        })
    else:
        # 非学生角色，重定向到登录页
        return redirect('login')