#导入要用的模块
import os
import uuid
import datetime
from msilib.schema import Media

from django.template.context_processors import request
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
from django.contrib import messages




from .models import MediaMaterial, MainQuestion, SubQuestion
from .forms import (
    MainQuestionForm,
    SubQuestionForm,
    CorrectionForm,
    SubQuestionFormSet,
    ChoiceOptionFormSet,
    MatchingOptionFormset,
    CorrectionFormSet
)


# 大题+小题页
def create_big_question_with_small_questions(request):
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
            # url = reverse('create_big_question_with_small_questions')
            url = reverse('teacher_question_type')
            return HttpResponseRedirect(f"{url}?{query_string}")
            # return redirect('teacher_question_add')

    # 表单无数据，为初次跳转网页
    print('first fetch at task_package_add.html')
    form = UploadMediaForm()
    return render(request, 'teacher_side/task_package_add.html',
            {
                    'form': form,
                })


def teacher_question_type(request):
    task_package_id = request.GET.get('task_package_id')
    if request.method == 'POST':
        question_type = request.POST.get('question_type')
        params = {
            'task_package_id': task_package_id,
            'question_type': question_type,
        }
        query_string = urlencode(params)
        if question_type == 'matching':
            url = reverse('teacher_matching')
            return HttpResponseRedirect(f"{url}?{query_string}")
        if question_type == 'correction':
            url = reverse('teacher_correction')
            return HttpResponseRedirect(f"{url}?{query_string}")
        # return HttpResponse(question_type)
        print('document')
    return render(request, 'teacher_side/question_type.html')


# 连线题
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