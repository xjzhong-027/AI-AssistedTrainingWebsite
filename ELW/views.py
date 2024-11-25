#导入要用的模块
import os
from django.shortcuts import render, HttpResponse, redirect
from English_Listening_Website import settings
from .forms import UploadMediaForm

# Create your views here.

def test_page(request):
    return render(request, 'test_page.html')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    #【待连接数据库...】
    if request.method == 'POST':
        #print(request.POST)
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']
        if role == 'student' and username == 'student' and password == 'student':
            return HttpResponse('The main page of student version should be shown here.')
        # 【待修改为教师端主页面】
        if role == 'teacher' and username == 'teacher' and password == 'teacher':
            request.session['username'] = username  #username值发送给session的username
            request.session['is_login'] = True  #认证为真
            return redirect('teacher_index')
        if role == 'admin' and username == 'admin' and password == 'admin':
            return HttpResponse('The main page of admin version should be shown here.')
        return render(request, 'login.html',
                      {
                          'error_message': 'Invalid username or password！',
                      })

def teacher_index(request):
    return render(request, 'teacher_side/index.html')

def teacher_course(request):
    return render(request, 'teacher_side/course.html')

def teacher_class(request):
    return render(request, 'teacher_side/class.html')

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




