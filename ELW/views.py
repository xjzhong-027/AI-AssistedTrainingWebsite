#导入要用的模块
import os,uuid,datetime,json,re

from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.core.paginator import Paginator, Page
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from django.contrib.auth import login


from English_Listening_Website import settings
from .forms import UploadMediaForm, WordUploadForm
from ELW import models
from django.contrib import messages

from . import func, pre_page, doc_func, doc_page_func

from .models import (
    MediaMaterial,
    MainQuestion,
    SubQuestion,
    MatchingOption,
    Correction,
    ChoiceOption,
    Course,
    # Teachers,
    # Students,
    # Class,
    # Attendance,
    Unit,
    PaperPage,
    PageMainQuestion,
    PageSubQuestion,
    TimeManagement, Blank,
)
from .forms import (
    MainQuestionForm,
    SubQuestionForm,
    CorrectionForm,
    SubQuestionFormSet,
    ChoiceOptionFormSet,
    MatchingOptionFormset,
    CorrectionFormSet
)
from Account.models import Students, Teachers, Class, Attendance, Course

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
        print('last_active_time updated.')
        if request.session.get('is_login', False):
            # 更新数据库中的最后活跃时间
            request.session['last_active_time'] = datetime.datetime.now().isoformat()
            # print('last_active_time', request.session['last_active_time'])
        return JsonResponse({"status": "success"})
    # 接受心跳机制数据
    if request.method == 'GET':
        # 如果用户已登录
        # print('expired.')
        # return redirect('logout')
        if request.session.get('is_login', False):
            this_datetime = datetime.datetime.now()
            if request.session.get('last_active_time', None):
                last_active_time = datetime.datetime.fromisoformat(request.session.get('last_active_time'))
                print(f'interval: {(this_datetime - last_active_time).total_seconds()}')
                if (this_datetime-last_active_time).total_seconds() > 60 * 10: #10分钟
                    # 心跳机制验证失败1，学生异常挂机
                    username = request.session.get('username')
                    student_instance = Students.objects.get(username=username)
                    class_instance = Class.objects.get(id=student_instance.class_instance_id)
                    start_date = datetime.date.fromisoformat(class_instance.start_date)
                    this_date = datetime.date.today()
                    start_datetime = datetime.datetime.combine(this_date, datetime.time.fromisoformat(class_instance.start_time))
                    end_datetime = datetime.datetime.combine(this_date, datetime.time.fromisoformat(class_instance.end_time))
                    this_datetime = datetime.datetime.now()
                    # 判断是否为上课时间
                    if ((this_date-start_date).days % 7 == 0) and ((this_datetime-start_datetime).total_seconds()>0) and ((end_datetime-this_datetime).total_seconds()>0):
                        week = (this_date-start_date).days // 7
                        attendance_instance = Attendance.objects.get(week=week, student_id=student_instance.id)
                        # 学生活跃异常，更新考勤状态为异常挂机
                        attendance_instance.status = 'abnormal'
                        attendance_instance.save()
                    print(f' 心跳机制验证失败1,超时登出')
                    return redirect('logout')
                else:
                    # 心跳机制验证成功，学生正常活动
                    print(f' 心跳机制验证成功，正常活动')
            else:
                # 心跳机制验证失败2，学生异常挂机
                print(f'心跳机制验证失败2,超时登出')
                return redirect('logout')
    return JsonResponse({"status": "error"}, status=400)

# 处理用户题库输入数据
'''
@csrf_exempt
def submit_question(request):
    if request.method == 'POST':
        print('Delete all in temtaskpackage and exit successfully.')
        models.TemMediaMaterial.objects.all().delete()
    return redirect('teacher_question_bank')
'''

# 登录板块
def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']
        request.session['last_active_time'] = datetime.datetime.now().isoformat()
        # 验证学生登录
        if role == 'student':
            # if models.Students.objects.filter(username=username).exists():
            if Students.objects.filter(username=username).exists():
                # 写入session
                request.session['role'] = 'student'
                request.session['username'] = username
                request.session['is_login'] = True
                print(f'{username}: Login.')

                # 存储学生登录信息
                time = datetime.datetime.now()
                user_agent = request.META.get('HTTP_USER_AGENT', '')# 获取用户的 User-Agent 信息，包括浏览器类型和引擎、操作系统信息、设备类型等信息
                models.LoginInfo.objects.create(
                    username=username,
                    action='login',
                    action_time=time,
                    last_active_time='',
                    device_info=user_agent,
                )
                '''
                start_date = datetime.date.fromisoformat('2024-12-22')
                today = datetime.date.today()
                between_days = (today - start_date).days
                start_time = datetime.time.fromisoformat('00:30:00')
                this_time = datetime.datetime.combine(today, start_time)
                now = datetime.datetime.now()
                between = (now - this_time).total_seconds()
                '''
                # 修改学生考勤状况
                student_instance = Students.objects.get(username=username)
                student_user = student_instance.user
                if student_user is not None:
                    login(request, student_user)

                class_instance = Class.objects.get(id=student_instance.class_instance_id)
                start_date = datetime.date.fromisoformat(class_instance.start_date)
                this_date = datetime.date.today()
                if ((this_date - start_date).days) % 7 == 0:

                    week = (this_date - start_date).days // 7
                    start_time = datetime.time.fromisoformat(class_instance.start_time)
                    end_time = datetime.time.fromisoformat(class_instance.end_time)
                    start_datetime = datetime.datetime.combine(this_date, start_time)
                    end_datetime = datetime.datetime.combine(this_date, end_time)
                    this_datetime = datetime.datetime.now()
                    interval = (this_datetime-start_datetime).total_seconds()
                    status = Attendance.objects.get(week=week, student_id=student_instance.id).status
                    # 对在考勤时间范围内且尚未登记考勤状态的学生进行考勤
                    if (interval >= -900) and (interval <= 900) and status == 'absent':
                        print('class time.')
                        student_id = student_instance.id
                        attendance_instance = Attendance.objects.get(student=student_id, week=week)
                        attendance_instance.status = 'normal'
                        attendance_instance.save()
                        print(f'normal attendance')
                    elif (interval > 900) and ((end_datetime-this_datetime).total_seconds() > 0) and status == 'absent':
                        student_id = student_instance.id
                        attendance_instance = Attendance.objects.get(student=student_id, week=week)
                        attendance_instance.status = 'late'
                        attendance_instance.save()
                        print(f'week{week}-{username}: late attendance')

                # 【待替换学生端页面】
                return redirect('student_ELW:student_index')
        # 验证教师登录
        if role == 'teacher':
            # if models.Teachers.objects.filter(username=username,password=password).exists():
            if Teachers.objects.filter(username=username,password=password).exists():
                request.session['role'] = 'teacher'
                request.session['username'] = username
                request.session['is_login'] = True
                request.session['teacher_name'] = Teachers.objects.get(username=username).name
                time = datetime.datetime.now()
                # 获取用户的 User-Agent 信息，包括浏览器类型和引擎、操作系统信息、设备类型等信息
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                models.LoginInfo.objects.create(
                    username=username,
                    action='login',
                    action_time=time,
                    last_active_time='',
                    device_info=user_agent,
                )
                # print(request.session['teacher_name'])
                teacher_instance = Teachers.objects.get(username=username)
                teacher_user = teacher_instance.user
                if teacher_user is not None:
                    login(request, teacher_user)
                return redirect('teacher_index')
        # 验证管理员登录
        if role == 'admin':
            if models.Admins.objects.filter(username=username).exists():
                request.session['role'] = 'admin'
                request.session['username'] = username
                request.session['is_login'] = True
                #【待替换管理员页面】
                # return HttpResponse('The main page of admin version should be shown here.')
                return redirect('/admin/')
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


def teacher_week_task(request):
    return render(request, 'teacher_side/week_task.html')

def teacher_week_task_package_add(request):
    if request.method == 'POST':
        # 全球唯一标识符
        media_uuid = uuid.uuid4().hex
        # 存储音频/视频
        media_file = request.FILES.get('media_file')
        media_file_path = os.path.join(settings.MEDIA_ROOT, 'media\\', media_uuid)
        media_url = os.path.join('\\media_material\\media\\', media_uuid)
        print('media_path: ', media_file_path)
        print('media_url: ', media_url)
        os.makedirs(os.path.dirname(media_file_path), exist_ok=True)
        with open(media_file_path, 'wb+') as destination:
            for chunk in media_file.chunks():
                destination.write(chunk)
        # 存储图片
        image_files = request.FILES.getlist('image_file')
        if image_files:
            image_urls = ''
            for image_file in image_files:
                image_file_path = os.path.join(f'{settings.MEDIA_ROOT}\\image\\{media_uuid}\\{image_file.name}')
                image_url = os.path.join(f'\\media_material\\image\\{media_uuid}\\{image_file.name}')
                print('image_path: ', image_file_path)
                print('image_url: ', image_url)
                image_urls = image_urls + image_url + ','
                os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
                with open(image_file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
            new_task_package = models.MediaMaterial.objects.create(
                title=request.POST.get('title'),
                theme=request.POST.get('theme'),
                abstract=request.POST.get('abstract'),
                keywords=request.POST.get('keywords'),
                transcript=request.POST.get('transcript'),
                media_url=media_url,
                image_url=image_urls,
            )
            print('new_task_package', new_task_package)
            id = new_task_package.id
            params = {'task_package_id': id}
            query_string = urlencode(params)
            url = reverse('teacher_week_file_import')
            return HttpResponseRedirect(f"{url}?{query_string}")
    return render(request, 'teacher_side/week_task_package_add.html')

def teacher_week_file_import(request):
    task_package_id = request.GET.get('task_package_id')
    print(f'task_package_id: {task_package_id}')

    # word文档导入
    if request.method == 'POST' and request.FILES.get('word_file'):
        def extract_text_from_word(doc_file):
            # 读取Word文档内容
            doc = Document(doc_file)
            text = ''
            for para in doc.paragraphs:
                text += para.text
            return text
        form = WordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            word_file = request.FILES['word_file']
            # 提取文本内容
            text_content = extract_text_from_word(word_file)
            print(f'text_content: {text_content}')
            # question_data = doc_func.main_process(text_content)

    form = WordUploadForm()
    return render(request, 'teacher_side/week_file_import.html', {'form': form})

# 题库管理
def teacher_question_bank(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                sub_id = int(data.get('question_id'))
                material_id = int(data.get('material_id'))

                # 在这里处理接收到的变量
                print(f"Received: sub_id: {sub_id}\n material_id: {material_id}")
                redirect_url = reverse('teacher_edit_question', args=[sub_id, material_id])
                # 返回 JSON 响应，包含重定向 URL
                return JsonResponse({'status': 'success', 'redirect_url': redirect_url})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        else:
            username = request.session.get('username', None)
            media_materials = MediaMaterial.objects.all()
            print('media_materials: ', media_materials)
            paginator = Paginator(media_materials, 15)  # 每页展示 15 条
            page_number = request.GET.get('page')  # 获取当前页码
            page_obj = paginator.get_page(page_number)  # 获取当前页对象
            # print((datetime.datetime.now() - datetime.datetime.fromisoformat(request.session.get('last_active_time'))).total_seconds() > 60)
            return render(request, 'teacher_side/question_bank.html',
                          {
                              'username': username,
                              'media_materials': media_materials,
                              'page_obj': page_obj,
                          })
    return redirect('login')

def teacher_delete_material(request, material_id):
    media_material = MediaMaterial.objects.get(id=material_id)
    media_material.delete()
    return redirect('teacher_question_bank')

def teacher_edit_question(request, sub_id, material_id):
    sub_question = SubQuestion.objects.get(id=sub_id)
    main_question = MainQuestion.objects.get(id=sub_question.main_question_id)
    media_material = MediaMaterial.objects.get(id=material_id)
    if sub_question.image_url:
        images = sub_question.image_url.split(',')
        print(images)
        return render(request, 'teacher_side/edit_question.html', {
            'main_question': main_question,
            'sub_question': sub_question,
            'media_material': media_material,
            'image': images,
        })
    return render(request, 'teacher_side/edit_question.html', {
        'main_question': main_question,
        'sub_question': sub_question,
        'media_material': media_material,
    })

def teacher_page_create(request, material_id):
    material = get_object_or_404(MediaMaterial, id=material_id)
    main_questions = material.main_questions.prefetch_related('sub_questions')
    pre_selected_questions = []
    # pre_selected_questions = [['sub_0', 'sub_0', 'sub_0']]

    if request.method == 'POST':
        print(request.POST)
        this_selected_questions = request.POST.getlist('questions')
        print('this_selected_questions: ', this_selected_questions)

        # test_selected_questions = ['sub_1', 'sub_2', 'sub_3']
        if request.POST['pre_selected_questions']:
            pre_selected_questions_json = request.POST.get('pre_selected_questions')
            try:
                # 将 JSON 字符串还原为 Python 对象
                pre_selected_questions = json.loads(pre_selected_questions_json)
                print('成功还原pre_selected_questions: ', pre_selected_questions)
            except json.JSONDecodeError:
                print("JSON 解析出错")
        '''
        # if request.POST['pre_selected_questions']:
            # try:
                # test_pre_selected_questions = request.POST['pre_selected_questions'] #json数据
                # print('received pre_selected_questions: ', test_pre_selected_questions)
                # pre_selected_questions = json.loads(pre_selected_questions)
                # print('test_type: ', pre_selected_questions.__class__)
                # print(f'pre_selected_questions: {pre_selected_questions}')
                # pre_selected_questions.append(test_selected_questions)
            # except json.JSONDecodeError:
            #     return JsonResponse({'status': 'error', 'message': 'JSON 解码失败'}, status=400)
        # else:
        #     pre_selected_questions = []
        #     pre_selected_questions.append(test_selected_questions)
        #     print(f'pre_selected_questions: {pre_selected_questions}')
        # pre_selected_questions.append(test_selected_questions)
        '''
        if 'add_page' in request.POST:      #如果点击的是“添加组卷”按钮
            print('add_page')
            print('this_selected_questions: ', this_selected_questions)
            if this_selected_questions:
                print('列表不为空，增加this_selected_questions至pre_selected_questions.')
                pre_selected_questions.append(this_selected_questions)
                print('增加后pre_selected_questions: ', pre_selected_questions)
            else:
                print('列表为空')

            preview_pages = []
            for pre_selected_question in pre_selected_questions:
                preview_page = pre_page.preview_page(pre_selected_question)
                preview_pages.append(preview_page)
            print('preview_pages: ', preview_pages)
            # print('receive: ', request.POST['pre_selected_questions'])

            return render(request, 'teacher_side/page_create.html', {
                'material': material,
                'main_questions': main_questions,
                'preview_pages': preview_pages,
                'pre_selected_questions': pre_selected_questions,

            })


        if 'preview' in request.POST:  # 如果点击的是“预览组卷”按钮
            print('preview')
            # 收集预览数据
            preview_data = []
            main_id_list = []
            for question_id in this_selected_questions:
                if question_id.startswith('main_'):  # 选中整到大题，为改错题
                    main_id = int(question_id.split('_')[1])
                    main_question = MainQuestion.objects.get(id=main_id)
                    # sub_questions = []
                    if main_question.question_type == 'correction':
                        sub_questions = ''
                        for sub_question in SubQuestion.objects.filter(main_question_id=main_question.id):
                            for correction in Correction.objects.filter(sub_question_id=sub_question.id):
                                question_text = sub_question.question_text
                                type = correction.type
                                index = correction.index
                                content = f'[{type}: {sub_question.answer}]'
                                print('content: ',content)
                                text_split = [text for text in question_text.split(' ') if text]
                                if type == 'insert':
                                    text_split.insert(index, content)
                                else:
                                    text_split.insert(index+1, content)
                                text_split = ' '.join(text_split)
                                sub_questions = sub_questions + ' ' + text_split
                        print('sub_questions: ', sub_questions)
                        preview_data.append({'type': 'main', 'question': main_question, 'sub_questions': sub_questions})
                elif question_id.startswith('sub_'):  # 处理小题
                    sub_id = int(question_id.split('_')[1])
                    sub_question = SubQuestion.objects.get(id=sub_id)
                    # 找到对应的大题
                    for data in preview_data:
                        if data['question'].id == sub_question.main_question.id:
                            data['sub_questions'].append(sub_question)
                            break
                    else:  # 如果没有找到，新增一个大题记录
                        preview_data.append({
                            'type': 'main',
                            'question': sub_question.main_question,
                            'sub_questions': [sub_question],
                        })
            print('preview_data: ', preview_data)
            return render(request, 'teacher_side/page_preview.html', {
                'material': material,
                'preview_data': preview_data,
                'this_selected_questions': this_selected_questions,  # 将选中的题目传递到预览页面
                'pre_selected_questions': pre_selected_questions,

            })

    return render(request, 'teacher_side/page_create.html', {
        'material': material,
        'main_questions': main_questions,
        'pre_selected_questions': pre_selected_questions,
    })

def teacher_page_save(request, material_id):
    if request.method == 'POST':

        username = request.session.get('username')
        teacher_instance = Teachers.objects.get(username=username)
        classes = Class.objects.filter(teacher_id=teacher_instance.id)
        if request.POST.get('selected_class'):
            preview_datas_json = request.POST.get('preview_datas')
            preview_datas = json.loads(preview_datas_json)
            print('data: ', request.POST)

            class_id = int(request.POST.get('selected_class'))
            order = request.POST.get('week')
            title = request.POST.get('title')
            type = request.POST.get('selected_type')
            if request.POST.get('exam_time'):
                duration = int(request.POST.get('exam_time'))
            if request.POST.get('exam_date'):
                exam_date = datetime.date.fromisoformat(request.POST.get('exam_date'))
                start_time = datetime.time.fromisoformat(request.POST.get('start_time'))
                end_time = datetime.time.fromisoformat(request.POST.get('end_time'))

            # 创建试卷
            class_instance = Class.objects.get(pk=class_id)
            unit_instance = Unit.objects.create(
                class_instance=class_instance,
                order=order,
                title=title,
                type=type,
            )
            unit_instance.save()
            print('unit_instance: ', unit_instance)
            # 如果为考试，则创建时间管理表
            if type == 'exam':
                time_management_instance = TimeManagement.objects.create(
                    unit=unit_instance,
                    duration=duration,
                    exam_date=exam_date,
                    start_time=start_time,
                    end_time=end_time,
                )
                time_management_instance.save()
            if type == 'quiz':
                time_management_instance = TimeManagement.objects.create(
                    unit=unit_instance,
                    week=order,
                    duration=duration,
                )
                time_management_instance.save()
            # 遍历所有待创建页面
            for order, preview_data in enumerate(preview_datas):
                # 创建页面
                page_instance = PaperPage.objects.create(
                    unit=unit_instance,
                    order=order,
                    text=f'第{order+1}个页面',
                )
                page_instance.save()
                main_id_list = []
                page_main_list = []
                for question_id in preview_data:
                    print('question_id: ', question_id)
                    if question_id.startswith('main_'):  # 大题,则为改错题
                        # 保存大题信息
                        main_id = int(question_id.split('_')[1])
                        main_instance = MainQuestion.objects.get(id=main_id)
                        page_main_instance = PageMainQuestion.objects.create(
                            page=page_instance,
                            main_question=main_instance,
                        )
                        page_main_instance.save()
                        main_id_list.append(main_instance.id)
                        page_main_list.append({'page_main_id': page_main_instance.id, 'main': main_id})
                        # 保存改错题小题
                        for sub_instance in SubQuestion.objects.filter(main_question_id=main_id):
                            page_sub_instance = PageSubQuestion.objects.create(
                                page_main_question=page_main_instance,
                                sub_question=sub_instance,
                            )
                            page_sub_instance.save()
                    elif question_id.startswith('sub_'):  # 小题
                        sub_id = int(question_id.split('_')[1])
                        sub_instance = SubQuestion.objects.get(id=sub_id)
                        main_instance = MainQuestion.objects.get(pk=sub_instance.main_question_id)
                        main_id = main_instance.id
                        if main_id in main_id_list:  # 已存在大题
                            for page_main in page_main_list:
                                if main_id == page_main['main']:
                                    page_main_instance = PageMainQuestion.objects.get(id=page_main['page_main_id'])
                                    page_sub_instance = PageSubQuestion.objects.create(
                                        page_main_question=page_main_instance,
                                        sub_question=sub_instance,
                                    )
                                    page_sub_instance.save()
                        else:
                            page_main_instance = PageMainQuestion.objects.create(
                                page=page_instance,
                                main_question=main_instance,
                            )
                            page_main_instance.save()
                            main_id_list.append(main_instance.id)
                            page_main_list.append({'page_main_id': page_main_instance.id, 'main': main_id})
                            page_sub_instance = PageSubQuestion.objects.create(
                                page_main_question=page_main_instance,
                                sub_question=sub_instance,
                            )
                            page_sub_instance.save()
            return redirect('teacher_question_bank')
        else:
            preview_datas_json = request.POST.get('preview_datas')
            return render(request, 'teacher_side/unit_create.html', {
                'preview_datas_json': preview_datas_json,
                'classes': classes,
            })

'''
        selected_questions = request.POST.getlist('selected_questions')  # 从预览页面获取选中的题目
        print('teacher_page_save receive selected_questions.')
        print('selected_questions: ', selected_questions)
        # 创建试卷
        class_instance = Class.objects.get(pk=1)
        unit_instance = Unit.objects.create(
            class_instance=class_instance,
            order = 1,
            title = 'test',
            type = 'practice',
        )
        # unit_instance.save()
        print('unit_instance: ', unit_instance)
        order = 0  # 页面顺序
        main_id_list = []
        page_main_list = []
        for question_id in selected_questions:
            print('question_id: ', question_id)
            if question_id.startswith('main_'):  # 大题,则为改错题
                # 为大题创建页面
                page_instance = PaperPage.objects.create(
                    unit=unit_instance,
                    order=order,
                    text=f'第{order}个页面',
                )
                page_instance.save()
                # 保存大题信息
                main_id = int(question_id.split('_')[1])
                main_instance = MainQuestion.objects.get(id=main_id)
                page_main_instance = PageMainQuestion.objects.create(
                    page = page_instance,
                    main_question = main_instance,
                )
                page_main_instance.save()
                main_id_list.append(main_instance.id)
                page_main_list.append({'page_main_id': page_main_instance.id, 'main': main_id})
                # 保存改错题小题
                for sub_instance in SubQuestion.objects.filter(main_question_id=main_id):
                    page_sub_instance = PageSubQuestion.objects.create(
                        page_main_question = page_main_instance,
                        sub_question = sub_instance,
                    )
                    page_sub_instance.save()
                order += 1
            elif question_id.startswith('sub_'):  # 小题
                sub_id = int(question_id.split('_')[1])
                sub_instance = SubQuestion.objects.get(id=sub_id)
                main_instance = MainQuestion.objects.get(pk=sub_instance.main_question_id)
                main_id = main_instance.id
                if main_id in main_id_list:
                    for page_main in page_main_list:
                        if main_id == page_main['main']:    #已存在大题
                            page_main_instance = PageMainQuestion.objects.get(id=page_main['page_main_id'])
                            page_sub_instance = PageSubQuestion.objects.create(
                                page_main_question = page_main_instance,
                                sub_question = sub_instance,
                            )
                            page_sub_instance.save()
                else:
                    # 为大题创建页面
                    page_instance = PaperPage.objects.create(
                        unit=unit_instance,
                        order=order,
                        text='test',
                    )
                    page_instance.save()
                    order += 1
                    page_main_instance = PageMainQuestion.objects.create(
                        page=page_instance,
                        main_question=main_instance,
                    )
                    page_main_instance.save()
                    main_id_list.append(main_instance.id)
                    page_main_list.append({'page_main_id': page_main_instance.id, 'main': main_id})
                    page_sub_instance = PageSubQuestion.objects.create(
                        page_main_question=page_main_instance,
                        sub_question=sub_instance,
                    )
                    page_sub_instance.save()
        '''
        # return redirect('teacher_question_bank')


        # 保存题目到试卷


        # return redirect('exam_paper_list')  # 重定向到试卷列表页

# 查看素材包
def teacher_media_material_detail(request, material_id):
    if request.method == 'POST':
        images = request.FILES.getlist('sub_images')  # 获取所有上传的文件
        data = request.POST
        print('data: ', data)

        sub_id = data.get('sub_question_id')
        sub_instance = SubQuestion.objects.get(id=sub_id)
        main_instance = MainQuestion.objects.get(id=sub_instance.main_question_id)
        question_text = data.get('sub_question_text')
        tips = data.get('sub_question_tips')
        analysis = data.get('sub_question_analysis')
        if data.get('new_sub_question_answer'):
            answer = data.get('new_sub_question_answer')
        else:
            answer = data.get('sub_question_answer')
        if main_instance.question_type == 'choice':
            option_count = data.get('option_count')
            print('option_count: ', option_count)



    material = get_object_or_404(MediaMaterial, id=material_id)
    main_questions = material.main_questions.all()
    # 获取大题下的小题
    sub_questions = {}
    for question in main_questions:
        sub_questions[question.id] = question.sub_questions.all()
        print('sub: ', sub_questions[question.id])
    return render(request, 'teacher_side/media_material_detail.html', {
        'material': material,
        'main_questions': main_questions,
        'sub_questions': sub_questions,
    })

# 添加题目
def teacher_question_add(request):
    return render(request, 'teacher_side/question_add.html')

# 添加素材包
def teacher_task_package_add(request):
    # 提交的表单有数据，则为填写表单后提交的网页
    '''
    if request.method == 'POST' and request.POST.keys():
        form = UploadMediaForm(request.POST, request.FILES)
        # 表单合法，存储表单数据至临时库
        if form.is_valid():
            print('valid')
            # 【处理文件保存逻辑（【待替换】需要保存到数据库，在这里创建 UploadedMedia 实例）】
            media_file = request.FILES.get('media_file')
            media_uuid =uuid.uuid4().hex
            media_file_path = os.path.join(settings.MEDIA_ROOT, 'media_material/', media_uuid)
            os.makedirs(os.path.dirname(media_file_path), exist_ok=True)
            with open(media_file_path, 'wb+') as destination:
                for chunk in media_file.chunks():
                    destination.write(chunk)

            # 处理多张图片
            # image_files = request.FILES.getlist('image_file')
            # for image_file in image_files:
            #     print("Image file:", image_file.name)

            image_file = request.FILES.get('image_file')
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
                    media_url = 'media_material/' + media_uuid,
                    image_url = 'image/' + image_uuid,
                )
                id = new_task_package.id
                params = {'task_package_id': id}
                query_string = urlencode(params)
                url = reverse('question_integration')
                return HttpResponseRedirect(f"{url}?{query_string}")
            new_task_package = models.MediaMaterial.objects.create(
                title=request.POST.get('title'),
                theme=request.POST.get('theme'),
                abstract=request.POST.get('abstract'),
                keywords=request.POST.get('keywords'),
                transcript=request.POST.get('transcript'),
                media_url='media_material/' + media_uuid,
            )
            id = new_task_package.id
            print('Received all task_package_info successfully.')
            # return render(request, 'teacher_side/question_add.html')    #替换为待跳转页面
            params = {'task_package_id': id}
            query_string = urlencode(params)
            # url = reverse('create_big_question_with_small_questions')
            # url = reverse('teacher_question_type')
            url = reverse('question_integration')
            return HttpResponseRedirect(f"{url}?{query_string}")
            # return redirect('teacher_question_add')

        else:
            # 打印表单错误信息
            print("表单验证失败，错误信息：", form.errors)
    '''

    if request.method == 'POST':
        # 全球唯一标识符
        media_uuid = uuid.uuid4().hex
        # 存储音频/视频
        media_file = request.FILES.get('media_file')
        media_file_path = os.path.join(settings.MEDIA_ROOT, 'media\\', media_uuid)
        media_url = os.path.join('\\media_material\\media\\', media_uuid)
        print('media_path: ', media_file_path)
        print('media_url: ', media_url)
        os.makedirs(os.path.dirname(media_file_path), exist_ok=True)
        with open(media_file_path, 'wb+') as destination:
            for chunk in media_file.chunks():
                destination.write(chunk)
        # 存储图片
        image_files = request.FILES.getlist('image_file')
        if image_files:
            image_urls = ''
            for image_file in image_files:
                image_file_path = os.path.join(f'{settings.MEDIA_ROOT}\\image\\{media_uuid}\\{image_file.name}')
                image_url = os.path.join(f'\\media_material\\image\\{media_uuid}\\{image_file.name}')
                print('image_path: ', image_file_path)
                print('image_url: ', image_url)
                image_urls = image_urls + image_url + ','
                os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
                with open(image_file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
            new_task_package = models.MediaMaterial.objects.create(
                title=request.POST.get('title'),
                theme=request.POST.get('theme'),
                abstract=request.POST.get('abstract'),
                keywords=request.POST.get('keywords'),
                transcript=request.POST.get('transcript'),
                media_url=media_url,
                image_url=image_urls,
            )
            print('new_task_package', new_task_package)
            id = new_task_package.id
            params = {'task_package_id': id}
            query_string = urlencode(params)
            url = reverse('question_integration')
            return HttpResponseRedirect(f"{url}?{query_string}")



    # 表单无数据，为初次跳转网页
    print('first fetch at task_package_add.html')
    # form = UploadMediaForm()
    return render(request, 'teacher_side/task_package_add.html')

def teacher_question_type(request):
    task_package_id = request.GET.get('task_package_id')
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        params = {
            'task_package_id': task_package_id,
            'question_type': question_type,
        }
        query_string = urlencode(params)
        if question_type == 'choice':
            url = reverse('teacher_choice')
            return HttpResponseRedirect(f"{url}?{query_string}")
        if question_type == 'matching':
            url = reverse('teacher_matching')
            return HttpResponseRedirect(f"{url}?{query_string}")
        if question_type == 'correction':
            url = reverse('teacher_correction')
            return HttpResponseRedirect(f"{url}?{query_string}")
        if question_type == 'test':
            url = reverse('teacher_integration')
            return HttpResponseRedirect(f"{url}?{query_string}")

        # return HttpResponse(question_type)
        print('document')
    return render(request, 'teacher_side/question_type.html')

# 选择题choice.html
def teacher_choice(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')

    # 按题号分割题目，返回包含各个题目的列表，题号格式为(1)
    def extract_questions(text):
        # 使用正则表达式匹配题号，支持中文括号和英文括号，题号格式为(1)
        question_pattern = r'[\(\（]\d+[\)\）]'
        # 找到所有匹配的题号位置
        question_indices = [m.start() for m in re.finditer(question_pattern, text)]
        # 确保有题号
        if not question_indices:
            return []
        # 结果列表
        questions = []
        # 逐一分割题目
        for i in range(len(question_indices)):
            start_index = question_indices[i]
            # 如果是最后一个题目，取到文本结束
            end_index = question_indices[i + 1] if i + 1 < len(question_indices) else len(text)
            # 获取题目的文本
            question_text = text[start_index:end_index].strip()
            # 移除题号
            question_text = re.sub(r'^[\(\（]\d+[\)\）]', '', question_text).strip()
            questions.append(question_text)
        return questions

    # 提取各个问题的信息
    def process_question(question):
        # 移除转义序列 \r\n\t
        question = question.replace('\n', '').replace('\r', '').replace('\t', '')
        # 默认值
        question_data = {
            'question_text': '',
            'score': 1.0,
            'label_count': 0,
            'A': '',
            'B': '',
            'C': '',
            'D': '',
            'answer': [],
            'tips': '',
            'analysis': ''
        }
        # 1. 优先匹配 '$数字$' 格式符号
        score_match = re.search(r'\$(\d+)\$', question)
        if score_match:
            # 如果找到 '$数字$'，则提取题干到该符号之前
            question_data['question_text'] = question[:score_match.start()].strip()
            question_data['score'] = float(score_match.group(1))
        else:
            # 2. 如果没有 '$数字$' 格式符号，检查是否存在 '[$A]' 格式
            option_match = re.search(r'\[\$([A-D])\]', question)  # 寻找 '[$A]', '[$B]' 等格式
            if option_match:
                # 如果找到 '[$A]' 格式，提取到该选项之前
                question_data['question_text'] = question[:option_match.start()].strip()
            else:
                # 如果没有 '[$A]' 格式，寻找 '[A]' 格式
                option_match = re.search(r'\[([A-D])\]', question)  # 寻找 '[A]', '[B]' 等格式
                if option_match:
                    # 提取到第一个 '[A]' 格式选项之前
                    question_data['question_text'] = question[:option_match.start()].strip()

        # 提取选项
        options = re.findall(r'([A-D])\]([^\[\n]+)', question)
        for label, option in options:
            question_data[label] = option.strip()
            question_data['label_count'] += 1

        # 提取答案 (假设答案是以[$X]格式给出的)
        answer_match = re.findall(r'\[\$(\w+)\]', question)
        question_data['answer'] = answer_match

        # 提取tips
        tips_match = re.search(r'\[tips:([^\]]+)\]', question)
        if tips_match:
            question_data['tips'] = tips_match.group(1).strip()

        # 提取analysis
        analysis_match = re.search(r'\[analysis:([^\]]+)\]', question)
        if analysis_match:
            question_data['analysis'] = analysis_match.group(1).strip()
        print(f'question_data: {question_data}')
        return question_data

    if request.method == 'POST':
        main_text = request.POST.get('MainQuestion')
        sub_text = request.POST.get('SubQuestion')

        # print(f'main_text: {main_text}')
        # print(f'sub_text: {sub_text}')
        question_list = extract_questions(sub_text)
        print('question_list: ', question_list)
        question_info = []
        for question in question_list:
            question_info.append(process_question(question))
        print('question_info: ', question_info)

        # 存储大题
        media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
        main_instance = MainQuestion(
            media_material=media_material_instance,
            question_type = question_type,
            question_text = main_text,
        )
        main_instance.save()
        # 存储小题
        label_list = ['A', 'B', 'C', 'D']
        for sub_info in question_info:
            question_text = sub_info.get('question_text')
            score = sub_info.get('score')
            label_count = sub_info.get('label_count')
            answer = sub_info.get('answer')
            tips = sub_info.get('tips')
            analysis = sub_info.get('analysis')
            sub_instance = SubQuestion(
                main_question=main_instance,
                main_question_id = main_instance.id,
                question_text = question_text,
                score = score,
                answer = answer,
                tips = tips,
                analysis = analysis,
            )
            sub_instance.save()
            for i in range(label_count):
                option_label = label_list[i]
                if option_label in answer:
                    is_answer = True
                else:
                    is_answer = False
                choice_option_instance = ChoiceOption(
                    sub_question=sub_instance,
                    sub_question_id = sub_instance.id,
                    option_label = option_label,
                    option_content = sub_info.get(option_label),
                    is_answer = is_answer,
                )
                choice_option_instance.save()
    return render(request, 'teacher_side/choice.html',)

# 改错题correction_test3.html
def teacher_correction(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')

    def parse_text_modifications(input_text):
        # 正则匹配 [text:type:answer]
        pattern = r'\[([^:]*):([^:]*):([^]]+)\]'
        matches = re.finditer(pattern, input_text)
        print('matches: ', matches)
        # 初始化结果变量
        sub_list = [] #小题题干
        text_list = [] #需要改错的原小题文本
        type_list = [] #改错类型
        answer_list = [] #答案
        index_list = [] #修订部分在原文本中的单词索引，以空格为分隔符
        last_end = 0 # 分割点初始化
        word_index = 0  # 当前单词索引

        # 遍历匹配
        for match in matches:
            text, op_type, answer = match.groups()
            start, end = match.span()
            # before_text = input_text[last_end:start]
            # sub_list.append(before_text)
            # 处理 type, answer 和 index
            text_list.append(text.strip())
            type_list.append(op_type.strip())
            answer_list.append(answer.strip())
            last_end = end # 更新 last_end

        #提取原文本中修订文本的前缀和后缀
        def extract_prefix_suffix(input_string):
            pattern = re.compile(r'(.*?)\[(.*?)\](.*)')
            match = pattern.match(input_string)
            if match:
                prefix = match.group(1).strip()
                suffix = match.group(3).strip()
            else:
                prefix = ''
                suffix = ''
            return prefix, suffix
        split_texts = input_text.split()
        print('split_texts: ', split_texts)
        before_text = ''
        index = 0
        ignore_count = 0 #当修改类型为insert时，修订部分在原文本中的单词索引为插入位置的前一个单词的索引，因此在原文中不占据索引位置
        match_count = 0
        insert_pattern =  r'.*:insert:.*' #判断修订类型为insert的题目
        for i, split_text in enumerate(split_texts):
            print(f"{i}: {split_text}")
            if re.search(pattern, split_text):
                match_count += 1
                prefix = extract_prefix_suffix(split_text)[0]
                suffix = extract_prefix_suffix(split_text)[1]
                if re.search(insert_pattern, split_text):
                    print('find insert')
                    ignore_count += 1
                    index_list.append(index - ignore_count)
                    before_text = before_text + prefix + suffix + ' '
                    sub_list.append(before_text)
                    before_text = ''
                    index += 1
                else:
                    before_text = before_text + prefix + text_list[match_count - 1] + suffix + ' '
                    print('test: ', text_list[match_count-1])
                    index_list.append(index-ignore_count)
                    print('match example: ', split_texts[index + ignore_count])
                    sub_list.append(before_text)
                    before_text = ''
                    index += 1
            else:
                before_text = before_text + split_text + ' '
                index += 1
        # 处理最后一段普通文本
        if last_end < len(input_text):
            sub_list[-1]=sub_list[-1] + input_text[last_end:]
            # sub_list.append(input_text[last_end:])
        # 返回结果
        return {
            'sub_list': sub_list,
            'text_list': text_list,
            'type_list': type_list,
            'answer_list': answer_list,
            'index_list': index_list
            # 'split_texts': split_texts,
        }

    if request.method == "POST":
        main_text = request.POST.get('MainQuestion')
        sub_text = request.POST.get('SubQuestion')
        print('data: ', request.POST)
        print('main_text: ', main_text)
        print('sub_text: ', sub_text)
        # 输入的改错题模板文本
        text = sub_text

        # 调用函数
        result = parse_text_modifications(text)
        sub_list = result['sub_list']
        text_list = result['text_list']
        type_list = result['type_list']
        answer_list = result['answer_list']
        index_list = result['index_list']
        # split_texts = result['split_texts']
        print('sub_list: ', sub_list)
        print('text_list: ', text_list)
        print('type_list: ', type_list)
        print('answer_list: ', answer_list)
        print('index_list: ', index_list)
        # print('split_texts: ', split_texts)
        # return HttpResponse(result)

        # 存储大题
        media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
        main_instance = MainQuestion(
            media_material = media_material_instance,
            question_type = question_type,
            question_text = main_text,
        )
        main_instance.save()
        for i in range(len(sub_list)):
            # 存储小题
            sub_instance = SubQuestion(
                main_question = main_instance,
                main_question_id = main_instance.id,
                question_text = sub_list[i],
                answer = answer_list[i],
            )
            sub_instance.save()
            correction_instance = Correction(
                sub_question = sub_instance,
                type = type_list[i],
                index = index_list[i],
            )
            correction_instance.save()
    return render(request, 'teacher_side/correction_test3.html')

# 连线题matching_test1.html
def teacher_matching(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')

    # 按题号分割题目，返回包含各个题目的列表
    def extract_questions(text):
        # 正则表达式匹配题号部分（支持中文和英文括号）,匹配的内容是：(1) 或 （1） 这种格式的题号
        pattern = r'([（(]\d+[）)])'
        # 按题号进行分割
        question_parts = re.split(pattern, text)
        print('question_parts: ', question_parts)
        # 移除空字符串，并将每个题目重新组合成题号 + 题目内容
        questions = []
        for i in range(1, len(question_parts), 2):
            # question_number = question_parts[i].strip()
            # print(f'question_number{i}: {question_number}')
            question_text = question_parts[i + 1].strip()
            print(f'question_text{i}: {question_text}')
            # 合并题号和题目内容
            # full_question = f"{question_number}{question_text}"
            # print(f'full_question{i}: {full_question}')
            questions.append(question_text)
        return questions

    # 提取各个问题的信息
    def process_question(question_text):
        # 移除转义序列 \r\n\t
        question_text = question_text.replace('\r\n', '').replace('\n', '').replace('\r', '').replace('\t', '')
        print('question_text: ', question_text)
        result = {
            'question_text': '',
            'score': '',
            'option_label': '',
            'option_content': '',
            'tips': '',
            'analysis': ''
        }
        # 判断题目中是否包含 $数字$ 格式的分数
        score_match = re.search(r'\$(\d+(\.\d+)?)\$', question_text)
        if score_match:
            # 如果包含 $数字$ 格式，则提取 $数字$ 前的部分作为题干
            question_text_match = re.match(r'([^\$]+)', question_text)
            if question_text_match:
                result['question_text'] = question_text_match.group(1).strip()
            result['score'] = score_match.group(1)
        else:
            # 如果不包含 $数字$ 格式，则提取到第一个选项[A]或[B]等选项之前的部分作为题干
            question_text_match = re.match(r'([^\[]+)', question_text)
            if question_text_match:
                result['question_text'] = question_text_match.group(1).strip()
            result['score'] = '1.0'  # 如果没有指明分值，则返回默认分值1.0
        # 提取选项标签和选项内容 (格式: [A] A website)
        option_match = re.search(r'\[([A-Z])\](.*?)\s*(?=\[|$)', question_text)
        if option_match:
            result['option_label'] = option_match.group(1)
            result['option_content'] = option_match.group(2).strip()
        # 提取提示 (格式: [tips: some tips])
        tips_match = re.search(r'\[tips:([^\[]+)\]', question_text)
        if tips_match:
            result['tips'] = tips_match.group(1).strip()
        else:
            result['tips'] = ''  # 若没有提示，返回空值
        # 提取分析 (格式: [analysis: something])
        analysis_match = re.search(r'\[analysis:([^\[]+)\]', question_text)
        if analysis_match:
            result['analysis'] = analysis_match.group(1).strip()
        else:
            result['analysis'] = ''  # 若没有分析，返回空值
        return result

    if request.method == "POST":
        main_text = request.POST.get('MainQuestion')
        sub_text = request.POST.get('SubQuestion')
        print('main_text: ', main_text)
        print('sub_text: ', sub_text)
        print('-'*20)
        questions = extract_questions(sub_text)
        print('questions: ', questions)
        question_info = []
        for question in questions:
            question_info.append(process_question(question))
        print('question_info: ', question_info)

        # 存储大题
        media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
        main_instance = MainQuestion(
            media_material=media_material_instance,
            question_text = main_text,
            question_type = question_type,
        )
        main_instance.save()
        for sub_info in question_info:
            question_text = sub_info.get('question_text')
            tips = sub_info.get('tips')
            analysis = sub_info.get('analysis')
            answer = sub_info.get('option_label')
            score = sub_info.get('score')
            option_label = sub_info.get('option_label')
            option_content = sub_info.get('option_content')
            # 存储小题
            sub_instance = SubQuestion(
                main_question = main_instance,
                main_question_id = main_instance.id,
                question_text = question_text,
                tips = tips,
                analysis = analysis,
                answer = answer,
                score = score,
            )
            sub_instance.save()
            # 存储选项
            matching_instance = MatchingOption(
                sub_question = sub_instance,
                option_label = option_label,
                option_content = option_content,
            )
            matching_instance.save()
    return render(request, 'teacher_side/matching_test1.html')

def question_integration(request):
    task_package_id = request.GET.get('task_package_id')
    '''
    start_time = datetime.time.fromisoformat("00:30:00").isoformat()
    end_time = datetime.time.fromisoformat("14:00:00").isoformat()
    print(start_time)
    print(type(start_time))

    current_date = datetime.date.today()
    # 创建 datetime 对象，结合当前日期和时间
    start_datetime = datetime.datetime.combine(current_date, datetime.time.fromisoformat("15:30:00"))
    print(start_datetime.isoformat())
    '''
    # word文档导入
    if request.method == 'POST' and request.FILES.get('word_file'):
        def extract_text_from_word(doc_file):
            # 读取Word文档内容
            doc = Document(doc_file)
            text = ''
            for para in doc.paragraphs:
                text += para.text
            return text

        form = WordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            word_file = request.FILES['word_file']
            # 提取文本内容
            text_content = extract_text_from_word(word_file)
            # question_data = []
            # questions = doc_func.extract_questions(text_content)
            # for question in questions:
            #     main_question = doc_func.parse_main_question(question)
            #     question_data.append(main_question)
            #     print('main_question: ', main_question)
            question_data = doc_func.main_process(text_content)

            # 将每道改错题的sub_list、type_list、answer_list、index_list合并为一个列表，列表中每个集合包含这四个值
            for main_question in question_data:
                if main_question['question_type'] == 'correction':
                    for sub_question in main_question['sub_questions']:
                        sub_question['questions'] = []
                        for i in range(len(sub_question['sub_list'])):
                            sub_question['questions'].append({
                                'sub': sub_question['sub_list'][i],
                                'type': sub_question['type_list'][i],
                                'answer': sub_question['answer_list'][i],
                                'index': sub_question['index_list'][i]
                            })

            print('question_data: ', question_data)
            return render(request, 'teacher_side/question_preview.html', {'question_data': question_data})
        else:
            return JsonResponse({'status': 'error', 'message': '文件上传失败'})

    # 传统表单导入
    elif request.method == 'POST':
        question_type = request.POST.get('question_type')
        # 处理预览
        if 'preview' in request.POST:
            main_text = request.POST.get('MainQuestion')
            sub_text = request.POST.get('SubQuestion')
            main_info = func.extract_main_question(main_text)

            question_data = [{
                "question_type": question_type,
                "question_text": main_info.get('question_text'),
                "score": main_info.get('score'),
                "min": main_info.get('min'),
                "max": main_info.get('max'),
                "start": main_info.get('start'),
                "end": main_info.get('end'),
                "sub_questions": []
            }]

            if question_type == 'choice':
                question_list = func.extract_sub_questions(sub_text)
                for question in question_list:
                    question_data[0]["sub_questions"].append(func.process_choice_question(question))

            if question_type == 'correction':
                result = func.parse_text_modifications(sub_text)
                question_data[0]["sub_questions"].append(result)
                for sub_question in question_data[0]['sub_questions']:
                    sub_question['questions'] = []
                    for i in range(len(sub_question['sub_list'])):
                        sub_question['questions'].append({
                            'sub': sub_question['sub_list'][i],
                            'type': sub_question['type_list'][i],
                            'answer': sub_question['answer_list'][i],
                            'index': sub_question['index_list'][i]
                        })

            if question_type == 'matching':
                # questions = func.extract_matching_questions(sub_text)
                questions = func.extract_sub_questions(sub_text)
                for question in questions:
                    question_data[0]["sub_questions"].append(func.process_matching_question(question))

            if question_type == 'comprehension':
                question_list = func.extract_sub_questions(sub_text)
                for question in question_list:
                    question_data[0]["sub_questions"].append(func.process_comprehension_question(question))

            if question_type == 'blank':
                questions = func.extract_sub_questions(sub_text)
                for question in questions:
                    question_data[0]["sub_questions"].append(func.extract_subtext_and_answers(question))

            return render(request, 'teacher_side/question_preview.html', {"question_data": question_data})

        # 处理保存逻辑
        if 'save' in request.POST:
            # 把POST数据转为字典
            post_data = request.POST.dict()
            print(request.POST)

            main_data = {}
            for key in post_data:
                if key.startswith('main['):
                    parts = key.split('.')
                    main_idx = int(parts[0][5:-1])
                    field_path = parts[1:]

                    # 构建嵌套字典结构
                    current = main_data.setdefault(main_idx, {})
                    for part in field_path[:-1]:
                        if '[' in part:
                            name, idx = part[:-1].split('[')
                            idx = int(idx)
                            current = current.setdefault(name, {}).setdefault(idx, {})
                        else:
                            current = current.setdefault(part, {})
                    current[field_path[-1]] = post_data[key]

            # 遍历所有大题
            for main_idx, main_item in main_data.items():
                # 保存大题
                media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
                main_instance = MainQuestion(
                    media_material=media_material_instance,
                    question_type=main_item.get('question_type'),
                    question_text=main_item.get('main_question_text'),
                    maximum_play=main_item.get('max') if main_item.get('max') else 3,
                    minimum_play=main_item.get('min') if main_item.get('min') else 1,
                    start_time=datetime.time.fromisoformat(main_item.get('start')) if main_item.get('start') else None,
                    end_time=datetime.time.fromisoformat(main_item.get('end')) if main_item.get('end') else None,
                    allow_pause = str(main_item.get('allow_pause', 'false')).lower() == 'true',
                    limited_time=datetime.time.fromisoformat(main_item.get('limited_time')) if main_item.get('limited_time') else None
                )
                main_instance.save()

                # 保存改错题
                if main_item['question_type'] == 'correction':
                    for sub_idx, sub_item in main_item.get('sub', {}).items():
                        for corr_idx, correction in sub_item.get('corrections', {}).items():
                            sub_question = SubQuestion(
                                main_question=main_instance,
                                question_text=correction.get('question_text'),
                                score=correction.get('score'),
                                answer=correction.get('answer'),
                                tips=correction.get('tips'),
                                analysis=correction.get('analysis')
                            )
                            sub_question.save()
                            correction_instance = Correction(
                                sub_question=sub_question,
                                type=correction.get('correction_type'),
                                index=correction.get('index'),
                            )
                            correction_instance.save()
                # 保存填空题
                elif main_item.get('question_type') == 'blank':
                    for sub_idx, sub_item in main_item.get('sub', {}).items():
                        for blank_idx, blank in sub_item.get('blanks', {}).items():
                            sub_question = SubQuestion(
                                main_question=main_instance,
                                question_text=blank.get('question_text'),
                                score=blank.get('score'),
                                answer=blank.get('answer'),
                                tips=blank.get('tips'),
                                analysis=blank.get('analysis')
                            )
                            sub_question.save()
                            blank_instance = Blank(
                                sub_question=sub_question,
                                index=blank.get('index')
                            )
                            blank_instance.save()
                else:
                    for sub_idx, sub_item in main_item.get('sub', {}).items():
                        sub_question = SubQuestion(
                            main_question=main_instance,
                            question_text=sub_item.get('question_text'),
                            score=sub_item.get('score'),
                            answer=sub_item.get('answer'),
                            tips=sub_item.get('tips'),
                            analysis=sub_item.get('analysis')
                        )
                        sub_question.save()

                        # 保存选择题
                        if main_item['question_type'] == 'choice':
                            label_list = ['A', 'B', 'C', 'D']
                            label_count = int(sub_item.get('label_count'))
                            for i in range(label_count):
                                option_label = label_list[i]
                                option_content = sub_item.get(option_label)

                                if option_content:
                                    is_answer = option_label in sub_item.get('answer')  # 判断是否为答案
                                    choice_option = ChoiceOption(
                                        sub_question=sub_question,
                                        option_label=option_label,
                                        option_content=option_content,
                                        is_answer=is_answer
                                    )
                                    choice_option.save()

                        # 保存连线题
                        elif main_item['question_type'] == 'matching':
                            matching_instance = MatchingOption(
                                sub_question=sub_question,
                                option_label=sub_item.get('option_label'),
                                option_content=sub_item.get('option_content'),
                            )
                            matching_instance.save()
            return redirect('teacher_question_bank')

    form = WordUploadForm()
    return render(request, 'teacher_side/question_integration.html', {'form': form,})

# question_integration.html (test整合页面)
#
# def question_integration(request):
#     task_package_id = request.GET.get('task_package_id')
#     '''
#     start_time = datetime.time.fromisoformat("00:30:00").isoformat()
#     end_time = datetime.time.fromisoformat("14:00:00").isoformat()
#     print(start_time)
#     print(type(start_time))
#
#     current_date = datetime.date.today()
#     # 创建 datetime 对象，结合当前日期和时间
#     start_datetime = datetime.datetime.combine(current_date, datetime.time.fromisoformat("15:30:00"))
#     print(start_datetime.isoformat())
#     '''
#     if request.method == 'POST' and request.FILES.get('word_file'):
#         def extract_text_from_word(doc_file):
#             # 读取Word文档内容
#             doc = Document(doc_file)
#             text = ''
#             for para in doc.paragraphs:
#                 text += para.text
#             return text
#
#         form = WordUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             word_file = request.FILES['word_file']
#             # 提取文本内容
#             text_content = extract_text_from_word(word_file)
#             question_data = []
#             questions = doc_func.extract_questions(text_content)
#             for question in questions:
#                 main_question = doc_func.parse_main_question(question)
#                 question_data.append(main_question)
#                 print('main_question: ', main_question)
#             print('question_data: ', question_data)
#             return JsonResponse({'status': 'success', 'text': text_content})
#         else:
#             return JsonResponse({'status': 'error', 'message': '文件上传失败'})
#
#     elif request.method == 'POST':
#         question_type = request.POST.get('question_type')
#         main_text = request.POST.get('MainQuestion')
#         sub_text = request.POST.get('SubQuestion')
#         print('sub_text: ', sub_text)
#         main_info = func.extract_main_question(main_text)
#         score = main_info['score']
#         print('main_info: ', main_info)
#
#         # 存储大题
#         '''
#
#         media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
#         main_instance = MainQuestion(
#             media_material=media_material_instance,
#             question_type=question_type,
#             question_text=main_info.get('question_text'),
#             maximum_play=main_info.get('max') if main_info.get('max') else 3,
#             minimum_play=main_info.get('min') if main_info.get('min') else 1,
#             start_time=datetime.time.fromisoformat(main_info.get('start')) if main_info.get('start') else None,
#             end_time=datetime.time.fromisoformat(main_info.get('end')) if main_info.get('end') else None,
#         )
#         main_instance.save()
#         '''
#
#
#
#         # 选择题（单选+多选）
#         if question_type == 'choice':
#             question_list = func.extract_choice_questions(sub_text)
#             print('question_list: ', question_list)
#             question_info = []
#             for question in question_list:
#                 question_info.append(func.process_choice_question(question))
#             print('question_info: ', question_info)
#
#             # 存储小题
#             '''
#             label_list = ['A', 'B', 'C', 'D']
#             for sub_info in question_info:
#                 question_text = sub_info.get('question_text')
#                 label_count = sub_info.get('label_count')
#                 answer_list = sub_info.get('answer')
#                 tips = sub_info.get('tips')
#                 analysis = sub_info.get('analysis')
#                 answer = ''
#                 for asw in answer_list:
#                     answer += asw
#
#                 sub_instance = SubQuestion(
#                     main_question=main_instance,
#                     main_question_id=main_instance.id,
#                     question_text=question_text,
#                     score=score,
#                     answer=answer,
#                     tips=tips,
#                     analysis=analysis,
#                 )
#                 sub_instance.save()
#                 for i in range(label_count):
#                     option_label = label_list[i]
#                     if option_label in answer:
#                         is_answer = True
#                     else:
#                         is_answer = False
#                     choice_option_instance = ChoiceOption(
#                         sub_question=sub_instance,
#                         sub_question_id=sub_instance.id,
#                         option_label=option_label,
#                         option_content=sub_info.get(option_label),
#                         is_answer=is_answer,
#                     )
#                     choice_option_instance.save()
#                 '''
#
#         # 改错题
#         if question_type == 'correction':
#             result = func.parse_text_modifications(sub_text)
#             sub_list = result['sub_list']
#             text_list = result['text_list']
#             type_list = result['type_list']
#             answer_list = result['answer_list']
#             index_list = result['index_list']
#             # split_texts = result['split_texts']
#             print('sub_list: ', sub_list)
#             print('text_list: ', text_list)
#             print('type_list: ', type_list)
#             print('answer_list: ', answer_list)
#             print('index_list: ', index_list)
#             '''
#             for i in range(len(sub_list)):
#                 # 存储小题
#                 sub_instance = SubQuestion(
#                     main_question=main_instance,
#                     main_question_id=main_instance.id,
#                     question_text=sub_list[i],
#                     answer=answer_list[i],
#                 )
#                 sub_instance.save()
#                 correction_instance = Correction(
#                     sub_question=sub_instance,
#                     type=type_list[i],
#                     index=index_list[i],
#                 )
#                 correction_instance.save()
#             '''
#         # 连线题
#         if question_type == 'matching':
#             questions = func.extract_matching_questions(sub_text)
#             print('questions: ', questions)
#
#             question_info = []
#             for question in questions:
#                 question_info.append(func.process_matching_question(question))
#             print('question_info: ', question_info)
#
#             for sub_info in question_info:
#                 question_text = sub_info.get('question_text')
#                 tips = sub_info.get('tips')
#                 analysis = sub_info.get('analysis')
#                 answer = sub_info.get('option_label')
#                 option_label = sub_info.get('option_label')
#                 option_content = sub_info.get('option_content')
#             # 存储小题
#                 '''
#                 sub_instance = SubQuestion(
#                     main_question=main_instance,
#                     main_question_id=main_instance.id,
#                     question_text=question_text,
#                     tips=tips,
#                     analysis=analysis,
#                     answer=answer,
#                     score=score,
#                 )
#                 sub_instance.save()
#                 # 存储选项
#                 matching_instance = MatchingOption(
#                     sub_question=sub_instance,
#                     option_label=option_label,
#                     option_content=option_content,
#                 )
#                 matching_instance.save()
#             '''
#         # 简答题
#         if question_type == 'comprehension':
#             # 提取文本内容
#             question_list = func.extract_comprehension_questions(sub_text)
#             print('question_list: ', question_list)
#             sub_list = []
#             for question in question_list:
#                 sub_list.append(func.process_comprehension_question(question))
#                 print(f'process_question: {func.process_comprehension_question(question)}')
#             # 保存小题
#             '''
#             for sub_info in sub_list:
#                 question_text = sub_info.get('question_text')
#                 answer = sub_info.get('answer')
#                 tips = sub_info.get('tips')
#                 analysis = sub_info.get('analysis')
#                 sub_instance = SubQuestion(
#                     main_question = main_instance,
#                     main_question_id = main_instance.id,
#                     question_text = question_text,
#                     score = score,
#                     answer = answer,
#                     tips = tips,
#                     analysis = analysis,
#                 )
#                 sub_instance.save()
#             '''
#     form = WordUploadForm()
#
#     return render(request, 'teacher_side/question_integration.html', {'form': form})

# 连线题
'''
def teacher_matching(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')


    if request.method == 'POST':
        print('post data: ', request.POST)
        main_form = MainQuestionForm(request.POST)
        print("Main form data:", main_form.cleaned_data if main_form.is_valid() else main_form.errors)
        sub_formset = SubQuestionFormSet(request.POST, request.FILES)

        if main_form.is_valid() and sub_formset.is_valid():
            # 保存大题
            main_question =main_form.save(commit=False)
            main_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            main_question.question_type = question_type
            main_question.save()

            sub_formset.instance = main_question
            sub_questions = sub_formset.save(commit=False)
            # 保存小题和其选项
            for sub_question in sub_questions:
                sub_question.main_question = main_question
                sub_question.save()

                # 保存选项
                prefix = f"options-{sub_question.id}"
                print('prefix: ', prefix)
                option_formset = MatchingOptionFormset(data=request.POST, files=request.FILES, instance=sub_question,
                                                       prefix=prefix)
                if option_formset.is_valid():
                    option_formset.save()
                else:
                    # print('option_formset: ', option_formset)
                    # print(f"Option formset errors for sub_question {sub_question.id}: {option_formset.errors}")
                    print(f"Option formset errors for sub_question {sub_question.id}: {option_formset.errors}")
                    print("POST data:", request.POST.dict())
                    print("Management form data:", option_formset.management_form.data)
                    print('option_formset: ', option_formset)
                    print("Cleaned data:",
                          option_formset.cleaned_data if hasattr(option_formset, 'cleaned_data') else "No cleaned data")
            return HttpResponse('save.')
        else:
            print("Form validation failed.")
            print(main_form.errors, sub_formset.errors)
        return HttpResponse("Form validation failed.")
    else:
        main_form = MainQuestionForm()
        # sub_form = SubQuestionForm()
        # formset = MatchingOptionFormset()
        sub_formset = SubQuestionFormSet()
        # 构造每个小题的选项表单
        option_formsets = []
        for i, sub_form in enumerate(sub_formset):
            sub_question = sub_form.instance
            prefix = f"options-{i}"
            option_formsets.append({
                'prefix': prefix,
                'formset': MatchingOptionFormset(instance=sub_question, prefix=prefix)
            })
        print('option_formsets: ', option_formsets)

    return render(request, 'teacher_side/matching.html', {
        'main_form': main_form,
        # 'sub_form': sub_form,
        # 'formset': formset,
        'sub_formset': sub_formset,
        'option_formsets': option_formsets,
        # 'option_formset_template': MatchingOptionFormset(instance=SubQuestion()).empty_form,
    })
'''

# correction.html
'''
def teacher_correction(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')
    if request.method == 'POST':
        # 处理提交的数据
        main_form = MainQuestionForm(request.POST)
        sub_formset = SubQuestionFormSet(request.POST, request.FILES)

        if main_form.is_valid() and sub_formset.is_valid():
            # 保存大题表单数据
            main_question = main_form.save(commit=False)
            main_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            main_question.question_type = question_type
            main_question.save()
            # 将大题对象关联到小题表单集
            sub_questions = sub_formset.save(commit=False)
            for sub_question in sub_questions:
                sub_question.main_question = main_question
                sub_question.save()
                # 处理改错题表单集
                correction_formset = CorrectionFormSet(
                    request.POST,
                    instance=sub_question,
                )
                if correction_formset.is_valid():
                    corrections = correction_formset.save(commit=False)
                    for correction in corrections:
                        correction.sub_question = sub_question
                        correction.save()
                else:
                    messages.error(request, "改错题表单填写有误，请检查后重试。")
                    return render(request, 'correction.html', {
                        'main_form': main_form,
                        'sub_formset': sub_formset,
                        'correction_formset': correction_formset,
                    })
            messages.success(request, "题目已成功保存！")
            return HttpResponse('save.')
        else:
            messages.error(request, "表单填写有误，请检查后重试。")
    else:
        # 初始化空表单
        main_form = MainQuestionForm()
        sub_formset = SubQuestionFormSet()
        correction_formset = CorrectionFormSet()


    return render(request, 'teacher_side/correction.html', {
        'main_form': main_form,
        'sub_formset': sub_formset,
        'correction_formset': correction_formset,
    })
'''

# correction_test.html
'''
def teacher_correction(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')
    correction_formsets = []
    if request.method == 'POST':
        # 处理提交的数据
        main_form = MainQuestionForm(request.POST)
        sub_formset = SubQuestionFormSet(request.POST, request.FILES)

        if main_form.is_valid() and sub_formset.is_valid():
            # 保存大题表单数据
            main_question = main_form.save(commit=False)
            main_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            main_question.question_type = question_type
            main_question.save()
            # 将大题对象关联到小题表单集
            sub_questions = sub_formset.save(commit=False)
            for index, sub_question in enumerate(sub_questions):
                sub_question.main_question = main_question
                sub_question.save()
                # 初始化并验证每个小题的改错题表单集
                correction_prefix = f'correction-{index}'  # 动态生成前缀
                correction_formset = CorrectionFormSet(
                    request.POST,
                    instance=sub_question,
                    prefix=correction_prefix,  # 使用唯一的 prefix
                )
                if correction_formset.is_valid():
                    corrections = correction_formset.save(commit=False)
                    for correction in corrections:
                        correction.sub_question = sub_question
                        correction.save()
                else:
                    # 如果某个改错题表单无效，需回显错误信息
                    messages.error(request, f"改错题表单验证失败，请检查表单：{correction_prefix}")
                    correction_formsets.append(correction_formset)
                    break
                correction_formsets.append(correction_formset)
            if all([cf.is_valid() for cf in correction_formsets]):
                messages.success(request, "题目已成功保存！")
                return HttpResponse('save.')
        else:
            messages.error(request, "表单填写有误，请检查后重试。")
    else:
        # 初始化空表单
        main_form = MainQuestionForm()
        sub_formset = SubQuestionFormSet()

        # 创建一个临时的主问题
        media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
        print(media_material_instance)
        main_question_instance = MainQuestion(
            question_text='temporary main question instance',
            media_material=media_material_instance  # 设置有效的外键实例
        )
        print('main_question_instance: ', main_question_instance)

        # 初始化每个小题表单的改错题表单集
        for index, sub_form in enumerate(sub_formset):
            # 创建一个临时的 SubQuestion 实例
            sub_question_instance = sub_form.instance if sub_form.instance.pk else SubQuestion(
                main_question=main_question_instance,
                question_text='temporary instance.',
                answer='temporary instance.'
            )
            # temporary_sub_question = SubQuestion(main_question=instance)
            print('instance: ', sub_question_instance)
            correction_formsets.append(
                CorrectionFormSet(
                    # instance=sub_form.instance,
                    instance=sub_question_instance,
                    prefix=f'correction-{index}',
                    initial=[
                        {'type': 'insert', 'index': 0},  # 示例初始数据
                    ]
                )
            )
            print('count: ', correction_formsets[-1].total_form_count())
            print('correction_formsets: ', correction_formsets)
            print('correction_formsets[0]: ', correction_formsets[0])
    # 修改视图中的上下文传递逻辑
    form_pairs = zip(sub_formset, correction_formsets)

    return render(request, 'teacher_side/correction_test2.html', {
        'main_form': main_form,
        'sub_formset': sub_formset,
        'correction_formsets': correction_formsets,
        'form_pairs': form_pairs,  # 传递组合后的表单对
    })
'''

# correction_test2.html
'''
def teacher_correction(request):
    task_package_id = request.GET.get('task_package_id')
    question_type = request.GET.get('question_type')
    correction_formsets = []

    if request.method == 'POST':
        print('data: ', request.POST)
        # 处理提交的数据
        main_form = MainQuestionForm(request.POST)
        sub_formset = SubQuestionFormSet(request.POST, request.FILES)

        if main_form.is_valid() and sub_formset.is_valid():
            # 保存大题表单数据
            main_question = main_form.save(commit=False)
            main_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            main_question.question_type = question_type
            main_question.save()

            # 保存小题表单数据
            sub_questions = sub_formset.save(commit=False)
            for index, sub_question in enumerate(sub_questions):
                # 小题关联大题后保存
                sub_question.main_question = main_question
                sub_question.save()
                # 初始化并验证每个小题的改错题表单集
                correction_prefix = f'correction-{index}'  # 动态生成前缀
                correction_formset = CorrectionFormSet(
                    request.POST,
                    instance=sub_question,
                    prefix=correction_prefix,  # 使用唯一的 prefix
                )
                if correction_formset.is_valid():
                    corrections = correction_formset.save(commit=False)
                    for correction in corrections:
                        correction.sub_question = sub_question
                        correction.save()
                    # correction_formset.save()
                else:
                    # 返回无效改错题表单的错误信息
                    messages.error(request, f"改错题表单验证失败，请检查表单：{correction_prefix}")
                    correction_formsets.append(correction_formset)
                    # break
                correction_formsets.append(correction_formset)
            if all([cf.is_valid() for cf in correction_formsets]):
                messages.success(request, "题目已成功保存！")
                return HttpResponse('save.')
        else:
            messages.error(request, "表单填写有误，请检查后重试。")
    else:
        # 初始化空表单
        main_form = MainQuestionForm()
        sub_formset = SubQuestionFormSet()

        # 创建临时大题实例
        media_material_instance = MediaMaterial.objects.get(pk=task_package_id)
        # print(media_material_instance)
        main_question_instance = MainQuestion(
            question_text='temporary main question instance',
            media_material=media_material_instance  # 设置有效的外键实例
        )
        # print('main_question_instance: ', main_question_instance)

        for index, sub_form in enumerate(sub_formset):
            # 创建临时小题实例
            sub_question_instance = sub_form.instance if sub_form.instance.pk else SubQuestion(
                main_question=main_question_instance,
                question_text='temporary instance.',
                answer='temporary instance.'
            )
            # temporary_sub_question = SubQuestion(main_question=instance)
            # print('instance: ', sub_question_instance)
            correction_formsets.append(
                CorrectionFormSet(
                    # instance=sub_form.instance,
                    instance=sub_question_instance,
                    prefix=f'correction-{index}',
                    initial=[
                        {'type': 'insert', 'index': 0},  # 示例初始数据
                    ]
                )
            )
            # print('count: ', correction_formsets[-1].total_form_count())
            # print('correction_formsets: ', correction_formsets)
            # print('correction_formsets[0]: ', correction_formsets[0])
    # 组合表单对
    form_pairs = zip(sub_formset, correction_formsets)
    # 供前端模板动态加载
    empty_correction_form = CorrectionFormSet(prefix='correction-__prefix__').empty_form
    return render(request, 'teacher_side/correction_test2.html', {
        'main_form': main_form,
        'sub_formset': sub_formset,
        'correction_formsets': correction_formsets,
        'form_pairs': form_pairs,  # 传递组合后的表单对
        'empty_correction_form': empty_correction_form,  #
    })
'''







def teacher_course(request):
    return render(request, 'teacher_side/course.html')

def teacher_class(request):
    return render(request, 'teacher_side/class.html')

def teacher_exam_bank(request):
    if request.session.get('is_login', None):
        year = datetime.datetime.now().year
        month = int(datetime.datetime.now().month)
        if 1<=month<=8:
            semester = 1
        else:
            semester = 2

        username = request.session.get('username', None)
        teacher_instance = Teachers.objects.get(username=username)
        classes = Class.objects.filter(teacher=teacher_instance)
        units = Unit.objects.all()

        # 处理筛选查询
        class_id = request.GET.get('class_id', '')
        if class_id:
            class_instance = Class.objects.get(id=int(class_id))
            units = Unit.objects.filter(class_instance=class_instance)


        paginator = Paginator(units, 15)  # 每页展示 15 条
        page_number = request.GET.get('page')  # 获取当前页码
        page_obj = paginator.get_page(page_number)  # 获取当前页对象
        return render(request, 'teacher_side/exam_bank.html',
                      {
                          'username': username,
                          'classes': classes,
                          'units': units,
                          'page_obj': page_obj,
                      })
    return render(request, 'teacher_side/exam_bank.html')

def teacher_exam_detail(request, unit_id):
    # 根据 unit_id 获取对应的 Unit 实例，并预取关联的 PaperPage、PageMainQuestion 和 PageSubQuestion 信息
    unit = Unit.objects.prefetch_related(
        'paper_pages__page_main_questions__page_sub_questions'
    ).get(id=unit_id)
    try:
        # 获取该 Unit 实例关联的所有 TimeManagement 实例
        time_management = unit.time_management.get(unit=unit)
    except TimeManagement.DoesNotExist:
        time_management = None
    return render(request, 'teacher_side/exam_detail.html', {
        'unit': unit,
        'time_management': time_management,
    })

def teacher_exam_delete(request, unit_id):
    Unit.objects.get(id=unit_id).delete()
    return redirect(teacher_exam_bank)

def teacher_exam_management(request):
    # if request.method == 'POST':
        # main_text = request.POST['MainQuestion']
        # sub_text = request.POST['SubQuestion']
        # main_data = func.extract_main_question(main_text)
        # print('main_data: ', main_data)
        # if request.POST['question_type'] == 'blank':
        #     questions = func.extract_blank_questions(sub_text)
        #     print('questions: ', questions)
        #     for question in questions:
        #         question_datas = func.extract_subtext_and_answers(question)
        #         print('question_datas: ', question_datas)
        # word文档导入
    form = WordUploadForm()
    if request.method == 'POST' and request.FILES.get('word_file'):
        def extract_text_from_word(doc_file):
            # 读取Word文档内容
            doc = Document(doc_file)
            text = ''
            for para in doc.paragraphs:
                text += para.text
            return text

        form = WordUploadForm(request.POST, request.FILES)
        if form.is_valid():
            word_file = request.FILES['word_file']
            # 提取文本内容
            text_content = extract_text_from_word(word_file)
            doc_page_func.main_process(text_content)

    return render(request, 'teacher_side/exam_management.html', {'form': form})

def teacher_forum(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        request.session['username'] = username
        request.session['role'] = role
        request.session['is_login'] = True
    return redirect('forum:forum')
def teacher_announce(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        request.session['username'] = username
        request.session['role'] = role
        request.session['is_login'] = True
    return redirect('announce:announcements')



'''
# 大题+小题页
def create_big_question_with_small_questions_old(request):
    task_package_id = request.GET.get('task_package_id')
    print('task_package_id', task_package_id)
    if request.method == 'POST':
        big_question_form = MainQuestionForm(request.POST)
        small_question_formset = SubQuestionFormSet(request.POST, request.FILES)

        choice_option_formsets = []
        matching_option_formsets = []

        if big_question_form.is_valid() and small_question_formset.is_valid():
            # 保存大题
            big_question = big_question_form.save(commit=False)
            big_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            big_question.save()


            for small_question_form in small_question_formset:
                small_question = small_question_form.save(commit=False)
                small_question.main_question = big_question
                small_question.save()

                # if big_question.question_type == 'choice':
                #     choice_option_formset = ChoiceOptionFormSet(
                #         request.POST,
                #         prefix=f"options-{small_question_form.prefix}",
                #         instance=small_question
                #     )
                # 根据大题类型初始化选项表单集合
                if big_question.question_type == "choice":
                    choice_option_formset = ChoiceOptionFormSet(instance=small_question)
                    choice_option_formsets.append(choice_option_formset)
                elif big_question.question_type == "matching":
                    matching_option_formset = MatchingOptionFormset(instance=small_question)
                    matching_option_formsets.append(matching_option_formset)
                if choice_option_formset.is_valid():
                        choice_option_formset.save()
            return HttpResponse('submit all.')
    else:
        big_question_form = MainQuestionForm()
        small_question_formset = SubQuestionFormSet()
        choice_option_formsets = [ChoiceOptionFormSet()]
        matching_option_formsets = [MatchingOptionFormset()]

        # 动态初始化选项表单集
        # for small_question_form in small_question_formset:
        #     small_question_form.options_formset = ChoiceOptionFormSet(
        #         prefix=f"options-{small_question_form.prefix}",
        #         instance=small_question_form.instance
        #     )

    return render(request, 'create_big_question_with_small_questions.html', {
        # 'big_question_form': big_question_form,
        # 'small_question_formset': small_question_formset,
        "big_question_form": big_question_form,
        "small_question_formset": small_question_formset,
        "choice_option_formsets": choice_option_formsets,
        "matching_option_formsets": matching_option_formsets,
    })
'''

'''
#新的，暂时算能用吧
def create_big_question_with_small_questions(request):
    task_package_id = request.GET.get('task_package_id')
    print('task_package_id', task_package_id)
    if request.method == 'POST':
        big_question_form = MainQuestionForm(request.POST)
        small_question_formset = SubQuestionFormSet(request.POST, request.FILES)

        if big_question_form.is_valid() and small_question_formset.is_valid():
            # 保存大题
            big_question = big_question_form.save(commit=False)
            big_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            big_question.save()

            for small_question_form in small_question_formset:
                small_question = small_question_form.save(commit=False)
                small_question.main_question = big_question
                small_question.save()

            return HttpResponse('submit all.')
    else:
        big_question_form = MainQuestionForm()
        small_question_formset = SubQuestionFormSet()

    # 传递 empty_form 到模板
    empty_form = small_question_formset.empty_form

    return render(request, 'create_big_question_with_small_questions.html', {
        'big_question_form': big_question_form,
        'small_question_formset': small_question_formset,
        'empty_small_question_form': empty_form,
    })
'''


'''
def create_big_question_with_small_questions(request):
    task_package_id = request.GET.get('task_package_id')
    print('task_package_id', task_package_id)

    if request.method == "POST":
        big_question_form = BigQuestionForm(request.POST)
        small_question_formset = SmallQuestionFormSet(request.POST)

        # 根据大题类型动态绑定选项表单
        choice_option_formsets = []
        matching_option_formsets = []
        correction_formsets = []

        if big_question_form.is_valid() and small_question_formset.is_valid():
            # 保存大题
            big_question = big_question_form.save(commit=False)
            big_question.media_material = MediaMaterial.objects.get(id=task_package_id)
            big_question.save()

            for small_form in small_question_formset:
                small_question = small_form.save(commit=False)
                small_question.big_question = big_question
                small_question.save()

                if big_question.question_type == 'choice':
                    choice_option_formset = ChoiceOptionFormSet(request.POST, instance=small_question)
                    if choice_option_formset.is_valid():
                        choice_option_formset.save()
                elif big_question.question_type == 'matching':
                    matching_option_formset = MatchingOptionFormset(request.POST, instance=small_question)
                    if matching_option_formset.is_valid():
                        matching_option_formset.save()
                elif big_question.question_type == 'correction':
                    correction_formset = CorrectionFormset(request.POST, instance=small_question)
                    if correction_formset.is_valid():
                        correction_formset.save()
            return HttpResponse('submit all.')
        else:
            big_question_form = BigQuestionForm()
            small_question_formset = SmallQuestionFormSet()
    else:
        # GET 请求初始化表单
        big_question_form = BigQuestionForm()
        small_question_formset = SmallQuestionFormSet()

    return render(request, "teacher_side/create_question.html", {
        "big_question_form": big_question_form,
        "small_question_formset": small_question_formset,
    })
'''

