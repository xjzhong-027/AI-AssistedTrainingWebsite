import decimal
import json
import random
import threading
import time

from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Max, Min,Sum
from AI_module.Get_from_AI import Get_from_AI
from django.http import HttpResponse
from asgiref.sync import async_to_sync
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


from accessment.models import StudentMediaPlayRecord, StudentAnswer, StudentPageRecord,StudentExamRecord
from ELW.models import (
    TimeManagement,
    Unit,
    PaperPage,
    MediaMaterial,
    SubQuestion,
    MainQuestion,
    PageMainQuestion,
    PageSubQuestion,
    Correction, ChoiceOption, MatchingOption,
)
from Account.services.user_service_impl import UserServiceImpl
from accessment.services.exam_service_impl import ExamServiceImpl
# Note: ClassScheduleAddition and ClassScheduleAdjustment are not in UserService interface
# They are schedule-related models, not user information models
# We'll keep them as direct imports for now
from Account.models import ClassScheduleAddition, ClassScheduleAdjustment, Class
from ELW.services.content_service_impl import ContentServiceImpl
# Note: PageMainQuestion, PageSubQuestion, TimeManagement, Correction, ChoiceOption, MatchingOption 
# are not in ContentService interface, keep direct import for now
# Note: Unit, PaperPage, MainQuestion, SubQuestion, MediaMaterial are used for:
# 1. QuerySet operations (filter, none, all) - needed for compatibility
# 2. Reverse relationship queries (paper_pages, sub_questions, etc.) - not in ContentService
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseBadRequest
from Account.services.auth_service_impl import AuthServiceImpl

@AuthServiceImpl.require_login
def practice_list(request):
    """
    练习列表页面
    
    使用 @require_login 装饰器确保用户已登录。
    """

    current_username = request.session.get('username')
    if not current_username:
        return redirect('login')

    student = UserServiceImpl.get_student_by_username(current_username)
    if not student:
        return HttpResponse("学生信息不存在，请联系管理员。", status=404)

    class_instance = student.class_instance
    current_datetime = timezone.now()
    current_date = current_datetime.date()

    # 获取当前班级的所有练习单元，排除考试类型
    # Use ContentService to get units by class
    all_units = ContentServiceImpl.get_units_by_class(class_instance.id)
    practices = [u for u in all_units if u.type != 'exam']

    practice_data_list = {'practice': [], 'quiz': [], 'task': []}
    for practice in practices:
        start_week = practice.order
        class_start_date = datetime.strptime(class_instance.start_date, '%Y-%m-%d').date()  # 转换为 date 对象
        start_date = class_start_date + timedelta(weeks=start_week - 1)
        end_date = None

        if practice.type == 'quiz':
            # 截止到当周下课前
            end_date = start_date + timedelta(days=6)  # 当周的最后一天
        elif practice.type in ['practice', 'task']:
            # 截止到下周上课前
            end_date = start_date + timedelta(days=7)  # 下周的第一天

        is_overdue = current_date > end_date if end_date else False

        if practice.type == 'quiz' and is_overdue:
            # 如果是 quiz 类型且已过期，则跳过
            continue

        # 获取当前学生在该练习中的记录
        student_practice_record = ExamServiceImpl.get_exam_record(student.id, practice.id)
        if student_practice_record:
            pages = practice.paper_pages.all()
            for page in pages:
                page_record = None
                if student_practice_record:
                    page_records = ExamServiceImpl.get_page_records_by_exam(student_practice_record.id)
                    page_record = next((pr for pr in page_records if pr.page.id == page.id), None)
                if page_record:
                    if page_record.submitted:
                        page_status = "已提交"
                        is_overdue = False
                    elif is_overdue:
                        page_status = "已超时"
                    else:
                        page_status = "未提交"
                else:
                    page_status = "未提交" if not is_overdue else "已超时"
        else:
            page_status = "未提交" if not is_overdue else "已超时"

        practice_data = {
            'unit_id': practice.id,
            'title': practice.title,
            'start_date': start_date,
            'end_date': end_date,
            'is_overdue': is_overdue,
            'page_status': page_status,
        }
        practice_data_list[practice.type].append(practice_data)

    # 过滤掉没有练习的项目
    practice_data_list = {k: v for k, v in practice_data_list.items() if v}

    return render(request, 'practice/practice_list.html', {'practices': practice_data_list})

def start_practice(request, practice_id):
    # Use ContentService to get unit by ID
    practice = ContentServiceImpl.get_unit_by_id(int(practice_id))
    if not practice or practice.type not in ['practice', 'quiz', 'task']:
        from django.http import Http404
        raise Http404("Practice not found")

    username = request.session.get('username')
    if not username:
        return JsonResponse({'status': 'error', 'message': 'You are not logged in.'}, status=403)

    student = UserServiceImpl.get_student_by_username(username)
    if not student:
        return JsonResponse({'status': 'error', 'message': 'Student not found.'}, status=404)

    record = ExamServiceImpl.get_exam_record(student.id, practice.id)
    if not record:
        record = ExamServiceImpl.create_exam_record(student.id, practice.id)
        created = True
    else:
        created = False

    if created:
        record.started_at = timezone.now()
        record.save()

    first_page = practice.paper_pages.first()
    if not first_page:
        return JsonResponse({'status': 'error', 'message': 'No pages found for this practice.'}, status=404)

    return redirect('stu_practice:practice_page', practice_id=practice.id, order=first_page.order)

# 使用 ExamService 加载答案
def load_answers(student_page_record):
    return ExamServiceImpl.load_answers(student_page_record.id)

def practice_page(request, practice_id, order):
    # Use ContentService to get unit and page
    practice = ContentServiceImpl.get_unit_by_id(int(practice_id))
    if not practice or practice.type not in ['practice', 'quiz', 'task']:
        from django.http import Http404
        raise Http404("Practice not found")
    
    # Get pages for this unit and find the one with matching order
    pages = ContentServiceImpl.get_pages_by_unit(practice.id)
    page = None
    for p in pages:
        if p.order == order:
            page = p
            break
    if not page:
        from django.http import Http404
        raise Http404("Page not found")
    username = request.session.get('username')
    if not username:
        messages.error(request, "You are not logged in.")
        return redirect('login')

    student = UserServiceImpl.get_student_by_username(username)
    if not student:
        messages.error(request, "Student not found.")
        return redirect('login')
    student_practice_record = ExamServiceImpl.get_exam_record(student.id, practice.id)
    if not student_practice_record:
        student_practice_record = ExamServiceImpl.create_exam_record(student.id, practice.id)
    student_page_record = ExamServiceImpl.get_or_create_page_record(student_practice_record.id, page.id)

    page_records = ExamServiceImpl.get_page_records_by_exam(student_practice_record.id)
    page_record = next((pr for pr in page_records if pr.page.id == page.id), None)

    if page_record.submitted:
        is_submitted = True
        # 未全部提交禁止访问前页
        # all_related_submitted = True
        # related_page_records = StudentPageRecord.objects.filter(student_practice_record=student_practice_record).all()
        # related_pages = PaperPage.objects.filter(unit=practice).all()
        #
        # for rpr in related_page_records:
        #     if not rpr.submitted:
        #         all_related_submitted = False
        #         break
        #
        # record_ids = [int(id) for id in related_page_records.values_list('page_id', flat=True)]
        # related_pages_ids = [int(id) for id in related_pages.values_list('order', flat=True)]
        # if len(record_ids) != len(related_pages_ids):
        #     all_related_submitted = False
        #
        # if not all_related_submitted:
        #     if page_record.page_id != max(record_ids):
        #         return practice_page(request, practice_id, order+1)
    else:
        is_submitted = False

    page_main_questions = PageMainQuestion.objects.filter(page=page)
    main_questions = [pmq.main_question for pmq in page_main_questions]

    page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
    sub_questions = [psq.sub_question for psq in page_sub_questions]
    student_answers_iterable = StudentAnswer.objects.filter(student_page_record=page_record)
    student_answers = []
    for answer in student_answers_iterable:
        student_answers.append(answer)

    # 获取小题答案和学生分数
    graded_answers = []
    scores = {}
    if page_record.is_graded:
        graded_answers = {sq.id:sq.answer for sq in sub_questions}
        for sa in student_answers:
            if sa.score != None: scores[sa.sub_question_id] = int(sa.score)
            elif sa.sub_question.main_question.question_type == 'comprehension': scores[sa.sub_question_id] = '批改中'
            else: scores[sa.sub_question_id] = '批改错误'

    media_materials = MediaMaterial.objects.filter(main_questions__in=main_questions).distinct()

    random.seed(student_practice_record.user.id)
    answers_dict = load_answers(student_page_record)

    blank_data = {}
    correction_data = {}
    for main_question in main_questions:
        if main_question.question_type == 'blank':
            blank_sub_questions = main_question.sub_questions.all().order_by('id')
            html_parts = []
            for sub_q in blank_sub_questions:
                blanks = sub_q.blanks.order_by('-index')
                words = sub_q.question_text.split()
                for blank in blanks:
                    if 0 <= blank.index < len(words):
                        answer = answers_dict.get(sub_q.id, '')
                        if is_submitted: input_html = f'<input type="text" class="blank-input" name="answer_{sub_q.id}" id="answer_{sub_q.id}" value="{answer}" disabled/>'
                        else: input_html = f'<input type="text" class="blank-input" name="answer_{sub_q.id}" id="answer_{sub_q.id}" value="{answer}" />'
                        words.insert(blank.index + 1, input_html)
                processed_text = ' '.join(words)
                html_parts.append(processed_text)
            processed_html = ' '.join(html_parts)
            blank_data[main_question.id] = processed_html

        elif main_question.question_type == 'choice':
            for sub_question in sub_questions:
                options = list(sub_question.options.all())
                random.shuffle(options)
                sub_question.shuffled_options = options

        elif main_question.question_type == 'correction':
            correction_sub_questions = main_question.sub_questions.all().order_by('id')
            full_text = ' '.join(sub_q.question_text for sub_q in correction_sub_questions)

            word_data = []
            for sub_q in correction_sub_questions:
                sub_q_words = sub_q.question_text.split()
                for local_index, word in enumerate(sub_q_words):
                    word_data.append({
                        'word': word,
                        'sub_question_id': sub_q.id,
                        'local_index': local_index,
                    })

            correction_data[main_question.id] = {
                'html': full_text,
                'words': word_data,
                'sub_questions': correction_sub_questions,
            }

    main_question_ids = [mq.id for mq in main_questions]
    play_records = ExamServiceImpl.get_media_play_records_by_exam(
        student_practice_record.id,
        main_question_ids
    )
    play_records_dict = {record.main_question_id: record.play_count for record in play_records}

    # Check if this is the last page using ContentService
    pages = ContentServiceImpl.get_pages_by_unit(practice.id)
    is_last_page = not any(p.order == page.order + 1 for p in pages)

    context = {
        'practice': practice,
        'page': page,
        'student_practice_record': student_practice_record,
        'student_page_record': student_page_record,
        'current_page_record_id': student_page_record.id,
        'main_questions': main_questions,
        'media_materials': media_materials,
        'sub_questions': sub_questions,
        'order': page.order,
        'answers': json.dumps(answers_dict, cls=DjangoJSONEncoder),
        'is_last_page': is_last_page,
        'practice_record_id': student_practice_record.id,
        'started_at': student_practice_record.started_at,
        'ended_at': student_practice_record.ended_at,
        'MEDIA_URL': settings.MEDIA_URL,
        'play_records': play_records_dict,
        'remaining_time': student_page_record.remaining_time,
        'blank_data': blank_data,
        'correction_data': correction_data,
        'page_submitted': is_submitted,
        'can_modify': is_submitted,
        'graded_answers': graded_answers,
        'scores':scores,
    }
    return render(request, 'practice/practice_page.html', context)

@csrf_exempt
def update_remaining_time(request, page_record_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        remaining_time = data.get('remaining_time')

        student_page_record = get_object_or_404(StudentPageRecord, id=page_record_id)
        student_page_record.remaining_time = remaining_time
        if student_page_record.remaining_time <= 0:
            student_page_record.is_expired = True
        student_page_record.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def next_page(request, practice_id, order):
    # Use ContentService to get unit and page
    practice = ContentServiceImpl.get_unit_by_id(int(practice_id))
    if not practice or practice.type not in ['practice', 'quiz', 'task']:
        from django.http import Http404
        raise Http404("Practice not found")
    
    # Get pages for this unit and find the one with matching order
    pages = ContentServiceImpl.get_pages_by_unit(practice.id)
    current_page = None
    for p in pages:
        if p.order == order:
            current_page = p
            break
    if not current_page:
        from django.http import Http404
        raise Http404("Page not found")
    next_page = practice.paper_pages.filter(order=current_page.order + 1).first()
    username = request.session.get('username')
    if not username:
        messages.error(request, "You are not logged in.")
        return redirect('login')

    student = UserServiceImpl.get_student_by_username(username)
    if not student:
        messages.error(request, "Student not found.")
        return redirect('login')

    page_main_questions = PageMainQuestion.objects.filter(page=current_page)
    main_questions = [pmq.main_question for pmq in page_main_questions]

    # 检查是否所有问题都达到了最少播放次数
    student_practice_record = ExamServiceImpl.get_exam_record(student.id, practice.id)
    if not student_practice_record:
        student_practice_record = ExamServiceImpl.create_exam_record(student.id, practice.id)
    main_question_ids = [mq.id for mq in main_questions]
    play_records = ExamServiceImpl.get_media_play_records_by_exam(
        student_practice_record.id,
        main_question_ids
    )

    for main_question in main_questions:
        play_record = play_records.filter(main_question=main_question).first()
        if play_record and play_record.play_count >= main_question.minimum_play:
            # 检查是否为最后一页
            if not next_page:
                # 提示已完成考试，留在当前页面
                messages.success(request, 'You have completed the practice.')
                return redirect('stu_practice:practice_page', practice_id=practice.id, order=current_page.order)
            else:
                # 跳转到下一页
                return redirect('stu_practice:practice_page', practice_id=practice.id, order=next_page.order)

        else:
            #return JsonResponse({'message': f"You need to play the media at least {main_question.minimum_play} times"})
            # messages.error(request,f"You need to play the media at least {main_question.minimum_play} times")
            if main_question.minimum_play <= 0:
                return redirect('stu_practice:practice_page', practice_id=practice.id, order=next_page.order)
            else:
                return redirect('stu_practice:practice_page', practice_id=practice.id, order=current_page.order)

# 辅助函数：从 request.POST 提取答案数据（复用 accessment 的逻辑）
def _extract_answers_from_request(request, page_record_id):
    """从 request.POST 提取答案数据"""
    page_record = ExamServiceImpl.get_page_record_by_id(page_record_id)
    if not page_record:
        return {}
    
    page_main_questions = PageMainQuestion.objects.filter(page=page_record.page)
    page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
    sub_questions = [psq.sub_question for psq in page_sub_questions]
    
    cached_answers = cache.get(f"answers_{page_record_id}", {})
    
    for sub_question in sub_questions:
        sub_question_id = sub_question.id
        main_question = sub_question.main_question
        question_type = main_question.question_type
        answer_text = ""
        
        if question_type == 'choice':
            selected_option = request.POST.get(f'answer_{sub_question_id}')
            answer_text = selected_option
        elif question_type == 'matching':
            answers = request.POST.getlist(f'answer_{sub_question_id}')
            answer_text = ','.join(answers)
        elif question_type == 'correction':
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
            answer_text = json.dumps(answer_text)
        else:
            answer_text = request.POST.get(f'answer_{sub_question_id}', '').strip()
        
        cached_answers[sub_question_id] = answer_text
    
    return cached_answers

def _save_answers_to_cache(request, page_record_id):
    """保存答案到缓存"""
    answers_data = _extract_answers_from_request(request, page_record_id)
    ExamServiceImpl.save_answers_to_cache(page_record_id, answers_data)
    return JsonResponse({'message': '已保存'})

# _update_cache 已移至 ExamServiceImpl，不再需要

def _save_answers_to_database(page_record_id):
    """从缓存中读取答案并保存到数据库"""
    ExamServiceImpl.save_answers_to_database(page_record_id)
    return JsonResponse({'message': '已保存'})

@csrf_exempt
def save_page(request, practice_id, order):
    if request.method == 'POST':
        # Use ContentService to get unit and page
        practice = ContentServiceImpl.get_unit_by_id(int(practice_id))
        if not practice or practice.type not in ['practice', 'quiz', 'task']:
            from django.http import Http404
            raise Http404("Practice not found")
        
        # Get pages for this unit and find the one with matching order
        pages = ContentServiceImpl.get_pages_by_unit(practice.id)
        current_page = None
        for p in pages:
            if p.order == order:
                current_page = p
                break
        if not current_page:
            from django.http import Http404
            raise Http404("Page not found")
        username = request.session.get('username')
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return JsonResponse({'message': '学生信息不存在', 'status': 'error'}, status=404)
        student_practice_record = get_object_or_404(StudentExamRecord, user=student, exam=practice)
        page_record = ExamServiceImpl.get_or_create_page_record(student_practice_record.id, current_page.id)
        can_modify = page_record.submitted

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
            if can_modify:
                # if not unsubmitted_main_questions:
                page_record.submitted = True
                page_record.save()

        if is_manual_submit:
            return JsonResponse({'message': '是否确认提交？', 'status': 'finished'}, status=200)
        elif force_submit:
            _save_answers_to_cache(request, page_record.id)
            _save_answers_to_database(page_record.id)
            page_record.submitted = True
            page_record.submitted_at = timezone.now()

            # Check if this is the last page using ContentService
            pages = ContentServiceImpl.get_pages_by_unit(practice.id)
            is_last_page = not any(p.order == order + 1 for p in pages)

            if is_last_page:
                student_practice_record.submitted = True
                student_practice_record.finished_at = timezone.now()

                student_practice_record.save()
            page_record.save()
            grade_page(page_record)
            return JsonResponse({'message': '答案已提交，页面将重新加载', 'status': 'reload'}, status=200)

        return _save_answers_to_cache(request, page_record.id)
    else:
        return JsonResponse({'message': '请求方法错误'}, status=400)

def submit_practice(request):
    if request.method == 'POST':
        student_practice_record_id = request.POST.get('student_practice_record_id')
        still_submit = request.POST.get('still_submit', 'false').lower() == 'true'
        finish_submit = request.POST.get('finish_submit', 'false').lower() == 'true'
        force_submit = request.POST.get('force_submit', 'false').lower() == 'true'

        if not student_practice_record_id:
            return JsonResponse({'message': '缺少练习记录 ID', 'status': 'error'}, status=400)
        try:
            student_practice_record_id = int(student_practice_record_id)
        except ValueError:
            return JsonResponse({'message': '练习记录 ID 必须是有效的数字', 'status': 'error'}, status=400)

        # 获取学生的练习记录
        student_practice_record = get_object_or_404(StudentExamRecord, id=student_practice_record_id)
        unit = student_practice_record.exam
        pages = unit.paper_pages.all()
        # 获取所有页面记录
        page_records = ExamServiceImpl.get_page_records_by_exam(student_practice_record.id)

        if force_submit:
            for page in pages:
                page_record = ExamServiceImpl.get_or_create_page_record(student_practice_record.id, page.id)
                page_record.submitted = True
                page_record.submitted_at = timezone.now()
                page_record.save()
            student_practice_record.submitted = True
            student_practice_record.finished_at = timezone.now()
            student_practice_record.save()

            student_practice_record.submitted = True
            student_practice_record.finished_at = timezone.now()
            student_practice_record.save()

            # 批改所有已提交的页面
            for page_record in page_records:
                if (student_practice_record.submitted and page_record.submitted and not page_record.is_graded):
                    try:
                        # 调用批改函数
                        grade_page(page_record)
                    except Exception as e:
                        print(f"Error grading page {page_record.page.order}: {e}")

        unsubmitted_pages = []

        if unsubmitted_pages and not still_submit and not finish_submit and not force_submit:
            # 有未提交的页面，返回提示信息
            return JsonResponse({'message': '有未完成的页面，是否仍然交卷？', 'status': 'unfinished', 'unsubmitted_pages': unsubmitted_pages}, status=200)
        elif not unsubmitted_pages and not force_submit and not finish_submit:
            return JsonResponse({'message': '是否确认交卷？', 'status': 'finished'}, status=200)

        if still_submit or finish_submit:
            for page in pages:
                page_record = ExamServiceImpl.get_or_create_page_record(student_practice_record.id, page.id)
                page_record.submitted = True
                page_record.submitted_at = timezone.now()
                page_record.save()
            student_practice_record.submitted = True
            student_practice_record.finished_at = timezone.now()
            student_practice_record.save()

            # 批改所有已提交的页面
            for page_record in page_records:
                if (student_practice_record.submitted and page_record.submitted and not page_record.is_graded):
                    try:
                        # 调用批改函数
                        grade_page(page_record)
                    except Exception as e:
                        print(f"Error grading page {page_record.page.order}: {e}")

            # 更新练习记录的总分
            try:
                page_records_graded = [pr for pr in ExamServiceImpl.get_page_records_by_exam(student_practice_record.id) if pr.is_graded]
                total_score = sum(pr.page_score for pr in page_records_graded if pr.page_score is not None) or 0
                student_practice_record.score = total_score
                student_practice_record.save()
            except Exception as e:
                print(f"Error updating record score: {e}")
            return redirect('stu_practice:practice_result', practice_id=unit.id)  # 跳转到评分页面
    else:
        return JsonResponse({'message': '请求方法错误', 'status': 'error'}, status=400)

def practice_result(request, practice_id):
    # Use ContentService to get unit by ID
    practice = ContentServiceImpl.get_unit_by_id(int(practice_id))
    if not practice:
        from django.http import Http404
        raise Http404("Practice not found")
    student_practice_record = get_object_or_404(StudentExamRecord, exam=practice)
    page_records = ExamServiceImpl.get_page_records_by_exam(student_practice_record.id)

    question_scores = []
    for page_record in page_records:
        student_answers = StudentAnswer.objects.filter(student_page_record=page_record)
        for answer in student_answers:
            if answer.score != None:
                if(answer.sub_question.main_question.question_type == "comprehension" and answer.score < 0):
                    question_scores.append({
                        'sub_question_type': answer.sub_question.main_question.question_type,
                        'sub_question_text': answer.sub_question.question_text,
                        'score': "批改中",
                    })
                else:
                    question_scores.append({
                        'sub_question_type': answer.sub_question.main_question.question_type,
                        'sub_question_text': answer.sub_question.question_text,
                        'score': answer.score
                    })
            else:
                question_scores.append({
                    'sub_question_type': answer.sub_question.main_question.question_type,
                    'sub_question_text': answer.sub_question.question_text,
                    'score': "暂无数据"
                })
    try:
        total_score = sum(score['score'] for score in question_scores if isinstance(score['score'], decimal.Decimal))
    except Exception as e:
        print(f"practice_result: Error counting score: {e}")
        total_score = -999

    context = {
        'question_scores': question_scores,
        'total_score': total_score,
    }
    return render(request, 'practice/practice_result.html', context)

# grade_page 已移至 ExamServiceImpl，使用 ExamServiceImpl.grade_page(page_record.id)
def grade_page(page_record):
    """批改页面（已废弃，使用 ExamServiceImpl.grade_page）"""
    return ExamServiceImpl.grade_page(page_record.id)

@csrf_exempt
@require_POST
def update_play_count(request):
    try:
        data = json.loads(request.body)
        student_practice_record_id = data.get("student_practice_record_id")
        main_question_id = data.get("main_question_id")
        media_material_id = data.get("media_material_id")

        if not student_practice_record_id or not main_question_id or not media_material_id:
            return JsonResponse({"success": False, "message": "Invalid request data."}, status=400)

        student_practice_record = ExamServiceImpl.get_exam_record_by_id(int(student_practice_record_id))
        if not student_practice_record:
            return JsonResponse({"success": False, "message": "Exam record not found."}, status=404)
        # Use ContentService to get main question and media material by ID
        main_question = ContentServiceImpl.get_main_question_by_id(int(main_question_id))
        if not main_question:
            return JsonResponse({"success": False, "message": "Main question not found."}, status=404)
        media_material = ContentServiceImpl.get_media_material_by_id(int(media_material_id))
        if not media_material:
            return JsonResponse({"success": False, "message": "Media material not found."}, status=404)

        # 获取或创建播放记录
        play_record = ExamServiceImpl.get_media_play_record(
            int(student_practice_record_id),
            int(main_question_id)
        )
        
        if not play_record:
            # 创建新记录
            play_record = ExamServiceImpl.update_media_play_record(
                int(student_practice_record_id),
                int(main_question_id),
                0,
                0.0
            )
        
        if play_record.play_count >= main_question.maximum_play:
            return JsonResponse({"success": False, "message": "Maximum play count reached. Cannot play anymore."}, status=403)

        # 更新播放次数
        ExamServiceImpl.update_media_play_record(
            int(student_practice_record_id),
            int(main_question_id),
            play_record.play_count + 1,
            play_record.last_pause_time
        )

        return JsonResponse({"success": True, "message": "Play count updated successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

# grade_comprehension 和 background_grade_comprehension 已移至 ExamServiceImpl
# 使用 ExamServiceImpl.grade_comprehension(sub_question_id, student_answer_id)

@login_required
def student_dashboard(request):
    # Note: This view uses Django User object, not username
    # UserService doesn't have get_student_by_user method yet
    # For now, we'll get username from session or user object
    username = request.session.get('username') or request.user.username
    student = UserServiceImpl.get_student_by_username(username)
    if not student:
        return HttpResponse("学生信息不存在，请联系管理员。", status=404)

    # 获取学生的练习记录
    practice_records = ExamServiceImpl.get_exam_records_by_user(student.id)

    # 获取学生的成绩统计
    practice_scores = []
    for record in practice_records:
        page_records = ExamServiceImpl.get_page_records_by_exam(record.id)
        page_records_graded = [pr for pr in page_records if pr.is_graded]
        total_score = sum(pr.page_score for pr in page_records_graded if pr.page_score is not None) or 0
        practice_scores.append({
            'practice': record.exam,
            'total_score': total_score,
            'started_at': record.started_at,
            'finished_at': record.finished_at,
        })

    # 获取学生的个人信息
    student_info = {
        'username': student.username,
        'name': student.name,
        'class_instance': student.class_instance,
        'seat_number': student.seat_number,
    }

    context = {
        'student_info': student_info,
        'practice_scores': practice_scores,
    }
    return render(request, 'practice/student_dashboard.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        old = request.POST['old_password']
        new = request.POST['new_password']
        confirm = request.POST['confirm_password']
        # Note: This view uses Django User object and password
        # UserService doesn't have get_student_by_user method yet
        # For now, we'll get username from session or user object
        username = request.session.get('username') or request.user.username
        student = UserServiceImpl.get_student_by_username(username)
        # Check password separately since UserService doesn't handle password verification
        if student and student.password != old:
            student = None

        if student and (new == confirm):
            student.password = new
            student.save()
            messages.success(request, '密码修改成功。')
            return render(request, 'practice/change_password.html')
        elif new != confirm:
            messages.error(request, '新密码与确认密码不一致。')
            return render(request, 'practice/change_password.html')
        else:
            messages.error(request, '当前密码错误。')
            return render(request, 'practice/change_password.html')
    else:
        return render(request, 'practice/change_password.html', {})