import json
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime

from .models import StudentMediaPlayRecord,StudentPageRecord,StudentExamRecord,StudentAnswer
from ELW.models import (Students,
                        TimeManagement,
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
from django.utils import timezone

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
            return redirect('login:login_view')





from datetime import datetime


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
            start_time = time_management.start_time
            end_time = time_management.end_time

            # 将开始时间和结束时间转换为时间戳
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            current_timestamp = int(current_datetime.timestamp())

            # 计算初始倒计时时间（仅用于页面加载时显示）
            time_remaining = start_time - current_datetime
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
    # 检查时间范围
    if now < time_management.start_time:
        return JsonResponse({'status': 'not_start', 'message': 'It is not exam time now, please wait.'}, status=403)
    elif now > time_management.end_time:
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
        record.ended_at = min(now + timezone.timedelta(minutes=time_management.duration), time_management.end_time)
        record.save()

    if not created and record.submitted:
        return JsonResponse({'status': 'submitted', 'message': 'You have already submitted this exam.'}, status=403)


    first_page = exam.paper_pages.first()

    if not first_page:
        return JsonResponse({'status': 'error', 'message': 'No pages found for this exam.'}, status=404)

    return redirect('accessment:exam_page', exam_id=exam.id, order=first_page.order)



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
        student_page_record.remaining_time = page.duration_minutes * 60
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
    answers = StudentAnswer.objects.filter(student_page_record=student_page_record)
    #answers_dict = {answer.sub_question_id: answer.text for answer in answers}
    answers_dict = {str(answer.sub_question_id): answer.text for answer in answers}

    comprehension_data = {}
    for main_question in main_questions:
        if main_question.question_type == 'comprehension': # 处理填空题
            comprehension_sub_questions = main_question.sub_questions.all().order_by('id')
            html_parts = []
            for sub_q in comprehension_sub_questions:
                blanks = sub_q.blanks.order_by('-index')
                words = sub_q.question_text.split()
                for blank in blanks:
                    if 0 <= blank.index < len(words):
                        answer = answers_dict.get(str(sub_q.id), '')
                        input_html = f'<input type="text" class="blank-input" name="answer_{sub_q.id}" id="answer_{sub_q.id}" value="{answer}"   placeholder="{ sub_q.id }"/>'
                        words.insert(blank.index + 1, input_html)
                processed_text = ' '.join(words)
                html_parts.append(processed_text)
            # 合并为连贯段落
            processed_html = ' '.join(html_parts)
            comprehension_data[main_question.id] = processed_html

        elif main_question.question_type == 'choice': # 选择题乱序
            for sub_question in sub_questions:
                options = list(sub_question.options.all())
                random.shuffle(options)
                sub_question.shuffled_options = options

        elif main_question.question_type == 'correction':# 改错题拆词
            for sub_question in sub_questions:
                sub_question.words = sub_question.question_text.split()



# if sub_question.main_question.question_type == 'correction': # 改错题显示
        #     corrections = sub_question.corrections.all()
        #     error_indices = sorted([corr.index for corr in corrections])
        #
        #     # 将题干拆分为单词
        #     words = sub_question.question_text.split()
        #
        #     # 动态分行
        #     lines = []
        #     current_line = []
        #     current_line_text = ""
        #     error_in_current_line = False
        #     error_index_in_current_line = -1
        #
        #     for index, word in enumerate(words):
        #         current_line.append(word)
        #         current_line_text += word + " "
        #
        #         # 检查当前单词是否是错误
        #         if index in error_indices:
        #             if error_in_current_line:
        #                 # 如果当前行已经有错误，需要将当前单词放到下一行
        #                 lines.append({
        #                     'text': ' '.join(current_line[:-1]),
        #                     'has_error': error_in_current_line,
        #                     'error_index': error_index_in_current_line
        #                 })
        #                 current_line = [word]
        #                 current_line_text = word + " "
        #                 error_in_current_line = True
        #                 error_index_in_current_line = index
        #             else:
        #                 error_in_current_line = True
        #                 error_index_in_current_line = index
        #
        #         # 如果当前行的单词数超过一定长度，需要换行
        #         if len(current_line) >= 10:  # 每行最多10个单词
        #             lines.append({
        #                 'text': current_line_text.strip(),
        #                 'has_error': error_in_current_line,
        #                 'error_index': error_index_in_current_line
        #             })
        #             current_line = []
        #             current_line_text = ""
        #             error_in_current_line = False
        #             error_index_in_current_line = -1
        #
        #     if current_line:
        #         lines.append({
        #             'text': ' '.join(current_line).strip(),
        #             'has_error': error_in_current_line,
        #             'error_index': error_index_in_current_line
        #         })
        #
        #     sub_question.lines = lines




    # 答案


    # 获取缓存中的答案
    cache_key = f"answers_{student_page_record.id}"
    cached_answers = cache.get(cache_key, {})

    # 将缓存中的答案更新到 answers_dict 中
    for sub_question_id, answer_text in cached_answers.items():
        # 如果缓存中的答案存在且不为空，则覆盖数据库中的答案
        if answer_text:
            answers_dict[int(sub_question_id)] = answer_text

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
        'answers': answers_dict,
        'is_last_page': is_last_page,
        'exam_record_id': student_exam_record.id,
        'started_at': student_exam_record.started_at,
        'ended_at': student_exam_record.ended_at,
        'MEDIA_URL': settings.MEDIA_URL,
        'play_records': play_records_dict,
        'remaining_time': student_page_record.remaining_time,
        'comprehension_data': comprehension_data,

    }

    return render(request, 'exam/exam_page.html', context)


@csrf_exempt
def update_remaining_time(request, page_record_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        remaining_time = data.get('remaining_time')

        student_page_record = get_object_or_404(StudentPageRecord, id=page_record_id)
        student_page_record.remaining_time = remaining_time
        if student_page_record.remaining_time <= 0:
            student_page_record.is_expired = True
        student_page_record.save()


        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



def next_page(request, exam_id, order):
    exam = get_object_or_404(Unit, id=exam_id, type='exam')
    current_page = get_object_or_404(PaperPage, unit=exam, order=order)
    next_page = exam.paper_pages.filter(order=current_page.order + 1).first()
    # 检查是否为最后一页
    if not next_page:
        # 提示已完成考试，留在当前页面
        messages.success(request, 'You have completed the exam.')
        return redirect('accessment:exam_page', exam_id=exam.id, order=current_page.order)
    else:
        # 跳转到下一页
        return redirect('accessment:exam_page', exam_id=exam.id, order=next_page.order)

def _save_answers_logic(request, page_record_id):
    # 获取页面记录
    page_record = get_object_or_404(StudentPageRecord, id=page_record_id)

    # 获取当前页面的所有大题
    page_main_questions = PageMainQuestion.objects.filter(page=page_record.page)
    main_questions = [pmq.main_question for pmq in page_main_questions]

    # 获取所有相关的小题
    page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
    sub_question_ids = [psq.sub_question.id for psq in page_sub_questions]

    # 保存答案
    for sub_question_id in sub_question_ids:
        sub_question = SubQuestion.objects.get(id=sub_question_id)
        main_question = sub_question.main_question
        question_type = main_question.question_type

        if question_type == 'choice':
            # 选择题
            selected_option = request.POST.get(f'answer_{sub_question_id}')
            answer_text = selected_option
        elif question_type == 'matching':
            # 连线题
            answers = request.POST.getlist(f'answer_{sub_question_id}')
            answer_text = ','.join(answers)
        elif question_type == 'correction':
            correction_type = request.POST.get(f'correction_type_{sub_question_id}', '').strip()
            correction_index = request.POST.get(f'correction_index_{sub_question_id}', '').strip()
            correction_text = request.POST.get(f'correction_text_{sub_question_id}', '').strip()

            # 检查是否有错误
            if correction_type == 'none':  # 没有错误
                answer_text = 'right'
            else:
                # 格式化答案文本
                answer_text = f"{correction_type}:{correction_index}:{correction_text}"
        else:
            # 主观题

            answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()

        # 更新或创建答案记录
        StudentAnswer.objects.update_or_create(
            sub_question_id=sub_question_id,
            student_page_record=page_record,
            defaults={'text': answer_text}
        )

    return JsonResponse({'message': '答案保存成功'})


def save_answers(request):
    if request.method == 'POST':
        page_record_id = request.POST.get('page_record_id')
        if not page_record_id:
            return JsonResponse({'message': '缺少页面记录 ID'}, status=400)

        try:
            page_record_id = int(page_record_id)
        except ValueError:
            return JsonResponse({'message': '页面记录 ID 必须是有效的数字'}, status=400)

        return _save_answers_logic(request, page_record_id)
    else:
        return JsonResponse({'message': '请求方法错误'}, status=400)




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

        if question_type == 'choice':
            # 选择题
            selected_option = request.POST.get(f'answer_{sub_question_id}')
            answer_text = selected_option
        elif question_type == 'matching':
            # 连线题
            answers = request.POST.getlist(f'answer_{sub_question_id}')
            answer_text = ','.join(answers)
        elif question_type == 'correction':
            # 改错题
            correction_type = request.POST.get(f'correction_type_{sub_question_id}', '').strip()
            correction_index = request.POST.get(f'correction_index_{sub_question_id}', '').strip()
            correction_text = request.POST.get(f'correction_text_{sub_question_id}', '').strip()

            # 检查是否有错误
            if correction_type == 'none':  # 没有错误
                answer_text = 'right'
            else:
                # 格式化答案文本
                answer_text = f"{correction_type}:{correction_index}:{correction_text}"
        else:
            # 主观题
            answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()

        # 将答案存入缓存
        cached_answers[sub_question_id] = answer_text

    # 将更新后的答案存入缓存，设置缓存有效期为10分钟
    cache.set(cache_key, cached_answers, timeout=600)

    return JsonResponse({'message': '已保存'})

def _save_answers_to_database(page_record_id):
    """从缓存中读取答案并保存到数据库"""
    cache_key = f"answers_{page_record_id}"
    cached_answers = cache.get(cache_key, {})

    for sub_question_id, answer_text in cached_answers.items():
        StudentAnswer.objects.update_or_create(
            sub_question_id=sub_question_id,
            student_page_record_id=page_record_id,
            defaults={'text': answer_text}
        )
    cache.delete(cache_key)  # 删除缓存
    return JsonResponse({'message': '已保存'})



@csrf_exempt
def save_page(request, exam_id, order):
    if request.method == 'POST':
        # 获取对应的 Unit 实例（类型为 'exam'）
        exam = get_object_or_404(Unit, id=exam_id, type='exam')  # 使用 exam 作为变量名

        # 获取当前页面
        current_page = get_object_or_404(PaperPage, unit=exam, order=order)  # 使用 unit 和 order

        # 获取当前登录学生的用户名
        username = request.session.get('username')
        student = get_object_or_404(Students, username=username)

        # 获取学生的考试记录
        student_exam_record = get_object_or_404(StudentExamRecord, user=student, exam=exam)  # 使用 exam

        # 获取或创建学生的页面记录
        page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=current_page)

        # 获取当前页面的所有大题
        page_main_questions = PageMainQuestion.objects.filter(page=current_page)
        main_questions = [pmq.main_question for pmq in page_main_questions]

        # 获取所有相关的小题
        page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
        sub_questions = [psq.sub_question for psq in page_sub_questions]

        # 获取已提交的小题 ID
        submitted_sub_question_ids = StudentAnswer.objects.filter(
            student_page_record=page_record
        ).exclude(
            text__isnull=True
        ).exclude(
            text=''
        ).values_list('sub_question_id', flat=True)

        # 获取未提交的小题
        unsubmitted_sub_questions = SubQuestion.objects.filter(id__in=[sq.id for sq in sub_questions]).exclude(id__in=submitted_sub_question_ids)

        # 获取 POST 数据中的标志
        manual_save = request.POST.get('manual_save', 'false').lower() == 'true'
        is_manual_submit = request.POST.get('is_manual_submit', 'false').lower() == 'true'
        force_submit = request.POST.get('force_submit', 'false').lower() == 'true'
        saved = request.POST.get('saved', 'false').lower() == 'true'

        # 保存答案到缓存和数据库
        if manual_save:
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
        elif is_manual_submit:
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            if not current_page.can_modify:  # 不可修改的页面
                if unsubmitted_sub_questions.exists():
                    return JsonResponse({'message': '有未完成的题目，是否仍然提交？', 'status': 'unfinished'}, status=200)
                else:
                    return JsonResponse({'message': '是否确认提交？', 'status': 'finished'}, status=200)
            elif current_page.can_modify:  # 可修改的页面
                if unsubmitted_sub_questions.exists():
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
            return next_page(request, exam.id, order)  # 使用 exam.id
        if force_submit:
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            page_record.submitted = True
            page_record.submitted_at = timezone.now()
            page_record.save()
            return next_page(request, exam.id, order)  # 使用 exam.id

        # 如果是手动保存，返回缓存结果
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
        unit = student_exam_record.exam  # 获取关联的 Unit 实例
        pages = unit.paper_pages.all()  # 获取所有页面

        if force_submit:
            for page in pages:
                page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)
                page_record.submitted = True
                page_record.submitted_at = timezone.now()
                page_record.save()
            student_exam_record.submitted = True
            student_exam_record.finished_at = timezone.now()
            student_exam_record.save()
            return exam_result(request)  # 确保 exam_result 视图也适配了新的模型结构

        unsubmitted_pages = []
        for page in pages:
            page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)
            if not page_record.submitted:
                unsubmitted_pages.append(page.order)

        if unsubmitted_pages and not still_submit and not finish_submit and not force_submit:
            # 有未提交的页面，返回提示信息
            return JsonResponse({'message': '有未完成的页面，是否仍然交卷？', 'status': 'exam_unfinished', 'unsubmitted_pages': unsubmitted_pages}, status=200)

        elif not unsubmitted_pages and not force_submit:
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
