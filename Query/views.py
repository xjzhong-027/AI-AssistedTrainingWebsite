import json, pytz
from datetime import datetime

from django.contrib import messages
from django.http import JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from .models import ClassroomLayout
from Account.models import Class, Students, Teachers, Attendance, ClassScheduleAdjustment, ClassScheduleAddition
from ELW.models import Unit, TimeManagement, PaperPage, PageMainQuestion, PageSubQuestion, Correction, ChoiceOption, MatchingOption
from accessment.models import StudentExamRecord, StudentPageRecord, StudentAnswer, StudentMediaPlayRecord
from .forms import AttendanceQueryForm, ClassScheduleAdjustmentForm, ClassScheduleAdditionForm,  \
    ClassroomLayoutForm
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
            if unit.type == "exam" or unit.type == "quiz":
                unit_data = TimeManagement.objects.filter(unit=unit).first()
            else:
                unit_data = None
            record = StudentExamRecord.objects.filter(user=student, exam=unit).first()
            assignments_data.append({
                'unit': unit,
                'unit_data': unit_data,
                'record': record
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


def unit_detail(request, unit_id, student_id):
    """ 学生各单元答题情况 """
    # 获取学生
    student = get_object_or_404(Students, id=student_id)

    # 获取指定的单元信息
    unit = get_object_or_404(Unit, id=unit_id)

    # 获取学生行为数据
    exam_record = StudentExamRecord.objects.filter(exam=unit, user=student).first()
    page_record = StudentPageRecord.objects.filter(student_exam_record=exam_record)
    media_record = StudentMediaPlayRecord.objects.filter(student_exam_record=exam_record)


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

            for page_sub_question in page_sub_questions:
                sub_question = page_sub_question.sub_question

                corrections = Correction.objects.filter(sub_question=sub_question)
                corrected_text = apply_corrections(sub_question, corrections)
                student_answers = StudentAnswer.objects.filter(sub_question=sub_question, student_page_record__in=page_record)

                subquestions.append({
                    'sub_question': sub_question,
                    'corrections': corrections,
                    'corrected_text': corrected_text,
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
    # question_data=[]
    # pages = PaperPage.objects.filter(unit=unit) # 所有页面
    # page_main_questions = PageMainQuestion.objects.filter(page__in=pages)
    # page_sub_questions = PageSubQuestion.objects.filter(page_main_question__in=page_main_questions)
    #
    #
    # for page_main_question in page_main_questions:
    #     subquestions = []
    #     for page_sub_question in page_sub_questions:
    #         if page_sub_question.page_main_question == page_main_question:
    #             sub_question = page_sub_question.sub_question
    #             corrections = Correction.objects.filter(sub_question=sub_question)
    #             corrected_text = apply_corrections(sub_question, corrections)
    #             student_answers = StudentAnswer.objects.filter(sub_question=sub_question, student_page_record__in=page_record)
    #             subquestions.append({
    #                 'sub_question': sub_question,
    #                 'corrections': corrections,
    #                 'corrected_text': corrected_text,
    #                 'student_answers': student_answers
    #             })
    #     question_data.append({
    #         'main_question': page_main_question.main_question,
    #         'sub_questions': subquestions
    #     })

    context = {
        'student': student,
        'unit': unit,
        'pages': pages,
        'question_data': question_data,
        'exam_record': exam_record,
        'page_record': page_record,
        'media_record': media_record
    }
    return render(request, 'learning/unit_detail.html', context)


def update_page_score(student_page_record):
    """ 更新页面总分（所有小题的得分之和） """
    total_score = sum(answer.score for answer in student_page_record.answers.all())
    student_page_record.page_score = total_score
    student_page_record.save()


def update_exam_score(student_exam_record):
    """ 更新试卷总分（各页面分数 * 诚信分） """
    total_score = 0
    for page in student_exam_record.page_records.all():
        total_score += page.page_score * page.integrity_score  # 页面分数 * 诚信分
    student_exam_record.score = total_score
    student_exam_record.save()


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
def update_integrity_score(request):
    """ 修改页面诚信分 """
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
            record = StudentPageRecord.objects.get(id=record_id)
            record.integrity_score = integrity_score
            record.save()
            # 更新页面分数
            update_page_score(record)
            # 更新试卷总分
            update_exam_score(record.student_exam_record)
            return JsonResponse({"success": True})
        except StudentPageRecord.DoesNotExist:
            return JsonResponse({"success": False, "message": "页面学习记录未找到"})
    return JsonResponse({"success": False, "message": "无效请求"})



def delete_answer_records(request, unit_id, student_id):
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

    return unit_detail(request, unit_id, student_id)





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
    units = Unit.objects.filter(class_instance=class_instance)
    units_data = []
    categories = dict(Unit.TYPES)

    if units:
        for unit in units:
            if unit.type == "exam" or unit.type == "quiz":
                unit_data = TimeManagement.objects.filter(unit=unit).first()
            else:
                unit_data = None
            units_data.append({
                'unit': unit,
                'unit_data': unit_data,
            })

    # 分页，设置每页显示10条记录
    paginator = Paginator(units_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'statistic/class_unit.html',{
        'class_instance': class_instance,
        'units_data': page_obj,
        'categories': categories
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


def unit_statistic(request, unit_id, class_id):
    # 获取班级
    class_instance = get_object_or_404(Class, id=class_id)
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
            # 获取当前大题的所有小题
            page_sub_questions = PageSubQuestion.objects.filter(page_main_question=page_main_question)

            subquestions = []

            for page_sub_question in page_sub_questions:
                sub_question = page_sub_question.sub_question

                choices = ChoiceOption.objects.filter(sub_question=sub_question)
                corrections = Correction.objects.filter(sub_question=sub_question)
                matchings = MatchingOption.objects.filter(sub_question=sub_question)
                corrected_text = apply_corrections(sub_question, corrections)

                subquestions.append({
                    'sub_question': sub_question,
                    'choices': choices,
                    'corrections': corrections,
                    'matchings': matchings,
                    'corrected_text': corrected_text
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
        'class_instance': class_instance,
        'unit': unit,
        'pages': pages,
        'question_data': question_data,
    }
    return render(request, 'statistic/unit_statistic.html', context)






