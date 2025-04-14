import json
import random
import threading

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime

from AI_module.Get_from_AI import Get_from_AI
from .models import StudentMediaPlayRecord,StudentPageRecord,StudentExamRecord,StudentAnswer
from Account.models import Students
from ELW.models import (TimeManagement,
                        Unit,
                        PaperPage,
                        MediaMaterial,
                        SubQuestion,
                        MainQuestion,
                        PageMainQuestion,
                        PageSubQuestion, Correction, )

from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.db import models
from django.db.models import Sum
from django.utils.cache import patch_response_headers


def confirm_info(request):
    if request.method == 'POST':
        # 获取学生信息
        username = request.session.get('username')
        try:
            student = Students.objects.get(username=username)
            request.session['info_confirmed'] = True
            # 确认信息无误后跳转到考试列表页面
            return redirect('accessment:exam_list')
        except Students.DoesNotExist:
            messages.error(request, 'Student information not found.')
            return redirect('login:login_view')
    else:
        # GET 请求，显示个人信息确认页面
        username = request.session.get('username')
        try:
            student = Students.objects.get(username=username)
            class_instance = student.class_instance
            course = class_instance.course
            teacher = class_instance.teacher
            context = {
                'student': student,
                'class_instance': class_instance,
                'course': course,
                'teacher': teacher
            }
            return render(request, 'exam/info_confirm.html', context)
        except Students.DoesNotExist:
            messages.error(request, 'Student information not found.')
            return redirect('login')

def exam_list(request):
    if not request.session.get('is_login', False):
        return redirect('login')

    if not request.session.get('info_confirmed'):
        return redirect('accessment:confirm_info')

    current_username = request.session.get('username')
    if not current_username:
        return redirect('login')

    try:
        student = Students.objects.get(username=current_username)
    except Students.DoesNotExist:
        return HttpResponse("学生信息不存在，请联系管理员。", status=404)

    class_instance = student.class_instance
    exam_units = Unit.objects.filter(type='exam', class_instance=class_instance)

    exams = []
    current_datetime = datetime.now()
    for unit in exam_units:
        time_management = unit.time_management.first()
        if time_management:
            exam_date = time_management.exam_date
            start_time = time_management.start_time
            end_time = time_management.end_time

            # 将开始时间和结束时间转换为时间戳
            start_datetime = datetime.combine(exam_date, start_time)
            end_datetime = datetime.combine(exam_date, end_time)
            start_timestamp = int(start_datetime.timestamp())
            end_timestamp = int(end_datetime.timestamp())
            current_timestamp = int(current_datetime.timestamp())

            # 计算初始倒计时时间（仅用于页面加载时显示）
            time_remaining = start_datetime - current_datetime
            if time_remaining.total_seconds() < 0:
                time_remaining_display = "考试已开始"
            else:
                hours, remainder = divmod(time_remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_remaining_display = f"{hours}小时{minutes}分钟{seconds}秒"

            exam_data = {
                'unit_id': unit.id,
                'title': unit.title,
                'start_time': start_time,
                'end_time': end_time,
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'current_timestamp': current_timestamp,
                'time_remaining': time_remaining_display,
            }
            exams.append(exam_data)

    return render(request, 'exam/exam_list.html', {'exams': exams})

def start_exam(request, exam_id):

    exam = get_object_or_404(Unit, id=exam_id, type='exam')
    time_management = get_object_or_404(TimeManagement, unit=exam)

    now = timezone.now()

    exam_date = time_management.exam_date
    start_time = time_management.start_time
    end_time = time_management.end_time

    start_datetime = datetime.combine(exam_date, start_time)
    end_datetime = datetime.combine(exam_date, end_time)

    # 检查时间范围
    if now < start_datetime:
        return JsonResponse({'status': 'not_start', 'message': 'It is not exam time now, please wait.'}, status=403)
    elif now > end_datetime:
        return JsonResponse({'status': 'expired', 'message': 'The exam has already ended.'}, status=403)

    # 获取当前登录学生的用户名
    username = request.session.get('username')
    if not username:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in.'}, status=403)

    student = get_object_or_404(Students, username=username)

    # 创建或获取学生的考试记录
    record, created = StudentExamRecord.objects.get_or_create(user=student, exam=exam)

    if created:
        # 设置考试记录的开始时间和结束时间
        record.started_at = now
        record.ended_at = min(now + timezone.timedelta(minutes=time_management.duration), end_datetime)
        record.save()

    if not created and record.submitted:
        return JsonResponse({'status': 'submitted', 'message': 'You have already submitted this exam.'}, status=403)


    first_page = exam.paper_pages.first()

    if not first_page:
        return JsonResponse({'status': 'error', 'message': 'No pages found for this exam.'}, status=404)

    return redirect('accessment:exam_page', exam_id=exam.id, order=first_page.order)


#加载答案
def load_answers(student_page_record):
    cache_key = f"answers_{student_page_record.id}"
    cached_answers = cache.get(cache_key)

    if cached_answers is not None:
        # 如果缓存存在，直接使用缓存中的答案
        answers_dict = {}
        for sub_question_id, answer_text in cached_answers.items():
            if answer_text:
                if isinstance(answer_text, str) and answer_text.startswith('['):
                    answers_dict[int(sub_question_id)] = json.loads(answer_text)
                else:
                    answers_dict[int(sub_question_id)] = answer_text
        return answers_dict

    else:
        # 如果没有缓存，从数据库中加载答案
        answers = StudentAnswer.objects.filter(student_page_record=student_page_record)
        answers_dict = {}
        for answer in answers:
            sub_question_id = int(answer.sub_question_id)
            if answer.sub_question.main_question.question_type == 'correction':
                if sub_question_id not in answers_dict:
                    answers_dict[sub_question_id] = []
                answers_dict[sub_question_id].append({
                    'text': answer.text,
                    'index': answer.index,
                    'type': answer.type
                })
            else:
                answers_dict[sub_question_id] = answer.text

        # 更新缓存
        cache.set(cache_key, answers_dict, timeout=600)

        return answers_dict

def exam_page(request, exam_id, order):
    exam = get_object_or_404(Unit, id=exam_id, type='exam')
    time_management = get_object_or_404(TimeManagement, unit=exam)
    page = get_object_or_404(PaperPage, unit=exam, order=order)
    username = request.session.get('username')
    if not username:
        messages.error(request, "You are not logged in.")
        return redirect('login')

    student = get_object_or_404(Students, username=username)
    student_exam_record = get_object_or_404(StudentExamRecord, user=student, exam=exam)
    student_page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)

    if student_page_record.submitted and not page.can_modify:
        messages.error(request, "页面已提交，无法继续答题。")
        return next_page(request, exam_id, order)

    if created:
        if page.limited_time > 0:
            student_page_record.remaining_time = page.limited_time* 60
        else:
            student_page_record.remaining_time = None
        student_page_record.save()


    if student_page_record.is_expired:
        messages.error(request, "页面已超时，无法继续答题。")
        return save_page(request, exam_id, order)

    page_main_questions = PageMainQuestion.objects.filter(page=page)
    main_questions = [pmq.main_question for pmq in page_main_questions]

    page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
    sub_questions = [psq.sub_question for psq in page_sub_questions]

    media_materials = MediaMaterial.objects.filter(main_questions__in=main_questions).distinct()

    random.seed(student_page_record.student_exam_record.user.id)


    answers_dict = load_answers(student_page_record)


    blank_data = {}
    correction_data = {}
    for main_question in main_questions:
        if main_question.question_type == 'blank':  # 处理填空题
            blank_sub_questions = main_question.sub_questions.all().order_by('id')
            html_parts = []
            for sub_q in blank_sub_questions:
                blanks = sub_q.blanks.order_by('-index')
                words = sub_q.question_text.split()
                for blank in blanks:
                    if 0 <= blank.index < len(words):
                        answer = answers_dict.get(str(sub_q.id), '')
                        input_html = f'<input type="text" class="blank-input" name="answer_{sub_q.id}" id="answer_{sub_q.id}" value="{answer}" placeholder="{sub_q.id}"/>'
                        # tip_html = f'<span class="blank-tip" id="tip_{sub_q.id}" style="display: none;">{sub_q.tips}</span>' if sub_q.tips else ''
                        tip_icon_html = ''
                        if sub_q.tips:
                            tip_icon_html = f'''
                                                    <span class="tip-icon" data-tip-content="{sub_q.tips}">
                                                        ⓘ
                                                        <span class="tip-content">{sub_q.tips}</span>
                                                    </span>
                                                '''
                        words.insert(blank.index + 1, input_html + tip_icon_html)
                processed_text = ' '.join(words)
                html_parts.append(processed_text)
            # 合并为连贯段落
            processed_html = ' '.join(html_parts)
            blank_data[main_question.id] = processed_html

        elif main_question.question_type == 'choice': # 选择题乱序
            for sub_question in sub_questions:
                options = list(sub_question.options.all())
                random.shuffle(options)
                sub_question.shuffled_options = options

        elif main_question.question_type == 'correction':# 改错题拆词
            correction_sub_questions = main_question.sub_questions.all().order_by('id')
            full_text = ' '.join(sub_q.question_text for sub_q in correction_sub_questions)  # 合并为完整短文

            # 记录每个单词的 sub_question_id 和局部 index
            word_data = []
            for sub_q in correction_sub_questions:
                sub_q_words = sub_q.question_text.split()
                for local_index, word in enumerate(sub_q_words):  # 使用局部索引
                    word_data.append({
                        'word': word,
                        'sub_question_id': sub_q.id,
                        'local_index': local_index,  # 使用局部索引
                    })

            correction_data[main_question.id] = {
                'html': full_text,
                'words': word_data,  # 存储每个单词的详细信息
                'sub_questions': correction_sub_questions,  # 存储 SubQuestion 信息
            }

    play_records = StudentMediaPlayRecord.objects.filter(student_exam_record=student_exam_record,
                                                         main_question__in=main_questions)
    play_records_dict = {record.main_question_id: record.play_count for record in play_records}

    is_last_page = not PaperPage.objects.filter(unit=exam, order=page.order + 1).exists()


    context = {
        'exam': exam,
        'page': page,
        'student_exam_record': student_exam_record,
        'student_page_record': student_page_record,
        'current_page_record_id': student_page_record.id,
        'main_questions': main_questions,
        'media_materials': media_materials,
        'sub_questions': sub_questions,
        'order': page.order,
        'answers': json.dumps(answers_dict, cls=DjangoJSONEncoder),
        'is_last_page': is_last_page,
        'exam_record_id': student_exam_record.id,
        'started_at': student_exam_record.started_at,
        'ended_at': student_exam_record.ended_at,
        'MEDIA_URL': settings.MEDIA_URL,
        'play_records': play_records_dict,
        'remaining_time': student_page_record.remaining_time,
        'blank_data': blank_data,
        'correction_data':correction_data,
        'page_submitted': student_page_record.submitted,

    }
    response = render(request, 'exam/exam_page.html', context)

    # 设置响应头防止缓存
    patch_response_headers(response, cache_timeout=0)
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response
    # return render(request, 'exam/exam_page.html', context)


@csrf_exempt
def update_remaining_time(request, page_record_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        remaining_time = data.get('remaining_time')

        student_page_record = get_object_or_404(StudentPageRecord, id=page_record_id)
        student_page_record.remaining_time = remaining_time
        if student_page_record.remaining_time and student_page_record.remaining_time<= 0:
            student_page_record.is_expired = True
        else:
            student_page_record.is_expired = False

        student_page_record.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def next_page(request, exam_id, order):
    exam = get_object_or_404(Unit, id=exam_id, type='exam')
    current_page = get_object_or_404(PaperPage, unit=exam, order=order)
    next_page = exam.paper_pages.filter(order=current_page.order + 1).first()
    username = request.session.get('username')
    if not username:
        messages.error(request, "You are not logged in.")
        return redirect('login')

    student = get_object_or_404(Students, username=username)

    page_main_questions = PageMainQuestion.objects.filter(page=current_page)
    main_questions = [pmq.main_question for pmq in page_main_questions]

    # 检查是否所有问题都达到了最少播放次数
    student_exam_record = get_object_or_404(StudentExamRecord, user=student, exam=exam)
    play_records = StudentMediaPlayRecord.objects.filter(
        student_exam_record=student_exam_record,
        main_question__in=main_questions
    )

    for main_question in main_questions:
        play_record = play_records.filter(main_question=main_question).first()
        print(main_question.minimum_play)
        if main_question.minimum_play <= 0:
            if next_page:
                return redirect('accessment:exam_page', exam_id=exam.id, order=next_page.order)
            else:
                messages.success(request, 'You have completed the exam.')
                return redirect('accessment:exam_page', exam_id=exam.id, order=current_page.order)
        else:
            if play_record and play_record.play_count >= main_question.minimum_play:
                if next_page:
                    return redirect('accessment:exam_page', exam_id=exam.id, order=next_page.order)
                else:
                    messages.success(request, 'You have completed the exam.')
                    return redirect('accessment:exam_page', exam_id=exam.id, order=current_page.order)
            else:
                # 播放次数不满足要求，留在当前页面
                messages.warning(request, f'You need to play the media at least {main_question.minimum_play} times.')
                return redirect('accessment:exam_page', exam_id=exam.id, order=current_page.order)


# def _save_answers_logic(request, page_record_id):
#     # 获取页面记录
#     page_record = get_object_or_404(StudentPageRecord, id=page_record_id)
#
#     # 获取当前页面的所有大题
#     page_main_questions = PageMainQuestion.objects.filter(page=page_record.page)
#     main_questions = [pmq.main_question for pmq in page_main_questions]
#
#     # 获取所有相关的小题
#     page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
#     sub_question_ids = [psq.sub_question.id for psq in page_sub_questions]
#
#     # 保存答案
#     for sub_question_id in sub_question_ids:
#         sub_question = SubQuestion.objects.get(id=sub_question_id)
#         main_question = sub_question.main_question
#         question_type = main_question.question_type
#
#         if question_type == 'choice':
#             # 选择题
#             selected_option = request.POST.get(f'answer_{sub_question_id}')
#             answer_text = selected_option
#             # 更新或创建答案记录
#             StudentAnswer.objects.update_or_create(
#                 sub_question_id=sub_question_id,
#                 student_page_record=page_record,
#                 defaults={'text': answer_text}
#             )
#         elif question_type == 'matching':
#             # 连线题
#             answers = request.POST.getlist(f'answer_{sub_question_id}')
#             answer_text = ','.join(answers)
#             # 更新或创建答案记录
#             StudentAnswer.objects.update_or_create(
#                 sub_question_id=sub_question_id,
#                 student_page_record=page_record,
#                 defaults={'text': answer_text}
#             )
#         elif question_type == 'correction':
#             # 改错题
#             for key, value in request.POST.items():
#                 if key.startswith(f'correction_type_{sub_question_id}_'):
#                     # 提取 local_index
#                     local_index = key.split('_')[-1]
#
#                     # 获取对应的错误类型、索引和修改内容
#                     correction_type = value.strip()
#                     correction_text = request.POST.get(f'correction_text_{sub_question_id}_{local_index}', '').strip()
#                     correction_index = request.POST.get(f'correction_index_{sub_question_id}_{local_index}', '').strip()
#
#                     # 检查是否有错误
#                     if correction_type == 'none':  # 没有错误
#                         answer_text = 'right'
#                     else:
#                         # 格式化答案文本：type:index:text
#                         answer_text = f"{correction_type}:{correction_index}:{correction_text}"
#                     StudentAnswer.objects.create(
#                         sub_question=sub_question,
#                         student_page_record=page_record,
#                         text=answer_text
#                     )
#
#
#         else:
#             # 主观题
#             answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()
#             # 更新或创建答案记录
#             StudentAnswer.objects.update_or_create(
#                 sub_question_id=sub_question_id,
#                 student_page_record=page_record,
#                 defaults={'text': answer_text}
#             )
#
#         # # 更新或创建答案记录
#         # StudentAnswer.objects.update_or_create(
#         #     sub_question_id=sub_question_id,
#         #     student_page_record=page_record,
#         #     defaults={'text': answer_text}
#         # )
#
#     return JsonResponse({'message': '答案保存成功'})
# def save_answers(request):
#     if request.method == 'POST':
#         page_record_id = request.POST.get('page_record_id')
#         if not page_record_id:
#             return JsonResponse({'message': '缺少页面记录 ID'}, status=400)
#
#         try:
#             page_record_id = int(page_record_id)
#         except ValueError:
#             return JsonResponse({'message': '页面记录 ID 必须是有效的数字'}, status=400)
#
#         return _save_answers_logic(request, page_record_id)
#     else:
#         return JsonResponse({'message': '请求方法错误'}, status=400)

#暂时缓存
def _save_answers_to_cache(request, page_record_id):
    page_record = get_object_or_404(StudentPageRecord, id=page_record_id)

    page_main_questions = PageMainQuestion.objects.filter(page=page_record.page)
    main_questions = [pmq.main_question for pmq in page_main_questions]

    page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
    sub_questions = [psq.sub_question for psq in page_sub_questions]

    # 构造缓存键
    cache_key = f"answers_{page_record_id}"

    # 获取当前缓存中的答案，如果没有则初始化为空字典
    cached_answers = cache.get(cache_key, {})

    # 更新缓存中的答案
    for sub_question in sub_questions:
        sub_question_id = sub_question.id
        main_question = sub_question.main_question
        question_type = main_question.question_type
        answer_text = ""

        if question_type == 'choice':
            # 选择题
            selected_option = request.POST.get(f'answer_{sub_question_id}')
            answer_text = selected_option
        elif question_type == 'matching':
            # 连线题
            answers = request.POST.getlist(f'answer_{sub_question_id}')
            answer_text = ','.join(answers)
        elif question_type == 'correction': # 改错题
            correction_types = []
            correction_texts = []
            correction_indices = []

            for key, value in request.POST.items():
                if key.startswith(f'correction_type_{sub_question_id}_'):
                    local_index = key.split('_')[-1]
                    correction_type = value.strip()
                    correction_text = request.POST.get(f'correction_text_{sub_question_id}_{local_index}', '').strip()

                    if correction_type != 'none':
                        correction_types.append(correction_type)
                        correction_texts.append(correction_text)
                        correction_indices.append(local_index)
            answer_text = []
            for i in range(len(correction_types)):
                answer_text.append({
                    'type': correction_types[i],
                    'index': correction_indices[i],
                    'text': correction_texts[i]
                })
            answer_text = json.dumps(answer_text)  # 将列表转换为 JSON 字符串
        else:
            # 主观题
            answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()

        # 将答案存入缓存
        cached_answers[sub_question_id] = answer_text

    # 将更新后的答案存入缓存，设置缓存有效期为10分钟
    cache.set(cache_key, cached_answers, timeout=600)

    return JsonResponse({'message': '已保存'})

# def _save_answers_to_database(page_record_id):
#     """从缓存中读取答案并保存到数据库"""
#     cache_key = f"answers_{page_record_id}"
#     cached_answers = cache.get(cache_key, {})
#
#     for sub_question_id, answer_text in cached_answers.items():
#         StudentAnswer.objects.update_or_create(
#             sub_question_id=sub_question_id,
#             student_page_record_id=page_record_id,
#             defaults={'text': answer_text}
#         )
#     cache.delete(cache_key)  # 删除缓存
#     return JsonResponse({'message': '已保存'})

def _update_cache(page_record):
    """从数据库中读取最新答案并更新缓存"""
    cache_key = f"answers_{page_record.id}"
    cached_answers = {}

    student_answers = StudentAnswer.objects.filter(student_page_record=page_record)
    for answer in student_answers:
        sub_question_id = answer.sub_question.id
        if answer.sub_question.main_question.question_type == 'correction':
            # 对于改错题，将答案转换为 JSON 字符串
            corrections = []
            if answer.type and answer.index is not None and answer.text:
                corrections.append({
                    'type': answer.type,
                    'index': answer.index,
                    'text': answer.text
                })
            cached_answers[sub_question_id] = json.dumps(corrections)
        else:
            cached_answers[sub_question_id] = answer.text


    # 更新缓存
    cache.set(cache_key, cached_answers, timeout=600)

def _save_answers_to_database(page_record_id):
    """从缓存中读取答案并保存到数据库"""
    cache_key = f"answers_{page_record_id}"
    cached_answers = cache.get(cache_key, {})

    for sub_question_id, answer_text in cached_answers.items():
        sub_question_id = int(sub_question_id)
        sub_question = SubQuestion.objects.get(id=sub_question_id)

        if sub_question.main_question.question_type == 'correction':
            if answer_text == 'none':
                StudentAnswer.objects.filter(
                    sub_question=sub_question,
                    student_page_record_id=page_record_id
                ).delete()
            else:
                StudentAnswer.objects.filter(
                    sub_question=sub_question,
                    student_page_record_id=page_record_id
                ).delete()

                corrections = json.loads(answer_text)
                for correction in corrections:
                    StudentAnswer.objects.create(
                        sub_question=sub_question,
                        student_page_record_id=page_record_id,
                        text=correction['text'],
                        index=int(correction['index']),
                        type=correction['type']
                    )
        else:
            # 其他题型直接更新或创建答案记录
            StudentAnswer.objects.update_or_create(
                sub_question_id=sub_question_id,
                student_page_record_id=page_record_id,
                defaults={'text': answer_text}
            )
    # 更新缓存
    page_record = StudentPageRecord.objects.get(id=page_record_id)
    _update_cache(page_record)
    return JsonResponse({'message': '已保存'})


@csrf_exempt
def save_page(request, exam_id, order):
    if request.method == 'POST':
        exam = get_object_or_404(Unit, id=exam_id, type='exam')
        current_page = get_object_or_404(PaperPage, unit=exam, order=order)
        username = request.session.get('username')
        student = get_object_or_404(Students, username=username)
        student_exam_record = get_object_or_404(StudentExamRecord, user=student, exam=exam)
        page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=current_page)

        page_main_questions = PageMainQuestion.objects.filter(page=current_page).exclude(
            main_question__question_type='text')
        main_questions = [pmq.main_question for pmq in page_main_questions]

        page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
        sub_questions = [psq.sub_question for psq in page_sub_questions]

        submitted_sub_question_ids = StudentAnswer.objects.filter(
            student_page_record=page_record
        ).exclude(
            text__isnull=True
        ).exclude(
            text=''
        ).values_list(
            'sub_question_id', flat=True
        )

        #检查是否有题目未完成
        unsubmitted_main_questions = []

        # 特殊处理改错题
        for main_question in main_questions:
            if main_question.question_type == 'correction':
                # 改错题任意小题有答案，就视为完成
                sub_questions_for_main = [psq.sub_question for psq in page_sub_questions if
                                          psq.page_main_question.main_question == main_question]
                if not any(sq.id in submitted_sub_question_ids for sq in sub_questions_for_main):
                    unsubmitted_main_questions.append(main_question)
            else:
                sub_questions_for_main = [psq.sub_question for psq in page_sub_questions if
                                          psq.page_main_question.main_question == main_question]
                unsubmitted_sub_questions_for_main = [
                    sq for sq in sub_questions_for_main if sq.id not in submitted_sub_question_ids
                ]
                if unsubmitted_sub_questions_for_main:
                    unsubmitted_main_questions.append(main_question)
        manual_save = request.POST.get('manual_save', 'false').lower() == 'true'
        is_manual_submit = request.POST.get('is_manual_submit', 'false').lower() == 'true'
        force_submit = request.POST.get('force_submit', 'false').lower() == 'true'
        saved = request.POST.get('saved', 'false').lower() == 'true'

        # 保存答案到缓存和数据库
        if not manual_save and not is_manual_submit:  # 自动保存
            _save_answers_to_cache(request, page_record.id)
        if manual_save and not is_manual_submit: #手动保存
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            if current_page.can_modify:
                if not unsubmitted_main_questions:
                    page_record.submitted = True
                    page_record.save()

        if is_manual_submit:
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            if not current_page.can_modify:  # 不可修改的页面
                if unsubmitted_main_questions:
                    return JsonResponse({'message': '有未完成的题目，是否仍然提交？', 'status': 'unfinished'}, status=200)
                else:
                    return JsonResponse({'message': '是否确认提交？', 'status': 'finished'}, status=200)
            elif current_page.can_modify:  # 可修改的页面
                if unsubmitted_main_questions:
                    page_record.submitted = False
                    page_record.save()
                    return JsonResponse({'message': '答案保存成功', 'status': 'saved'}, status=200)
                else:
                    page_record.submitted = True
                    page_record.save()
                    return JsonResponse({'message': '答案保存成功', 'status': 'saved'}, status=200)
        if saved:
            page_record.submitted_at = timezone.now()
            page_record.save()
            return next_page(request, exam.id, order)
        if force_submit:
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            page_record.submitted = True
            page_record.submitted_at = timezone.now()
            page_record.save()
            return next_page(request, exam.id, order)
        return _save_answers_to_cache(request, page_record.id)


    else:
        return JsonResponse({'message': '请求方法错误'}, status=400)



def submit_exam(request):
    if request.method == 'POST':
        student_exam_record_id = request.POST.get('student_exam_record_id')
        still_submit = request.POST.get('still_submit', 'false').lower() == 'true'
        finish_submit = request.POST.get('finish_submit', 'false').lower() == 'true'
        force_submit = request.POST.get('force_submit', 'false').lower() == 'true'

        if not student_exam_record_id:
            return JsonResponse({'message': '缺少考试记录 ID', 'status': 'error'}, status=400)
        try:
            student_exam_record_id = int(student_exam_record_id)
        except ValueError:
            return JsonResponse({'message': '考试记录 ID 必须是有效的数字', 'status': 'error'}, status=400)

        # 获取学生的考试记录
        student_exam_record = get_object_or_404(StudentExamRecord, id=student_exam_record_id)
        unit = student_exam_record.exam
        pages = unit.paper_pages.all()
        # 获取所有页面记录
        page_records = StudentPageRecord.objects.filter(student_exam_record=student_exam_record,
                                                        page__in=pages)

        if force_submit:
            for page in pages:
                page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)
                page_record.submitted = True
                page_record.submitted_at = timezone.now()
                page_record.save()
            student_exam_record.submitted = True
            student_exam_record.finished_at = timezone.now()
            student_exam_record.save()
            return exam_result(request)

        unsubmitted_pages = []
        for page in pages:
            page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)
            if not page_record.submitted:
                unsubmitted_pages.append(page.order)

        if unsubmitted_pages and not still_submit and not finish_submit and not force_submit:
            # 有未提交的页面，返回提示信息
            return JsonResponse({'message': '有未完成的页面，是否仍然交卷？', 'status': 'exam_unfinished', 'unsubmitted_pages': unsubmitted_pages}, status=200)

        elif not unsubmitted_pages and not force_submit and not finish_submit:
            return JsonResponse({'message': '是否确认交卷？', 'status': 'exam_finished'}, status=200)

        if still_submit or finish_submit:
            for page in pages:
                page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)
                page_record.submitted = True
                page_record.submitted_at = timezone.now()
                page_record.save()
            student_exam_record.submitted = True
            student_exam_record.finished_at = timezone.now()
            student_exam_record.save()

            # 批改所有已提交的页面
            for page_record in page_records:
                if (student_exam_record.submitted and page_record.submitted
                        and not page_record.is_graded):
                    try:
                        # 调用批改函数
                        grade_page(page_record)
                    except Exception as e:
                        print(f"Error grading page {page_record.page.order}: {e}")

            # 更新考试记录的总分
            try:
                total_score = StudentPageRecord.objects.filter(
                    student_exam_record=student_exam_record,
                    is_graded=True
                ).aggregate(Sum('page_score'))['page_score__sum'] or 0
                student_exam_record.score = total_score
                student_exam_record.submitted = True
                student_exam_record.finished_at = timezone.now()
                student_exam_record.save()
            except Exception as e:
                print(f"Error updating exam record score: {e}")
            return exam_result(request)

    else:
        return JsonResponse({'message': '请求方法错误', 'status': 'error'}, status=400)



@csrf_exempt
@require_POST
def update_play_count(request):
    try:
        data = json.loads(request.body)
        student_exam_record_id = data.get("student_exam_record_id")
        main_question_id = data.get("main_question_id")
        media_material_id = data.get("media_material_id")

        if not student_exam_record_id or not main_question_id or not media_material_id:
            return JsonResponse({"success": False, "message": "Invalid request data."}, status=400)

        # 获取学生考试记录
        student_exam_record = StudentExamRecord.objects.get(id=student_exam_record_id)
        main_question = MainQuestion.objects.get(id=main_question_id)
        media_material = MediaMaterial.objects.get(id=media_material_id)

        # 获取或创建播放记录
        play_record, created = StudentMediaPlayRecord.objects.get_or_create(
            student_exam_record=student_exam_record,
            main_question=main_question,
            media_material=media_material,
            defaults={"play_count": 0}
        )

        # 检查播放次数是否达到最大值
        if play_record.play_count >= main_question.maximum_play:
            return JsonResponse({"success": False, "message": "Maximum play count reached. Cannot play anymore."},
                                status=403)

        # 更新播放次数
        play_record.play_count += 1
        play_record.save()

        return JsonResponse({"success": True, "message": "Play count updated successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

def exam_result(request):
    # 获取当前登录学生的用户名
    username = request.session.get('username')
    if not username:
        return redirect('login')  # 如果没有登录，重定向到登录页面
    student = get_object_or_404(Students, username=username)

    student_exam_record = get_object_or_404(StudentExamRecord, user=student, exam__type='exam')
    exam = student_exam_record.exam
    return render(request, 'exam/exam_result.html', {
        'exam': exam,
        'student_exam_record': student_exam_record
    })


# def grade_page(page_record):
#     # 获取学生提交的答案
#     student_answers = StudentAnswer.objects.filter(student_page_record=page_record)
#
#     # 批改答案逻辑
#     total_score = 0
#     feedback = []
#
#     for student_answer in student_answers:
#         sub_question = student_answer.sub_question
#         correct_answer = sub_question.answer  # 假设题目模型中有正确答案字段
#
#         # 根据题型进行不同的批改逻辑
#         if sub_question.main_question.question_type == 'choice':
#             # 选择题批改逻辑
#             if student_answer.text == correct_answer:
#                 score = sub_question.score
#             else:
#                 score = 0
#             feedback.append(f"第{sub_question.id}题: 你的答案是 {student_answer.text}, 正确答案是 {correct_answer}")
#
#         elif sub_question.main_question.question_type == 'blank':
#             # 填空题批改逻辑
#             correct = True
#             for blank in sub_question.blanks.all():
#                 student_blank = student_answer.text.split()[blank.index]
#                 if student_blank != blank.answer:
#                     correct = False
#                     break
#             if correct:
#                 score = sub_question.score
#             else:
#                 score = 0
#             feedback.append(f"第{sub_question.id}题: 部分答案可能有误，请检查")
#
#         elif sub_question.main_question.question_type == 'correction':
#             # 改错题批改逻辑
#             correct = True
#             for correction in student_answer.corrections.all():
#                 if correction.type != 'none' and (
#                         correction.text != correction.correct_text or correction.index != correction.correct_index):
#                     correct = False
#                     break
#             if correct:
#                 score = sub_question.score
#             else:
#                 score = 0
#             feedback.append(
#                 f"第{sub_question.id}题: 你的改错有 {sub_question.corrections.count() - correct} 处错误")
#
#         # 累加总分
#         total_score += score
#         student_answer.score = score
#         student_answer.save()
#
#     # 保存批改结果
#     page_record.page_score = total_score
#     page_record.feedback = "\n".join(feedback)
#     page_record.is_graded = True
#     page_record.save()
def grade_comprehension(sub_question, student_answer):
    try:
        m = Get_from_AI(model='ZhipuAI')
        m.set_prompt_variables(my_dict={"原文": "暂无", "题目": sub_question.question_text,
                                         "参考答案": sub_question.answer,
                                         "学生回答": student_answer.text, "其他要求_评分": "请按格式｛\"分数\":, \"理由\":｝给出分数和理由，使用英文符号"})
        res = m.get_answer(m.get_prompt("题目评分"))
        dic = json.loads(res)
        student_answer.score = dic['分数']
        return dic['分数']
    except Exception as e:
        print(e)
def background_grade_comprehension(sub_question, student_answer):
    try:
        score = grade_comprehension(sub_question, student_answer)
        student_answer.score = score
        student_answer.save()

        # 重新计算并更新页面分数
        page_record = student_answer.student_page_record
        answers = StudentAnswer.objects.filter(student_page_record=page_record)

        # 只包括有效分数（>= 0）
        valid_scores = [ans.score for ans in answers if ans.score is not None and ans.score >= 0]
        if valid_scores:
            page_record.page_score = sum(valid_scores)
            page_record.save()

        # 更新练习记录总分
        student_practice_record = page_record.student_practice_record
        page_records = StudentPageRecord.objects.filter(
            student_practice_record=student_practice_record,
            is_graded=True
        )
        total_score = sum(pr.page_score for pr in page_records if pr.page_score is not None)
        student_practice_record.score = total_score
        student_practice_record.save()
    except Exception as e:
        print(f"后台评分错误: {e}")

def grade_page(page_record):
    print('grade')
    # 获取学生提交的答案
    student_answers = StudentAnswer.objects.filter(student_page_record_id=page_record.id)

    # 批改答案逻辑
    total_score = 0
    feedback = []

    for student_answer in student_answers:
        sub_question = student_answer.sub_question
        correct_answer = sub_question.answer

        # 根据题型进行不同的批改逻辑
        if sub_question.main_question.question_type == 'choice':
            # 选择题批改逻辑
            if student_answer.text == correct_answer:
                score = sub_question.score
            else:
                score = 0
            feedback.append(f"第{sub_question.id}题: 你的答案是 {student_answer.text}, 正确答案是 {correct_answer}")
        elif sub_question.main_question.question_type == 'blank':
            # 填空题批改逻辑
            correct = False
            student_blank = student_answer.text
            if student_blank == correct_answer:
                correct = True

            if correct:
                score = sub_question.score
            else:
                score = 0
        elif sub_question.main_question.question_type == 'matching':
            # 连线题批改逻辑
            correct = False
            student_matching = student_answer.text
            if student_matching == correct_answer:
                correct = True

            if correct:
                score = sub_question.score
            else:
                score = 0
        elif sub_question.main_question.question_type == 'correction':
            # 改错题批改逻辑
            correct_corrections = Correction.objects.filter(sub_question=sub_question)
            student_corrections = StudentAnswer.objects.filter(sub_question=sub_question)
            correct = True
            for correct_correction in correct_corrections:
                found = False
                for student_correction in student_corrections:

                    if (student_correction.type == correct_correction.type and
                            student_correction.index == correct_correction.index):
                        found = True
                        break
                if not found:
                    correct = False
                    break
            if correct:
                score = sub_question.score
            else:
                score = 0
        elif sub_question.main_question.question_type == 'comprehension':
            #后续批改
            score = -1
            # 启动后台线程进行AI评分
            grading_thread = threading.Thread(
                target=background_grade_comprehension,
                args=(sub_question, student_answer)
            )
            grading_thread.daemon = True  # 使线程在主程序退出时终止
            grading_thread.start()
            continue

        # 累加总分
        if(score and score >= 0):
            total_score += score
            student_answer.score = score
        else:
            student_answer.score = score

        student_answer.save()

    # 保存批改结果
    page_record.page_score = total_score
    page_record.feedback = "\n".join(feedback)
    page_record.is_graded = True
    page_record.save()