#导入要用的模块
import os
import uuid
import datetime
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# from django.contrib.auth import authenticate, login
from English_Listening_Website import settings
from .forms import UploadMediaForm
from ELW import models




from .models import BigQuestion, MediaMaterial
from .forms import BigQuestionForm, SmallQuestionFormSet

# 大题+小题页
def create_big_question_with_small_questions(request):
    task_package_id = request.GET.get('task_package_id')
    print('task_package_id', task_package_id)
    if request.method == 'POST':
        big_question_form = BigQuestionForm(request.POST)
        small_question_formset = SmallQuestionFormSet(request.POST, request.FILES)

        if big_question_form.is_valid() and small_question_formset.is_valid():
            # 保存大题
            big_question = big_question_form.save(commit=False)
            big_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            big_question.save()

            # 将每个小题的关联设置为刚保存的大题
            small_questions = small_question_formset.save(commit=False)
            for small_question in small_questions:
                # if not small_question.cleaned_data.get('DELETE', False):
                small_question.big_question = big_question
                small_question.save()
            # 删除已标记为删除的小题
            # for deleted_form in small_question_formset.deleted_objects:
            #     deleted_form.delete()
            # return redirect('big_question_list')  # 假设有一个大题列表页面
            return HttpResponse('submit all.')
    else:
        big_question_form = BigQuestionForm()
        small_question_formset = SmallQuestionFormSet()

    return render(request, 'create_big_question_with_small_questions.html', {
        'big_question_form': big_question_form,
        'small_question_formset': small_question_formset
    })







# Create your views here.

def test_page(request):
    return render(request, 'test_page.html')

# 更新用户活跃时间
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
            request.session['last_active_time'] = datetime.datetime.now().isoformat()
            # print('last_active_time', request.session['last_active_time'])
        return JsonResponse({"status": "success"})
    # if request.method == 'GET':
    #     # 如果用户已登录
    #     if request.session.get('is_login', False):
    #         last_active_time = request.session.get('last_active_time', None)
    #         if last_active_time:
    #             last_active_time = datetime.datetime.fromisoformat(last_active_time)
    #
    #             # 超过 30 分钟的超时检查
    #             if (datetime.datetime.now() - last_active_time).total_seconds() > 60 * 1:  # 1分钟
    #                 # 如果超时，返回超时标识
    #                 return JsonResponse({'session_expired': True})
    #     # 如果没有超时，或者用户没有登录
    #     return JsonResponse({'session_expired': False})
    return JsonResponse({"status": "error"}, status=400)

# 处理用户题库输入数据
@csrf_exempt
def submit_question(request):
    if request.method == 'POST':
        print('Delete all in temtaskpackage and exit successfully.')
        models.TemMediaMaterial.objects.all().delete()
    return redirect('teacher_question_bank')

# 登录板块
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']
        request.session['last_active_time'] = datetime.datetime.now().isoformat()
        # 验证学生登录
        if role == 'student':
            if models.Students.objects.filter(username=username).exists():
                request.session['username'] = username
                request.session['is_login'] = True
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
                request.session['username'] = username
                request.session['is_login'] = True
                request.session['teacher_name'] = models.Teachers.objects.get(username=username).name
                # print(request.session['teacher_name'])
                return redirect('teacher_index')
        # 验证管理员登录
        if role == 'admin':
            if models.Admins.objects.filter(username=username).exists():
                request.session['username'] = username
                request.session['is_login'] = True
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

# 题库管理
def teacher_question_bank(request):
    if request.session.get('is_login', None):
        username = request.session.get('username', None)
        # print((datetime.datetime.now() - datetime.datetime.fromisoformat(request.session.get('last_active_time'))).total_seconds() > 60)
        return render(request, 'teacher_side/question_bank.html',
                      {
                          'username': username,
                      })
    return redirect('login')

# 添加题目
def teacher_question_add(request):
    return render(request, 'teacher_side/question_add.html')

# 传统试题交互界面+文档批量导入
def teacher_task_package_add(request):
    # 提交的表单有数据，则为填写表单后提交的网页
    if request.method == 'POST' and request.POST.keys():
        form = UploadMediaForm(request.POST, request.FILES)
        # 表单合法，存储表单数据至临时库
        if form.is_valid():
            # 【处理文件保存逻辑（【待替换】需要保存到数据库，在这里创建 UploadedMedia 实例）】
            media_file = request.FILES.get('media_file')
            image_file = request.FILES.get('image_file')
            media_uuid =uuid.uuid4().hex
            media_file_path = os.path.join(settings.MEDIA_ROOT, 'media/', media_uuid)
            os.makedirs(os.path.dirname(media_file_path), exist_ok=True)
            with open(media_file_path, 'wb+') as destination:
                for chunk in media_file.chunks():
                    destination.write(chunk)
            if image_file:
                image_uuid = uuid.uuid4().hex
                image_file_path = os.path.join(settings.MEDIA_ROOT, 'image/', image_uuid)
                os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
                with open(image_file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                new_task_package = models.MediaMaterial.objects.create(
                    title = request.POST.get('title'),
                    theme = request.POST.get('theme'),
                    abstract = request.POST.get('abstract'),
                    keywords = request.POST.get('keywords'),
                    transcript = request.POST.get('transcript'),
                    media_url = 'media/' + media_uuid,
                    image_url = 'image/' + image_uuid,
                )
                id = new_task_package.id
                params = {'task_package_id': id}
                query_string = urlencode(params)
                url = reverse('create_big_question_with_small_questions')
                return HttpResponseRedirect(f"{url}?{query_string}")
            new_task_package = models.MediaMaterial.objects.create(
                title=request.POST.get('title'),
                theme=request.POST.get('theme'),
                abstract=request.POST.get('abstract'),
                keywords=request.POST.get('keywords'),
                transcript=request.POST.get('transcript'),
                media_url='media/' + media_uuid,
            )
            id = new_task_package.id
            print('Received all task_package_info successfully.')
            # return render(request, 'teacher_side/question_add.html')    #替换为待跳转页面
            params = {'task_package_id': id}
            query_string = urlencode(params)
            url = reverse('create_big_question_with_small_questions')
            return HttpResponseRedirect(f"{url}?{query_string}")
            # return redirect('teacher_question_add')

    # 表单无数据，为初次跳转网页
    print('first fetch at task_package_add.html')
    form = UploadMediaForm()
    return render(request, 'teacher_side/task_package_add.html',
            {
                    'form': form,
                })













def teacher_course(request):
    return render(request, 'teacher_side/course.html')

def teacher_class(request):
    return render(request, 'teacher_side/class.html')

def teacher_exam_bank(request):
    return render(request, 'teacher_side/exam_bank.html')

def teacher_exam_management(request):
    return render(request, 'teacher_side/exam_management.html')

def teacher_forum(request):
    return render(request, 'teacher_side/forum.html')