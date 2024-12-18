#导入要用的模块
import datetime
import os
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# from django.contrib.auth import authenticate, login
from English_Listening_Website import settings
from .forms import UploadMediaForm
from ELW import models



# Create your views here.

def test_page(request):
    return render(request, 'test_page.html')


@csrf_exempt
def update_last_activity(request):
    if request.method == 'POST':
        # 获取请求中的时间
        # import json
        # data = json.loads(request.body)
        # last_active_time = data.get('last_active_time')
        print('received POST request.')
        if request.session.get('is_login', False):
            # 更新数据库中的最后活跃时间
            request.session['last_active_time'] = str(datetime.datetime.now())
            # print('last_active_time', request.session['last_active_time'])
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

# 登录板块
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']

        # 验证学生登录
        if role == 'student':
            if models.Students.objects.filter(username=username).exists():
                time = datetime.datetime.now()
                # 获取用户的 User-Agent 信息，包括浏览器类型和引擎、操作系统信息、设备类型等信息
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                # 【待修改周次week】
                models.LoginInfo.objects.create(
                    username=username,
                    action='login',
                    action_time=time,
                    last_active_time='',
                    device_info=user_agent,
                )
                # 【待替换学生端页面】
                return HttpResponse('The main page of student version should be shown here.')
        # 验证教师登录
        if role == 'teacher':
            if models.Teachers.objects.filter(username=username,password=password).exists():
                request.session['username'] = username  #username值发送给session的username
                request.session['is_login'] = True  #认证为真
                request.session['teacher_name'] = models.Teachers.objects.get(username=username).name
                # print(request.session['teacher_name'])
                return redirect('teacher_index')
        # 验证管理员登录
        if role == 'admin':
            if models.Admins.objects.filter(username=username).exists():
                #【待替换管理员页面】
                return HttpResponse('The main page of admin version should be shown here.')
        return render(request, 'login.html',
                      {
                          'error_message': 'Invalid username or password！',
                      })

# 登出板块
def log_out(request):
    # 获取用户的 IP 地址
    # ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    # print('ip_address', ip_address)
    models.LoginInfo.objects.create(
        username=request.session.get('username'),
        action='logout',
        action_time=datetime.datetime.now(),
        last_active_time=request.session['last_active_time'],   #待修改
        device_info=request.META.get('HTTP_USER_AGENT', ''),
    )
    logout(request)
    return redirect('login')

# 教师端主页展示
def teacher_index(request):
    if request.session.get('is_login', None):
        return render(request, 'teacher_side/index.html', {
            'teacher_name': request.session['teacher_name'],
        })
    return redirect('login')

def teacher_course(request):
    return render(request, 'teacher_side/course.html')

def teacher_class(request):
    return render(request, 'teacher_side/class.html')

# 题库管理
def teacher_question_bank(request):
    if request.session.get('is_login', None):
        username = request.session.get('username', None)
        return render(request, 'teacher_side/question_bank.html',
                      {
                          'username': username,
                      })
    return redirect('login')

def teacher_exam_bank(request):
    return render(request, 'teacher_side/exam_bank.html')

def teacher_exam_management(request):
    return render(request, 'teacher_side/exam_management.html')

def teacher_forum(request):
    return render(request, 'teacher_side/forum.html')

def teacher_question_add(request):
    return render(request, 'teacher_side/task_package_add.html')

# 传统试题交互界面+文档批量导入
def teacher_task_package_add(request):
    if request.method == 'POST':
        # print('post successfully.')
        form = UploadMediaForm(request.POST, request.FILES)
        if form.is_valid():
            # 【处理文件保存逻辑（【待替换】需要保存到数据库，在这里创建 UploadedMedia 实例）】
            # file = request.FILES['file']
            # file_path = os.path.join(settings.MEDIA_ROOT, file.name)
            # with open(file_path, 'wb+') as destination:
            #     for chunk in file.chunks():
            #         destination.write(chunk)
            # return render(request, 'test_page.html')    #【待替换为实际的成功页面 URL】
            audio_file = request.FILES.get('audio_file')
            video_file = request.FILES.get('video_file')
            image_file = request.FILES.get('image_file')
            if audio_file or video_file:
                audio_file_path = os.path.join(settings.MEDIA_ROOT, 'audio/',audio_file.name)
                video_file_path = os.path.join(settings.MEDIA_ROOT, 'video/',video_file.name)
                image_file_path = os.path.join(settings.MEDIA_ROOT, 'image/',image_file.name)
                # 【待修改】应将文件路径存储至数据库
                if audio_file:
                    os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
                    with open(audio_file_path, 'wb+') as destination:
                        for chunk in audio_file.chunks():
                            destination.write(chunk)
                if video_file:
                    os.makedirs(os.path.dirname(video_file_path), exist_ok=True)
                    with open(video_file_path, 'wb+') as destination:
                        for chunk in video_file.chunks():
                            destination.write(chunk)
                if image_file:
                    os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
                    with open(image_file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                print('文件接收成功！')
                return render(request, 'test_page.html')    #替换为待跳转页面
    else:
        form = UploadMediaForm()
    return render(request, 'teacher_side/task_package_add.html',
                    {
                        'form': form,
                    })




