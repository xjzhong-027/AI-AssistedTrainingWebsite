import json, pytz
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django import forms
from django.contrib import messages
from django.core import serializers
from django.http import JsonResponse, QueryDict, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from announce.forms import AnnouncementForm
from announce.models import Announcement, Message
from .models import ClassroomLayout, OverdueDeductionRule, OverduePeriod
from Account.models import Class, Students, Teachers, Attendance, ClassScheduleAdjustment, ClassScheduleAddition
from ELW.models import Unit, TimeManagement, PaperPage, PageMainQuestion, PageSubQuestion, Correction, ChoiceOption, \
    MatchingOption, Blank
from accessment.models import StudentExamRecord, StudentPageRecord, StudentAnswer, StudentMediaPlayRecord
from .forms import AttendanceQueryForm, ClassScheduleAdjustmentForm, ClassScheduleAdditionForm, \
    ClassroomLayoutForm, OverdueRuleForm, OverduePeriodFormSet, OverduePeriodForm

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# -------------------------- 查询总面板--------------------------------------
def query(request):
    return render(request, 'query_base.html')




# -------------------------- 考勤管理+调课补课管理--------------------------------------
def attendance_query(request):
    """ 考勤查询 """
    if not request.session.get('is_login', None):
        return redirect('login')  # 如果用户未登录，重定向到登录页面

    form = AttendanceQueryForm(request.GET or None)
    attendances = []
    class_info = None
    class_time = []
    status_choices = dict(Attendance._meta.get_field('status').choices)

    username = request.session.get('username', None)
    teacher_instance = Teachers.objects.get(username=username)
    classes = Class.objects.filter(teacher=teacher_instance)
    class_choices = [(cls.id, cls.class_name) for cls in classes]

    # 动态设置班级选择项
    form.fields['class_field'].choices = class_choices

    if form.is_valid():
        week = form.cleaned_data['week']
        class_id = form.cleaned_data['class_field']

        # 查询班级记录
        class_info = Class.objects.get(id=class_id)
        class_time.append(f"周{ class_info.week } — { class_info.start_time } - { class_info.end_time }")
        # 获取该班级所有学生
        students = Students.objects.filter(class_instance=class_info)
        adjustment = ClassScheduleAdjustment.objects.filter(class_instance=class_info, week=week).first()
        additions = ClassScheduleAddition.objects.filter(class_instance=class_info, week=week)
        if adjustment:
            class_time.append(f"周{ adjustment.new_week_day } — { adjustment.new_class_begin_time } - { adjustment.new_class_end_time }")
        if additions:
            for addition in additions:
                class_time.append(f"周{ addition.weekday } — { addition.class_begin_time } - { addition.class_end_time }")

        # 查询学生考勤记录
        for student in students:
            student_attendances = Attendance.objects.filter(student=student, week=week)
            for attendance in student_attendances:
                # 在前端显示中文字段
                attendance.status_display = status_choices.get(attendance.status, '未知状态')
                attendances.append(attendance)

    if request.method == 'POST':
        action = request.POST.get('action')  # 获取提交的按钮的值

        if action == 'update_all':
            # 统一修改所有学生的考勤状态
            status = request.POST.get('status')
            selected_attendance_ids = request.POST.getlist('attendance_ids')
            if selected_attendance_ids:
                Attendance.objects.filter(id__in=selected_attendance_ids).update(status=status)
                messages.success(request, "所有学生的考勤状态已更新。")
            else:
                messages.error(request, "请至少选择一条考勤记录。")
            # 保持查询参数在 URL 中，重新加载页面
            query_params = QueryDict(mutable=True)
            query_params['week'] = week
            query_params['class_field'] = class_id
            return redirect(f"{request.path}?{query_params.urlencode()}")

        if action == 'update_selected':
            # 单独修改选中的学生的考勤状态
            for attendance in attendances:
                status_key = f"status_{attendance.id}"
                if status_key in request.POST:
                    new_status = request.POST.get(status_key)
                    if new_status:
                        attendance.status = new_status
                        attendance.save()
            messages.success(request, "选中的考勤记录已更新。")
            # 保持查询参数在 URL 中，重新加载页面
            query_params = QueryDict(mutable=True)
            query_params['week'] = week
            query_params['class_field'] = class_id
            return redirect(f"{request.path}?{query_params.urlencode()}")

    # 分页，设置每页显示10条记录
    paginator = Paginator(attendances, 10)
    page_number = request.GET.get('page')  # 获取当前页码

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'attendance/attendance_query.html', {
        'form': form,
        'attendances': page_obj,
        'class_info': class_info,
        'class_time': class_time,
        'status_choices': status_choices
    })
# def attendance_query(request):
#     """ 考勤查询 """
#     form = AttendanceQueryForm(request.GET or None)
#     attendances = []
#     class_info = None
#     class_time = []
#     # 获取 status 字段的所有选择项
#     status_choices = dict(Attendance._meta.get_field('status').choices)
#
#
#     if request.session.get('is_login', None):
#         username = request.session.get('username', None)
#         teacher_instance = Teachers.objects.get(username=username)
#         classes = Class.objects.filter(teacher=teacher_instance)
#         class_choices = [(cls.id, cls.class_name) for cls in classes]
#
#         # 动态设置班级选择项
#         form.fields['class_field'].choices = class_choices
#
#         if form.is_valid():
#             week = form.cleaned_data['week']
#             class_id = form.cleaned_data['class_field']
#
#             # 查询班级记录
#             class_info = Class.objects.get(id=class_id)
#             class_time.append(f"周{ class_info.week } — { class_info.start_time } - { class_info.end_time }")
#             # 获取该班级所有学生
#             students = Students.objects.filter(class_instance=class_info)
#             adjustment = ClassScheduleAdjustment.objects.filter(class_instance=class_info, week=week).first()
#             additions = ClassScheduleAddition.objects.filter(class_instance=class_info, week=week)
#             if adjustment:
#                 class_time.append(f"周{ adjustment.new_week_day } — { adjustment.new_class_begin_time } - { adjustment.new_class_end_time }")
#             if additions:
#                 for addition in additions:
#                     class_time.append(f"周{ addition.weekday } — { addition.class_begin_time } - { addition.class_end_time }")
#
#             # 查询学生考勤记录
#             for student in students:
#                 student_attendances = Attendance.objects.filter(student=student, week=week)
#                 for attendance in student_attendances:
#                     # 在前端显示中文字段
#                     attendance.status_display = status_choices.get(attendance.status, '未知状态')
#                     attendances.append(attendance)
#
#
#         if request.method == 'POST':
#             action = request.POST.get('action')  # 获取提交的按钮的值
#
#             if action == 'update_all':
#                 # 统一修改所有学生的考勤状态
#                 status = request.POST.get('status')
#                 selected_attendance_ids = request.POST.getlist('attendance_ids')
#                 if selected_attendance_ids:
#                     Attendance.objects.filter(id__in=selected_attendance_ids).update(status=status)
#                     messages.success(request, "所有学生的考勤状态已更新。")
#                 else:
#                     messages.error(request, "请至少选择一条考勤记录。")
#                 # 保持查询参数在 URL 中，重新加载页面
#                 query_params = QueryDict(mutable=True)
#                 query_params['week'] = week
#                 query_params['class_field'] = class_id
#                 return redirect(f"{request.path}?{query_params.urlencode()}")
#
#             if action == 'update_selected':
#                 # 单独修改选中的学生的考勤状态
#                 for attendance in attendances:
#                     status_key = f"status_{attendance.id}"
#                     if status_key in request.POST:
#                         new_status = request.POST.get(status_key)
#                         if new_status:
#                             attendance.status = new_status
#                             attendance.save()
#                 messages.success(request, "选中的考勤记录已更新。")
#                 # 保持查询参数在 URL 中，重新加载页面
#                 query_params = QueryDict(mutable=True)
#                 query_params['week'] = week
#                 query_params['class_field'] = class_id
#                 return redirect(f"{request.path}?{query_params.urlencode()}")
#
#     # 分页，设置每页显示5条记录
#     paginator = Paginator(attendances, 10)
#     page_number = request.GET.get('page')  # 获取当前页码
#     page_obj = paginator.get_page(page_number)
#
#     return render(request, 'attendance/attendance_query.html', {
#         'form': form,
#         'attendances': page_obj,
#         'class_info': class_info,
#         'class_time': class_time,
#         'status_choices': status_choices
#     })


def adjust_class_schedule(request):
    """ 调课+补课 """
    if request.session.get('is_login', None):
        username = request.session.get('username', None)
        teacher_instance = Teachers.objects.get(username=username)
        class_choices = Class.objects.filter(teacher=teacher_instance)

        if request.method == 'POST':
            # 分别处理调课和补课表单
            adjustment_form = ClassScheduleAdjustmentForm(request.POST, class_choices=class_choices)
            addition_form = ClassScheduleAdditionForm(request.POST, class_choices=class_choices)

            if adjustment_form.is_valid():
                # 保存调课记录
                adjustment = adjustment_form.save(commit=False)
                adjustment.teacher = teacher_instance
                adjustment.save()

                # 更新学生考勤记录表中的 adjusted_class_time 字段
                class_instance = adjustment.class_instance
                students = Students.objects.filter(class_instance=class_instance)
                for student in students:
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        week=adjustment.week,
                        defaults={'status': 'absent', 'adjusted_class_time': adjustment, 'added_class_time': None}
                    )
                    if not created:
                        attendance.adjusted_class_time = adjustment
                        attendance.save()

                messages.success(request, '成功添加调课！')

            if addition_form.is_valid():
                # 保存补课记录
                addition = addition_form.save(commit=False)
                addition.teacher = teacher_instance
                addition.save()

                # 为每个学生添加考勤记录
                class_instance = addition.class_instance
                students = Students.objects.filter(class_instance=class_instance)
                for student in students:
                    Attendance.objects.update_or_create(
                        student=student,
                        week=addition.week,
                        status='absent',
                        adjusted_class_time=None,
                        added_class_time=addition
                    )

                messages.success(request, '成功添加补课！')

            return redirect(request.path)  # 调整和补课成功后刷新页面

        else:
            # 初始化空的表单，并传递 class_choices
            adjustment_form = ClassScheduleAdjustmentForm(class_choices=class_choices)
            addition_form = ClassScheduleAdditionForm(class_choices=class_choices)

        # 筛选当前教师的调课和补课记录
        schedule_adjustments = ClassScheduleAdjustment.objects.filter(
            class_instance__teacher=teacher_instance
        ).order_by('-id')

        schedule_additions = ClassScheduleAddition.objects.filter(
            class_instance__teacher=teacher_instance
        ).order_by('-id')

    else:
        # 如果用户未登录，初始化空的表单
        adjustment_form = ClassScheduleAdjustmentForm()
        addition_form = ClassScheduleAdditionForm()
        schedule_adjustments = ClassScheduleAdjustment.objects.none()
        schedule_additions = ClassScheduleAddition.objects.none()

    # 分页，设置每页显示10条记录
    paginator_adjustments = Paginator(schedule_adjustments, 10)
    paginator_additions = Paginator(schedule_additions, 10)

    page_number_adjustments = request.GET.get('page_adjustments')  # 获取当前调课页码
    page_number_additions = request.GET.get('page_additions')  # 获取当前补课页码

    try:
        page_obj_adjustments = paginator_adjustments.page(page_number_adjustments)
    except PageNotAnInteger:
        page_obj_adjustments = paginator_adjustments.page(1)
    except EmptyPage:
        page_obj_adjustments = paginator_adjustments.page(paginator_adjustments.num_pages)

    try:
        page_obj_additions = paginator_additions.page(page_number_additions)
    except PageNotAnInteger:
        page_obj_additions = paginator_additions.page(1)
    except EmptyPage:
        page_obj_additions = paginator_additions.page(paginator_additions.num_pages)

    return render(request, 'attendance/adjust_schedule.html', {
        'adjustment_form': adjustment_form,
        'addition_form': addition_form,
        'schedule_adjustments': page_obj_adjustments,
        'schedule_additions': page_obj_additions,
    })


def batch_delete_schedule_adjustments(request):
    """ 批量删除调课记录 """
    if request.method == 'POST':
        selected_records = request.POST.getlist('selected_adjustment_records')  # 使用表单中复选框的name 'selected_adjustment_records'获取选中的记录ID

        if selected_records:
            # 将选中的调课记录删除
            ClassScheduleAdjustment.objects.filter(id__in=selected_records).delete()
            messages.success(request, "选中的调课记录已成功删除")
        else:
            messages.warning(request, "未选择任何调课记录")

        return redirect("Query:adjust_schedule")

    return redirect("Query:adjust_schedule")


def batch_delete_schedule_additions(request):
    """ 批量删除补课记录 """
    if request.method == 'POST':
        selected_records = request.POST.getlist('selected_addition_records')  # 获取选中的记录ID

        if selected_records:
            # 将选中的补课记录删除
            ClassScheduleAddition.objects.filter(id__in=selected_records).delete()
            messages.success(request, "选中的补课记录已成功删除")
        else:
            messages.warning(request, "未选择任何补课记录")

        return redirect("Query:adjust_schedule")

    return redirect("Query:adjust_schedule")


def class_seat_plan(request, class_id):
    """ 班级座位表 """
    # 获取班级信息
    class_obj = get_object_or_404(Class, id=class_id)

    # 获取该班级的所有学生及其座位号
    students = Students.objects.filter(class_instance=class_obj)

    if request.method == 'POST':
        form = ClassroomLayoutForm(request.POST, class_obj=class_obj)
        if form.is_valid():
            layout, created = ClassroomLayout.objects.get_or_create(class_instance=class_obj)

            layout.seat_rows = form.cleaned_data['seat_rows']
            layout.seat_cols = form.cleaned_data['seat_cols']
            layout.save()
            messages.success(request, "成功设置课室！")
            return redirect(request.path)
    else:
        form = ClassroomLayoutForm(class_obj=class_obj)

        # 获取课室的行数和列数
        classroom = ClassroomLayout.objects.filter(class_instance=class_obj).first()
        if classroom is not None:
            rows = classroom.seat_rows
            columns = classroom.seat_cols
        else:
            rows = 10
            columns = 10

        # 生成课室座位的布局
        seats = []
        for row in range(1, rows + 1):
            row_seats = []
            for col in range(1, columns + 1):
                seat = f"{chr(64 + col)}{row}"  # 生成座位号，例如 B5
                student_in_seat = students.filter(seat_number=seat).first()
                student_name = student_in_seat.name if student_in_seat else None
                row_seats.append({'seat': seat, 'student_name': student_name})
            seats.append(row_seats)

        # 生成列字母（从 A 开始，最多到 Z）
        column_letters = [chr(65 + i) for i in range(columns)]  # 生成 A, B, C, ..., Z

    # 分页，设置每页显示5个学生
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')  # 获取当前页码
    page_obj = paginator.get_page(page_number)

    return render(request, 'attendance/class_seat_plan.html', {
        'class': class_obj,
        'seats': seats,
        'columns': columns,
        'rows': rows,
        'column_letters': column_letters,  # 传递列字母
        'students': page_obj,
        'form': form
    })


@csrf_exempt
def update_seat_number(request):
    """ 修改学生座位号 """
    if request.method == "POST":
        # 解析请求中的数据
        data = json.loads(request.body)
        student_id = data.get('student_id')
        seat_number = data.get('seat_number')

        # 查找相应的学生记录并更新
        try:
            student = Students.objects.get(id=student_id)
            student.seat_number = seat_number
            student.save()
            return JsonResponse({"success": True})
        except Students.DoesNotExist:
            return JsonResponse({"success": False, "message": "学生记录未找到"})
    return JsonResponse({"success": False, "message": "无效请求"})






# -------------------------- 学习记录管理--------------------------------------
def student_learning_search(request):
    """ 查询学生 """
    if not request.session.get('is_login', None):
        return redirect('login')  # 如果用户未登录，重定向到登录页面

    username = request.session.get('username', None)
    teacher_instance = Teachers.objects.get(username=username)
    class_instances = Class.objects.filter(teacher=teacher_instance)
    students = Students.objects.filter(class_instance__in=class_instances)

    # 获取学生学号，如果有输入则进行过滤
    search_username = request.GET.get('username', '')

    if search_username:
        students = students.filter(username__icontains=search_username)

    # 分页，设置每页显示5条记录
    paginator = Paginator(students, 5)
    page_number = request.GET.get('page')  # 获取当前页码

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'learning/student_learning_search.html', {
        'students': page_obj,
        'username': search_username
    })


def assignment_unit(request, student_id):
    """ 学生学习总体情况 """
    student = Students.objects.get(id=student_id)
    class_instance = student.class_instance
    units = Unit.objects.filter(class_instance=class_instance)
    assignments_data = []
    categories = dict(Unit.TYPES)
    now = datetime.now(pytz.utc)

    if units:
        for unit in units:
            week = 0

            if unit.type == "exam":
                time = TimeManagement.objects.filter(unit=unit).first()
                unit_time_data = f"{time.exam_date} {time.end_time}"
                print("unit_time_data:", unit_time_data)
            elif unit.type == "quiz":
                # 解析开课日期
                start_date_obj = datetime.strptime(class_instance.start_date, '%Y-%m-%d')
                week = TimeManagement.objects.filter(unit=unit).first().week
                # 计算日期范围
                date_1 = start_date_obj + timedelta(days=(week - 1) * 7)
                date_1_str = date_1.strftime('%Y-%m-%d')
                unit_time_data = f"{date_1_str} {class_instance.end_time}"
            elif unit.type == "task":
                # 解析开课日期
                start_date_obj = datetime.strptime(class_instance.start_date, '%Y-%m-%d')
                # 计算日期范围
                # date_1 = start_date_obj + timedelta(days=(unit.order - 1) * 7)
                # date_1_str = date_1.strftime('%Y-%m-%d')
                date_2 = start_date_obj + timedelta(days=unit.order * 7)
                date_2_str = date_2.strftime('%Y-%m-%d')
                unit_time_data = f"{date_2_str} {class_instance.start_time}"
            else:
                # 解析开课日期
                start_date_obj = datetime.strptime(class_instance.start_date, '%Y-%m-%d')
                # 计算日期范围
                date_1 = start_date_obj + timedelta(days=(unit.order - 1) * 7)
                date_1_str = date_1.strftime('%Y-%m-%d')
                unit_time_data = f"{date_1_str} {class_instance.end_time}"

            unit_time_data_obj = datetime.strptime(unit_time_data, '%Y-%m-%d %H:%M:%S')

            is_late = False
            exam_record = StudentExamRecord.objects.filter(user=student, exam=unit).first()
            if exam_record:
                finished_at = exam_record.finished_at
                if finished_at and finished_at > unit_time_data_obj:
                    is_late = True

                page_records = []
                page_record = StudentPageRecord.objects.filter(student_exam_record=exam_record)
                exam_initial_score = 0

                for record in page_record:
                    # 更新页面原始总分
                    update_page_score(record)

                    page_final_score = record.page_score * record.late_score
                    page_final_score = page_final_score.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                    exam_initial_score += page_final_score
                    exam_initial_score = exam_initial_score.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                    page_records.append({"page_record":record, "page_final_score":page_final_score})

                # 更新试卷总分
                update_exam_score(exam_record)
                # exam_final_score = exam_record.score
                assignments_data.append({
                    'unit': unit,
                    'unit_time_data': unit_time_data, # 截止时间
                    'week': week,   # quiz的开放周次
                    'is_late': is_late,   # 是否逾期完成
                    'exam_record': exam_record,
                    'page_records': page_records,
                    'exam_initial_score': exam_initial_score,
                    # 'exam_final_score': exam_final_score
                })

    # 分页，设置每页显示10条记录
    paginator = Paginator(assignments_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'learning/assignment_unit.html', {
        'student': student,
        'assignments_data': page_obj,
        'categories': categories,
        'now': now,
        })


def unit_detail(request, unit_id, student_id, unit_time_data):
    """ 学生各单元答题情况 """
    # 获取学生
    student = get_object_or_404(Students, id=student_id)

    # 获取指定的单元信息
    unit = get_object_or_404(Unit, id=unit_id)
    unit_time_data = unit_time_data
    unit_time_data_obj = datetime.strptime(unit_time_data, '%Y-%m-%d %H:%M:%S')


    # 获取学生行为数据
    exam_record = StudentExamRecord.objects.filter(exam=unit, user=student).first()
    page_record = StudentPageRecord.objects.filter(student_exam_record=exam_record)
    media_record = StudentMediaPlayRecord.objects.filter(student_exam_record=exam_record)
    page_records = []
    for record in page_record:
        submitted_at = record.submitted_at
        is_late = False
        if submitted_at and submitted_at > unit_time_data_obj:
            is_late = True
        page_records.append({"page": record.page.order+1, "record": record, "is_late": is_late})

    # 获取该单元的所有页面、题目、答案等
    question_data = []
    pages = PaperPage.objects.filter(unit=unit)  # 获取该单元的所有页面

    for page in pages:
        # 获取当前页面的所有大题
        page_main_questions = PageMainQuestion.objects.filter(page=page)

        main_questions = []

        for page_main_question in page_main_questions:
            # 获取当前大题的所有小题
            page_sub_questions = PageSubQuestion.objects.filter(page_main_question=page_main_question)

            subquestions = []

            for idx, page_sub_question in enumerate(page_sub_questions):
                sub_question = page_sub_question.sub_question

                corrections = Correction.objects.filter(sub_question=sub_question)
                corrected_text = apply_corrections(sub_question, corrections)
                blank = Blank.objects.filter(sub_question=sub_question)
                blank_text = apply_blanks(sub_question, blank, idx)
                student_answers = StudentAnswer.objects.filter(sub_question=sub_question, student_page_record__in=page_record)

                subquestions.append({
                    'sub_question': sub_question,
                    'corrections': corrections,
                    'corrected_text': corrected_text,
                    'blank_text': blank_text,
                    'student_answers': student_answers
                })

            # 将大题及其小题数据添加到 main_questions 列表中
            main_questions.append({
                'main_question': page_main_question.main_question,
                'sub_questions': subquestions
            })

        # 将页面及其大题数据添加到 question_data 列表中
        question_data.append({
            'page': page,
            'main_questions': main_questions
        })

    context = {
        'student': student,
        'unit': unit,
        'unit_time_data': unit_time_data,
        'pages': pages,
        'question_data': question_data,
        'exam_record': exam_record,
        'page_record': page_records,
        'media_record': media_record
    }
    return render(request, 'learning/unit_detail.html', context)


def update_page_score(student_page_record):
    """ 更新页面总分（页面所有小题的得分之和） """
    total_score = 0
    student_answer_records = StudentAnswer.objects.filter(student_page_record=student_page_record)
    for record in student_answer_records:
        total_score += record.score
    student_page_record.page_score = total_score
    student_page_record.save()


def update_exam_score(student_exam_record):
    """ 更新试卷总分（各页面分数 * 逾期分），并根据诚信分调整总分 """
    try:
        total_score = 0

        student_page_records = StudentPageRecord.objects.filter(student_exam_record=student_exam_record)
        for record in student_page_records:
            total_score += record.page_score * record.late_score  # 页面分数 * 逾期分
            print("page_score", record.page_score)
            print("late:", record.late_score)
            print("total score:", total_score)

        final_score = total_score * Decimal(student_exam_record.integrity_score)
        # 保留小数点后两位，四舍五入
        final_score = final_score.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        print("final_score:", final_score)
        student_exam_record.score = final_score
        student_exam_record.save()
    except Exception as e:
        print("Exception occurred in update_exam_score:", e)
        raise





@csrf_exempt
def update_question_score(request):
    """ 修改单个学生的小题得分 """
    if request.method == "POST":
        # 解析请求中的数据
        data = json.loads(request.body)
        record_id = data.get('record_id')
        question_score = data.get('question_score')

        # 查找相应的练习答案记录并更新
        try:
            record = StudentAnswer.objects.get(id=record_id)
            record.score = question_score
            record.save()
            # 更新页面分数
            update_page_score(record.student_page_record)
            # 更新试卷总分
            update_exam_score(record.student_page_record.student_exam_record)
            return JsonResponse({"success": True})
        except StudentAnswer.DoesNotExist:
            return JsonResponse({"success": False, "message": "答案记录未找到"})
    return JsonResponse({"success": False, "message": "无效请求"})


@csrf_exempt
def update_late_score(request):
    """ 单一修改页面逾期分 """
    if request.method == "POST":
        # 解析请求中的数据
        data = json.loads(request.body)
        record_id = data.get('record_id')
        late_score = data.get('late_score')

        try:
            late_score = float(late_score)
            if late_score < 0 or late_score > 1:
                return JsonResponse({"success": False, "message": "逾期分必须介于0和1之间"})

        except (ValueError, TypeError):
            return JsonResponse({"success": False, "message": "无效的逾期分值"})

        # 查找相应的学习记录并更新
        try:
            record = StudentPageRecord.objects.get(id=record_id)
            record.late_score = late_score
            record.save()
            # 更新页面分数
            update_page_score(record)
            # 更新试卷总分
            update_exam_score(record.student_exam_record)
            return JsonResponse({"success": True})
        except StudentPageRecord.DoesNotExist:
            return JsonResponse({"success": False, "message": "页面学习记录未找到"})
    return JsonResponse({"success": False, "message": "无效请求"})


@csrf_exempt
def batch_update_late_scores(request):
    """ 统一修改页面逾期分 """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            unit_id = data.get('unit_id')
            late_score = data.get('late_score')
            class_id = data.get('class_id')

            unit = Unit.objects.get(id=unit_id)
            class_instance = Class.objects.get(id=class_id)
            students = Students.objects.filter(class_instance=class_instance)
            exam_records = StudentExamRecord.objects.filter(exam=unit, user__in=students)

            page_records = StudentPageRecord.objects.filter(
                student_exam_record__in=exam_records
            )

            # 更新每个学生的逾期分
            for record in page_records:
                record.late_score = late_score
                record.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid method'})


@csrf_exempt
def update_integrity_score(request):
    """ 修改单元诚信分 """
    if request.method == "POST":
        # 解析请求中的数据
        data = json.loads(request.body)
        record_id = data.get('record_id')
        integrity_score = data.get('integrity_score')

        try:
            integrity_score = float(integrity_score)
            if integrity_score < 0 or integrity_score > 1:
                return JsonResponse({"success": False, "message": "诚信分必须介于0和1之间"})

        except (ValueError, TypeError):
            return JsonResponse({"success": False, "message": "无效的诚信分值"})

        # 查找相应的学习记录并更新
        try:
            record = StudentExamRecord.objects.get(id=record_id)
            record.integrity_score = integrity_score
            record.save()

            # 更新试卷总分
            update_exam_score(record)
            return JsonResponse({"success": True})
        except StudentPageRecord.DoesNotExist:
            return JsonResponse({"success": False, "message": "单元学习记录未找到"})
    return JsonResponse({"success": False, "message": "无效请求"})



def delete_answer_records(request, unit_id, student_id, unit_time_data):
    """ 删除学生小题作答记录 """
    if request.method == 'POST':
        selected_records = request.POST.getlist('selected_answer_records')  # 获取选中的记录ID

        try:
            if selected_records:
                StudentAnswer.objects.filter(id__in=selected_records).delete()
                messages.success(request, "选中的小题作答记录已成功删除")
            else:
                messages.warning(request, "未选择小题作答记录")

        except Exception as e:
            messages.error(request, f"没有该小题的答题数据")

        return redirect(request.path)

    return unit_detail(request, unit_id, student_id, unit_time_data)


def delete_media_records(request, unit_id, student_id, unit_time_data):
    """ 删除学生媒体播放记录 """
    if request.method == 'POST':
        selected_records = request.POST.getlist('selected_media_records')  # 获取选中的记录ID

        try:
            if selected_records:
                StudentMediaPlayRecord.objects.filter(id__in=selected_records).delete()
                messages.success(request, "选中的媒体播放记录已成功删除")
            else:
                messages.warning(request, "未选择媒体播放记录")

        except Exception as e:
            messages.error(request, f"没有媒体播放数据")

        return redirect(request.path)

    return unit_detail(request, unit_id, student_id, unit_time_data)




# -------------------------------- 数据统计分析 --------------------------------
def class_statistic_search(request):
    """ 查询班级 """
    if not request.session.get('is_login', None):
        return redirect('login')  # 如果用户未登录，重定向到登录页面

    username = request.session.get('username', None)
    teacher_instance = Teachers.objects.get(username=username)
    class_instances = Class.objects.filter(teacher=teacher_instance)

    # 获取班号，如果有输入则进行过滤
    class_name = request.GET.get('class_name', '')

    if class_name:
        class_instances = class_instances.filter(class_name__icontains=class_name)

    # 分页，设置每页显示5条记录
    paginator = Paginator(class_instances, 10)
    page_number = request.GET.get('page')  # 获取当前页码

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'statistic/class_statistic_search.html', {
        'class_instances': page_obj,
        'class_name': class_name
    })


def class_unit(request, class_id):
    class_instance = Class.objects.get(id=class_id)
    students = Students.objects.filter(class_instance=class_instance)
    units = Unit.objects.filter(class_instance=class_instance)
    units_data = []
    categories = dict(Unit.TYPES)

    # 定义成绩区间
    score_ranges = [(0, 59), (60, 69), (70, 79), (80, 89), (90, 100)]

    if units:
        for unit in units:
            week = 0
            if unit.type == "exam":
                time = TimeManagement.objects.filter(unit=unit).first()
                unit_time_data = f"{time.exam_date} {time.end_time}"
            elif unit.type == "quiz":
                # 解析开课日期
                start_date_obj = datetime.strptime(class_instance.start_date, '%Y-%m-%d')
                week = TimeManagement.objects.filter(unit=unit).first().week
                # 计算日期范围
                date_1 = start_date_obj + timedelta(days=(week - 1) * 7)
                date_1_str = date_1.strftime('%Y-%m-%d')
                unit_time_data = f"{date_1_str} {class_instance.end_time}"
            elif unit.type == "task":
                # 解析开课日期
                start_date_obj = datetime.strptime(class_instance.start_date, '%Y-%m-%d')
                # 计算日期范围
                date_2 = start_date_obj + timedelta(days=unit.order * 7)
                date_2_str = date_2.strftime('%Y-%m-%d')
                unit_time_data = f"{date_2_str} {class_instance.start_time}"
            else:
                # 解析开课日期
                start_date_obj = datetime.strptime(class_instance.start_date, '%Y-%m-%d')
                # 计算日期范围
                date_1 = start_date_obj + timedelta(days=(unit.order - 1) * 7)
                date_1_str = date_1.strftime('%Y-%m-%d')
                unit_time_data = f"{date_1_str} {class_instance.end_time}"

            # 获取当前单元的成绩记录
            unit_records = StudentExamRecord.objects.filter(user__in=students, exam=unit)
            # 获取该单元的所有页面
            pages = PaperPage.objects.filter(unit=unit)

            score_statistic = []

            page_highest_scores = {} # 计算每个页面的最高分
            highest_unit_score = 0 # 每个单元的最高分
            if unit_records:

                for record in unit_records:
                    update_exam_score(record)
                    page_score = []
                    for page in pages:
                        page_record = StudentPageRecord.objects.filter(student_exam_record=record, page=page).first()
                        page_score.append({
                            'page': page, 'page_record': page_record
                        })
                        # 更新每个页面的最高分
                        if page_record and (
                                page not in page_highest_scores or page_record.page_score > page_highest_scores[
                            page]):
                            page_highest_scores[page] = page_record.page_score

                    score_statistic.append({
                        'user': record.user,
                        'page_score': page_score,
                        'unit_score': record.score
                    })
                print("page_highest_scores:", page_highest_scores)
                # 计算总成绩的最高分
                highest_unit_score = max(record.score for record in unit_records)


            # 统计当前单元的成绩分布
            distribution = defaultdict(int)
            if unit_records.exists():
                for record in unit_records:
                    score = record.score
                    if score is None:
                        distribution["无成绩"] += 1
                    else:
                        for lower, upper in score_ranges:
                            if lower <= score <= upper:
                                distribution[f"{lower}-{upper}"] += 1
                                break
            else:
                # 如果没有成绩记录，初始化分布为 0
                for lower, upper in score_ranges:
                    distribution[f"{lower}-{upper}"] = 0

            # 对 labels 和 data 进行排序
            def sort_key(label):
                if label == "无成绩":
                    return float('inf')  # 将 "无成绩" 放在最后
                else:
                    return int(label.split('-')[0])  # 按区间下限排序

            sorted_labels = sorted(distribution.keys(), key=sort_key)
            sorted_data = [distribution[label] for label in sorted_labels]

            # 统计完成人数和未完成作业的学生信息
            completed_students = set(unit_records.values_list('user', flat=True))
            total_students = set(students.values_list('id', flat=True))
            uncompleted_students = total_students - completed_students

            # 获取未完成作业的学生信息
            uncompleted_students_info = Students.objects.filter(id__in=uncompleted_students)
            uncompleted_students_json = serializers.serialize('json', uncompleted_students_info)


            # 将统计结果添加到单元数据中
            units_data.append({
                'unit': unit,
                'week': week,
                'unit_time_data': unit_time_data,
                'unit_record': unit_records,
                'score_distribution': {
                    'labels': sorted_labels,
                    'data': sorted_data,
                },
                'score_statistic': score_statistic,
                'page_highest_scores': page_highest_scores,
                'highest_unit_score': highest_unit_score,
                'completed_count': len(completed_students),
                'total_count': len(total_students),
                'uncompleted_students_info': uncompleted_students_info,
                'uncompleted_students_json': uncompleted_students_json,
            })

    # 分页，设置每页显示10条记录
    paginator = Paginator(units_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'statistic/class_unit.html', {
        'class_instance': class_instance,
        'units_data': page_obj,
        'categories': categories,
        'score_ranges': score_ranges,
    })


def statistic_announce(request, class_id):
    class_instance = Class.objects.get(id=class_id)
    students_data = request.GET.get('students')
    if students_data:
        try:
            students_list = json.loads(students_data)  # 将 JSON 字符串解析为 Python 对象
            students = []

            for student_data in students_list:
                student_instance = Students.objects.get(pk=student_data['pk'])
                students.append(student_instance)

        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON format")
        except Students.DoesNotExist:
            return HttpResponseBadRequest("Student not found in database")
    else:
        students = []
    print("Class:", class_instance)
    print("students", students)
    username = request.session.get('username')
    role = request.session.get('role', 'none')
    if role != 'teacher':
        return JsonResponse({'error': '只有教师可以管理公告'}, status=403)

    if request.method == 'POST':
        p_type = request.POST.get('type')
        if p_type == 'delete':
            a_id = request.POST.get('a_id')
            Announcement.objects.filter(id=a_id).delete()
            return JsonResponse({'success': '公告已删除'}, status=200)
        elif p_type == 'create':
            form = AnnouncementForm(request.POST)
            if form.is_valid():
                receivers = form.cleaned_data['receivers']
                select_all = form.cleaned_data.get('select_all', False)

                if not receivers and not select_all:
                    return JsonResponse({'error': '必须选择接收者或全选'}, status=400)

                a_title = form.cleaned_data['a_title']
                a_content = form.cleaned_data['a_content']
                announcement = form.save(commit=False)
                announcement.teachers = Teachers.objects.get(username=username)
                announcement.save()

                if select_all:
                    receivers = Students.objects.all()
                announcement.receivers.set(receivers)

                for receiver in receivers:
                    Message.objects.create(
                        sender=username,
                        receiver=receiver.username,
                        content=a_content,
                        is_announcement=True,
                        announcement_id=announcement.id
                    )
                    async_to_sync(get_channel_layer().group_send)(
                        f'user_{receiver.username}',
                        {
                            'type': 'notification_message',
                            'message': f"New announcement: {a_title}",
                            'announcement_id': announcement.id
                        }
                    )
                return JsonResponse({'success': '公告已发布'}, status=200)
            else:
                # 返回具体的表单错误信息
                return JsonResponse({'error': form.errors.as_json()}, status=400)


    elif request.method == 'GET':
        form = AnnouncementForm()
        announcements = Announcement.objects.all().order_by('-created_at').prefetch_related('receivers')
        paginator = Paginator(announcements, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # 按班级分组学生
        students_by_class = defaultdict(list)
        for student in students:
            students_by_class[class_instance].append(student)

        return render(request, 'announce/announcements.html', {
            'form': form,
            'page_obj': page_obj,
            'students_by_class': students_by_class.items()
        })



def apply_corrections(sub_question, corrections):
    """
    根据 correction 的类型和位置，在题目文段中添加标志。
    """
    text = sub_question.question_text
    words = text.split()

    # 对每个 correction 进行处理
    for correction in corrections:
        index = correction.index
        if 0 <= index < len(words):
            word = words[index]
            if correction.type == 'revise':
                # 在单词下方添加下划线
                words[index] = f'<u>{word}</u>'
            elif correction.type == 'delete':
                # 在单词上方添加斜杠
                words[index] = f'<span style="text-decoration: line-through;">{word}</span>'
            elif correction.type == 'insert':
                # 在单词右侧添加插入符号
                words[index] = f'{word}<sup>^</sup>'

    # 将处理后的单词重新组合为文本
    return mark_safe(' '.join(words))


def apply_blanks(sub_question, blanks, idx):
    """
    根据 blank 的位置，在题目文段中添加下划线
    """
    text = sub_question.question_text
    words = text.split()

    for blank in blanks:
        index = blank.index
        if 0 <= index < len(words):
            word = words[index]
            words[index] = f'{word}______<span style="font-size: smaller; margin-left: 2px; color: #ea5e5a">[{idx+1}]</span>'

    return mark_safe(' '.join(words))


def statistic_apply_blanks(sub_question, blanks, correct_rate_percentage, idx):
    """
    根据 blank 的位置，在题目文段中添加答对率和答案
    """
    text = sub_question.question_text
    answer = sub_question.answer
    words = text.split()

    for blank in blanks:
        index = blank.index
        if 0 <= index < len(words):
            word = words[index]
            words[index] = f'{word}<span id="blank_correct_rate{sub_question.id}" class="blank_correct_rate" style="color: #007bff; margin-left: 7px;"><u>{correct_rate_percentage}%</u></span><span style="color: green; margin-right: 9px;"><u>{answer}</u></span><span style="font-size: smaller; margin-left: 2px; color: #ea5e5a">[{idx+1}]</span>'

    return mark_safe(' '.join(words))


def unit_statistic(request, unit_id, class_id):
    # 获取班级和学生
    class_instance = get_object_or_404(Class, id=class_id)
    students = Students.objects.filter(class_instance=class_instance)
    # 获取指定的单元信息
    unit = get_object_or_404(Unit, id=unit_id)


    # 获取该单元的所有页面、题目、答案等
    question_data = []
    pages = PaperPage.objects.filter(unit=unit)  # 获取该单元的所有页面

    for page in pages:
        # 获取当前页面的所有大题
        page_main_questions = PageMainQuestion.objects.filter(page=page)

        main_questions = []

        for page_main_question in page_main_questions:
            main_question = page_main_question.main_question
            if main_question.image_url:
                main_images = main_question.image_url.split(',')
            else:
                main_images = None

            # 获取当前大题的所有小题
            page_sub_questions = PageSubQuestion.objects.filter(page_main_question=page_main_question)

            subquestions = []

            for idx, page_sub_question in enumerate(page_sub_questions):
                sub_question = page_sub_question.sub_question
                if sub_question.image_url:
                    sub_images = sub_question.image_url.split(',')
                else:
                    sub_images = None
                max_score = sub_question.score

                choices_data = []
                choices = ChoiceOption.objects.filter(sub_question=sub_question)
                if choices:
                    for choice in choices:
                        if choice.image_url:
                            choices_data.append({"choice": choice, "choice_images": choice.image_url.split(',')})
                        else:
                            choices_data.append({"choice": choice, "choice_images": None})

                corrections = Correction.objects.filter(sub_question=sub_question)
                matching = MatchingOption.objects.filter(sub_question=sub_question).first()
                if matching and matching.image_url:
                    matching_images = matching.image_url.split(',')
                else:
                    matching_images = []

                corrected_text = apply_corrections(sub_question, corrections)



                # 筛选出所有学生的答题记录
                student_page_records = StudentPageRecord.objects.filter(
                    student_exam_record__user__in=students,
                    page__unit=unit,
                    page__in=pages,
                )

                # 筛选出每个学生对应的小题作答数据
                student_records = StudentAnswer.objects.filter(
                    sub_question=sub_question,
                    student_page_record__in=student_page_records
                )
                student_answers = []
                for record in student_records:
                    student_answers.append(record.text)

                # 得分大于分值的 70% 视为答对(针对简答题）
                passing_score = max_score * 0.7
                # 统计答题人数
                total_answered = student_records.count()
                # 统计答对人数
                total_correct = student_records.filter(score__gt=passing_score).count()
                # 计算答对率
                correct_rate_percentage = round(total_correct / total_answered * 100) if total_answered > 0 else 0

                # 统计答案出现次数
                answer_counts = Counter(student_answers)
                # 计算每个答案的比例
                answer_statistics = []
                for answer, count in answer_counts.items():
                    percentage = (count / total_answered) * 100
                    answer_statistics.append({
                        'answer': answer,
                        'count': count,
                        'percentage': round(percentage, 2)
                    })

                blank = Blank.objects.filter(sub_question=sub_question)
                blank_text = statistic_apply_blanks(sub_question, blank, correct_rate_percentage, idx)

                subquestions.append({
                    'sub_question': sub_question,
                    'sub_images': sub_images,
                    'choices': choices_data,
                    'corrections': corrections,
                    'matching': matching,
                    'matching_images': matching_images,
                    'corrected_text': corrected_text,
                    'blank_text': blank_text,
                    'total_answered': total_answered,
                    'total_correct': total_correct,
                    'correct_rate_percentage': correct_rate_percentage,
                    'student_answers': answer_statistics,
                })

            # 将大题及其小题数据添加到 main_questions 列表中
            main_questions.append({
                'main_question': page_main_question.main_question,
                'main_images': main_images,
                'sub_questions': subquestions
            })

        # 将页面及其大题数据添加到 question_data 列表中
        question_data.append({
            'page': page,
            'main_questions': main_questions
        })

    context = {
        'class_instance': class_instance,
        'unit': unit,
        'pages': pages,
        'question_data': question_data,
    }
    return render(request, 'statistic/unit_statistic.html', context)






# -------------------------------- 逾期扣分规则 --------------------------------
class OverdueRuleListView(ListView):
    """ 逾期扣分规则列表 """
    model = OverdueDeductionRule
    template_name = 'overdue_rules/overdue_rules_lists.html'
    context_object_name = 'rules'

def overdue_rule_detail(request, pk):
    """ 查看详细扣分规则 """
    rule = get_object_or_404(OverdueDeductionRule, pk=pk)
    return render(request, 'overdue_rules/overdue_rule_detail.html', {'rule': rule})


def overdue_rule_create(request):
    """ 创建新扣分规则 """
    if request.method == 'POST':
        print("POST data:", request.POST)
        form = OverdueRuleForm(request.POST)
        formset = OverduePeriodFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            rule = form.save(commit=False)
            # 确保用户不能创建默认规则
            rule.is_default = False
            rule.save()
            formset.instance = rule
            formset.save()
            return redirect('Query:overdue_rules_lists')
    else:
        # 复制默认规则
        if 'copy_default' in request.GET:
            default_rule = OverdueDeductionRule.objects.filter(is_default=True).first()
            if default_rule:
                initial_data = {
                    'rule_name': f"{default_rule.rule_name} (副本)",
                    'description': default_rule.description
                }
                form = OverdueRuleForm(initial=initial_data)

                periods = default_rule.periods.all()
                # 临时创建一个新的 FormSet
                PeriodFormSet = forms.inlineformset_factory(
                    OverdueDeductionRule,
                    OverduePeriod,
                    form=OverduePeriodForm,
                    extra=len(periods),
                    can_delete=True
                )

                # 准备初始数据
                initial_periods = []
                for period in periods:
                    initial_periods.append({
                        'period_name': period.period_name,
                        'min_days': period.min_days,
                        'max_days': period.max_days,
                        'deduction_rate': period.deduction_rate,
                        'description': period.description
                    })

                # 使用initial初始化formset
                formset = PeriodFormSet(initial=initial_periods)

                print("formset:", formset)
                messages.info(request, "已从默认规则复制")
                return render(request, 'overdue_rules/overdue_rule_create.html', {
                    'form': form,
                    'formset': formset,
                    'has_default_rule': OverdueDeductionRule.objects.filter(is_default=True).exists()
                })
        form = OverdueRuleForm()
        formset = OverduePeriodFormSet()

    return render(request, 'overdue_rules/overdue_rule_create.html', {
        'form': form,
        'formset': formset,
        'has_default_rule': OverdueDeductionRule.objects.filter(is_default=True).exists()
    })


def overdue_rule_update(request, pk):
    """ 编辑逾期扣分规则 """
    rule = get_object_or_404(OverdueDeductionRule, pk=pk)

    if request.method == 'POST':
        form = OverdueRuleForm(request.POST, instance=rule)
        formset = OverduePeriodFormSet(request.POST, instance=rule)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('Query:overdue_rules_lists')
    else:
        form = OverdueRuleForm(instance=rule)
        formset = OverduePeriodFormSet(instance=rule)

    return render(request, 'overdue_rules/overdue_rule_update.html', {
        'form': form,
        'formset': formset,
        'rule': rule,
    })


@require_POST
def overdue_rule_batch_delete(request):
    rule_ids = request.POST.getlist('rule_ids')
    if not rule_ids:
        messages.error(request, "请选择要删除的规则")
        return redirect('Query:overdue_rules_lists')

    try:
        rules_to_delete = OverdueDeductionRule.objects.filter(pk__in=rule_ids)
        rule_count = rules_to_delete.count()

        rules_to_delete.delete()
        messages.success(request, f"成功删除 {rule_count} 条规则")
    except Exception as e:
        messages.error(request, f"删除失败: {str(e)}")

    return redirect('Query:overdue_rules_lists')