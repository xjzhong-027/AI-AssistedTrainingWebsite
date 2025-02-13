import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Exam, StudentExamRecord, Page, StudentPageRecord, StudentAnswer, MediaMaterial, SubQuestion
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest


@login_required
def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'exam/exam_list.html', {'exams': exams})

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    now = timezone.now()
    latest_entry_time = exam.start_time + timezone.timedelta(minutes=9990)

    if now < exam.start_time:
        return JsonResponse({'status': 'not_start', 'message': 'It is not exam time now, please wait.'}, status=403)
    elif latest_entry_time < now < exam.end_time:
        return JsonResponse({'status': 'late', 'message': 'You are late and cannot start the exam.'}, status=403)
    elif now > exam.end_time:
        return JsonResponse({'status': 'expired', 'message': 'The exam has already ended.'}, status=403)

    record, created = StudentExamRecord.objects.get_or_create(user=request.user, exam=exam)
    if created:
        record.started_at = now
        record.ended_at = min(now + timezone.timedelta(minutes=exam.duration_minutes), exam.end_time)
        record.save()

    if not created and record.submitted:
        return JsonResponse({'status': 'submitted', 'message': 'You have already submitted this exam.'}, status=403)

    first_page = exam.pages.first()
    return redirect('accessment:exam_page', exam_id=exam.id, page_number=first_page.page_number)

@login_required
def exam_page(request, exam_id, page_number):
    exam = get_object_or_404(Exam, id=exam_id)
    page = get_object_or_404(Page, exam=exam, page_number=page_number)
    student_exam_record = get_object_or_404(StudentExamRecord, user=request.user, exam=exam)
    student_page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)

    main_questions = page.main_questions.all()
    media_materials = MediaMaterial.objects.filter(main_questions__in=main_questions).distinct()
    sub_questions = SubQuestion.objects.filter(main_question__in=main_questions)

    # 获取当前页面的所有答案
    answers = StudentAnswer.objects.filter(student_page_record=student_page_record)
    answers_dict = {answer.sub_question_id: answer.text for answer in answers}
    # 获取缓存中的答案
    cache_key = f"answers_{student_page_record.id}"
    cached_answers = cache.get(cache_key, {})

    # 合并数据库中的答案和缓存中的答案（优先使用缓存中的答案）
    for sub_question_id, answer_text in cached_answers.items():
        answers_dict[int(sub_question_id)] = answer_text

    # 检查是否为最后一页
    is_last_page = not exam.pages.filter(page_number=page.page_number + 1).exists()

    context = {
        'exam': exam,
        'page': page,
        'student_exam_record': student_exam_record,
        'student_page_record': student_page_record,
        'current_page_record_id': student_page_record.id,
        'main_questions': main_questions,
        'media_materials': media_materials,
        'sub_questions': sub_questions,
        'page_number': page_number,
        'answers': answers_dict,
        'is_last_page': is_last_page,
        'exam_record_id': student_exam_record.id,
        'started_at': student_exam_record.started_at,
        'ended_at': student_exam_record.ended_at,
    }

    return render(request, 'exam/exam_page.html', context)


@login_required
def next_page(request, exam_id, page_number):
    exam = get_object_or_404(Exam, id=exam_id)
    current_page = get_object_or_404(Page, exam=exam, page_number=page_number)
    next_page = exam.pages.filter(page_number=current_page.page_number + 1).first()

    # 检查是否为最后一页
    if not next_page:
        # 提示已完成考试，留在当前页面
        messages.success(request, 'You have completed the exam.')
        return redirect('accessment:exam_page', exam_id=exam.id, page_number=current_page.page_number)
    else:
        # 跳转到下一页
        return redirect('accessment:exam_page', exam_id=exam.id, page_number=next_page.page_number)

def _save_answers_logic(request, page_record_id):
    page_record = get_object_or_404(StudentPageRecord, id=page_record_id)
    main_questions = page_record.page.main_questions.all()
    sub_question_ids = SubQuestion.objects.filter(main_question__in=main_questions).values_list('id', flat=True)

    # 保存答案
    for sub_question_id in sub_question_ids:
        answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()
        # 无论答案是否为空，都更新或创建记录
        StudentAnswer.objects.update_or_create(
            sub_question_id=sub_question_id,
            student_page_record=page_record,
            defaults={'text': answer_text}
        )

    return JsonResponse({'message': '答案保存成功'})

@login_required
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
    main_questions = page_record.page.main_questions.all()
    sub_question_ids = SubQuestion.objects.filter(main_question__in=main_questions).values_list('id', flat=True)

    # 构造缓存键
    cache_key = f"answers_{page_record_id}"

    # 获取当前缓存中的答案，如果没有则初始化为空字典
    cached_answers = cache.get(cache_key, {})

    # 更新缓存中的答案
    for sub_question_id in sub_question_ids:
        answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()
        cached_answers[sub_question_id] = answer_text

    # 将更新后的答案存入缓存
    cache.set(cache_key, cached_answers, timeout=600)  # 缓存有效期10分钟
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


@login_required
@csrf_exempt
def save_page(request, exam_id, page_number):
    if request.method == 'POST':
        exam = get_object_or_404(Exam, id=exam_id)
        current_page = get_object_or_404(Page, exam=exam, page_number=page_number)
        student_exam_record = get_object_or_404(StudentExamRecord, user=request.user, exam=exam)
        page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=current_page)

        main_questions = current_page.main_questions.all()
        sub_questions = SubQuestion.objects.filter(main_question__in=main_questions)
        submitted_sub_question_ids = StudentAnswer.objects.filter(
            student_page_record=page_record
        ).exclude(
            text__isnull=True
        ).exclude(
            text=''
        ).values_list('sub_question_id', flat=True)
        unsubmitted_sub_questions = sub_questions.exclude(id__in=submitted_sub_question_ids)
        manual_save = request.POST.get('manual_save', 'false').lower() == 'true'           #手动保存or自动保存
        is_manual_submit = request.POST.get('is_manual_submit', 'false').lower() == 'true' #提交
        force_submit = request.POST.get('force_submit', 'false').lower() == 'true'         #是否为用户选择“确认提交”
        saved = request.POST.get('saved', 'false').lower() == 'true'                       #页面允许修改但有未完成题目 不设置为已经提交

        if manual_save: #手动保存 暂存
            _save_answers_to_cache(request, page_record.id)
            return _save_answers_to_database(page_record.id)
        elif is_manual_submit: #提交
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            if not current_page.can_modify: #不可以修改的页面
                if unsubmitted_sub_questions.exists():
                    # 页面不允许二次修改且有未完成的题目
                    return JsonResponse({'message': '有未完成的题目，是否仍然提交？', 'status': 'unfinished'}, status=200)
                else:
                    # 页面不允许二次修改且没有未完成的题目
                    return JsonResponse({'message': '是否确认提交？', 'status': 'finished'}, status=200)
            elif current_page.can_modify:   # 允许修改的页面
                if unsubmitted_sub_questions.exists():  #有未完成的题目
                    page_record.submitted = False
                    page_record.save()
                    return JsonResponse({'message': '答案保存成功', 'status': 'saved'}, status=200)
                else:   #没有未完成的题目
                    page_record.submitted = True
                    page_record.save()
                    return JsonResponse({'message': '答案保存成功', 'status': 'saved'}, status=200)
        if saved:# 页面允许修改但有未完成题目 不设置为已经提交
            page_record.submitted_at = timezone.now()
            page_record.save()
            return next_page(request, exam_id, page_number)
        if force_submit:
            _save_answers_to_cache(request, page_record.id)
            # 选择“确认提交”：从缓存读取答案并保存到数据库
            _save_answers_to_database(page_record.id)
            #保存答案并跳转到下一页
            page_record.submitted = True
            page_record.submitted_at = timezone.now()
            page_record.save()
            return next_page(request, exam_id, page_number)

        else:  # 手动保存 暂存
            return _save_answers_to_cache(request, page_record.id)

    else:
        return JsonResponse({'message': '请求方法错误'}, status=400)

# def submit_exam(request):
#     if request.method == 'POST':
#         student_exam_record_id = request.POST.get('student_exam_record_id')
#         student_exam_record = get_object_or_404(StudentExamRecord, id=student_exam_record_id)
#         still_submit = request.POST.get('still_submit') == 'true'
#         # 检查所有页面是否已提交
#         pages = student_exam_record.exam.pages.all()
#         uncompleted_pages = []
#         for page in pages:
#             page_record = StudentPageRecord.objects.filter(student_exam_record=student_exam_record, page=page).first()
#             if not page_record or not page_record.submitted:
#                 uncompleted_pages.append(page.page_number)
#
#         if uncompleted_pages:
#                 # 返回带有状态的JSON响应
#             return JsonResponse({
#                 'message': '有未完成的页面，是否仍然交卷？',
#                 'status': 'exam_unfinished',
#                 'uncompleted_pages': uncompleted_pages
#             }, status=200)
#             #return HttpResponseBadRequest("所有页面必须提交后才能交卷。")
#         elif not uncompleted_pages:
#             # 返回带有状态的JSON响应
#             return JsonResponse({
#                 'message': '是否确认交卷？',
#                 'status': 'exam_finished',
#             }, status=200)
#
#         # 如果所有页面已提交/仍然提交
#         page_record.submitted = True
#         page_record.save()
#         student_exam_record.finished_at = timezone.now()
#         student_exam_record.submitted = True
#         student_exam_record.save()
#
#         return exam_result(request)  # 重定向到提交成功页面
#     else:
#         return HttpResponseBadRequest("Invalid request method.")


@login_required
def submit_exam(request):
    if request.method == 'POST':
        student_exam_record_id = request.POST.get('student_exam_record_id')
        still_submit = request.POST.get('still_submit', 'false').lower() == 'true'
        finish_submit = request.POST.get('finish_submit', 'false').lower() == 'true'
        is_manual_submit = request.POST.get('is_manual_submit', 'false').lower() == 'true'
        current_page_record_id = request.POST.get('current_page_record_id')

        if not student_exam_record_id:
            return JsonResponse({'message': '缺少考试记录 ID', 'status': 'error'}, status=400)
        try:
            student_exam_record_id = int(student_exam_record_id)
        except ValueError:
            return JsonResponse({'message': '考试记录 ID 必须是有效的数字', 'status': 'error'}, status=400)

        student_exam_record = get_object_or_404(StudentExamRecord, id=student_exam_record_id)
        pages = student_exam_record.exam.pages.all()

        if current_page_record_id:
            _save_answers_to_cache(request, current_page_record_id)
            _save_answers_to_database(current_page_record_id)
            print("save")
        unsubmitted_pages = []
        for page in pages:
            page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record, page=page)
            if not page_record.submitted:
                unsubmitted_pages.append(page.page_number)

        if unsubmitted_pages and not still_submit and not finish_submit:
            # 有未提交的页面，返回提示信息
            return JsonResponse({'message': '请', 'status': 'exam_unfinished', 'unsubmitted_pages': unsubmitted_pages}, status=200)

        elif not unsubmitted_pages:
            return JsonResponse({'message': '是否确认交卷？', 'status': 'exam_finished'}, status=200)

        if still_submit or finish_submit:
            for page in pages:
                page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record,page=page)
                page_record.submitted = True
                page_record.submitted_at = timezone.now()
                page_record.save()
            student_exam_record.submitted = True
            student_exam_record.finished_at = timezone.now()
            student_exam_record.save()
            return exam_result(request)

    else:
        return JsonResponse({'message': '请求方法错误', 'status': 'error'}, status=400)

# @login_required
# def submit_exam(request):
#     if request.method == 'POST':
#         student_exam_record_id = request.POST.get('student_exam_record_id')
#         still_submit = request.POST.get('still_submit', 'false').lower() == 'true'
#         finish_submit = request.POST.get('finish_submit', 'false').lower() == 'true'
#         is_manual_submit = request.POST.get('is_manual_submit', 'false').lower() == 'true'
#         if not student_exam_record_id:
#             return JsonResponse({'message': '缺少考试记录 ID', 'status': 'error'}, status=400)
#         try:
#             student_exam_record_id = int(student_exam_record_id)
#         except ValueError:
#             return JsonResponse({'message': '考试记录 ID 必须是有效的数字', 'status': 'error'}, status=400)
#
#         student_exam_record = get_object_or_404(StudentExamRecord, id=student_exam_record_id)
#         pages = student_exam_record.exam.pages.all()
#
#
#         # 自动保存所有页面的答案到数据库
#         unsubmitted_pages = []
#         with transaction.atomic():
#             for page in pages:
#                 page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record,
#                                                                                page=page)
#                 if page.can_modify:
#                     _save_answers_to_cache(request, page_record.id)
#                     _save_answers_to_database(page_record.id)
#                 if page.can_modify:
#                     unsubmitted_pages.append(page.page_number)
#
#         if unsubmitted_pages:
#             # 有未提交的页面，则提醒
#             return JsonResponse({'message': '有未完成的页面，是否仍然交卷？', 'status': 'exam_unfinished', 'unsubmitted_pages': unsubmitted_pages}, status=200)
#
#         elif not unsubmitted_pages:
#             return JsonResponse({'message': '是否确认交卷？', 'status': 'exam_finished'}, status=200)
#
#         if still_submit:    #选择仍然交卷
#             for page in pages:
#                 page_record, created = StudentPageRecord.objects.get_or_create(student_exam_record=student_exam_record,page=page)
#                 page_record.submitted = True
#                 page_record.save()
#             student_exam_record.submitted = True
#             student_exam_record.finished_at = timezone.now()
#             student_exam_record.save()
#             return exam_result(request)
#         if finish_submit:   #完成所有题目交卷，选择确定交卷
#             student_exam_record.submitted = True
#             student_exam_record.finished_at = timezone.now()
#             student_exam_record.save()
#             return exam_result(request)
#
#
#     else:
#         return JsonResponse({'message': '请求方法错误', 'status': 'error'}, status=400)


@login_required
def exam_result(request):
    exam = get_object_or_404(Exam)
    student_exam_record = get_object_or_404(StudentExamRecord, user=request.user, exam=exam)
    #分数未添加
    return render(request, 'exam/exam_result.html', {'exam': exam, 'student_exam_record': student_exam_record})