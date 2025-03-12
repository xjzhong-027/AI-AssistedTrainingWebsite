import openpyxl
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from Account.models import Admins, Teachers, Students, Class, Course, Attendance
from .forms import ClassForm



class Admin_list(admin.ModelAdmin):
    # 要展示的内容
    list_display = ['username', 'password']
    search_fields = ('username',)
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        # 如果修改了账号信息（change == True）
        if change:
            try:
                user = obj.user  # 通过外键关系获取关联的 User 对象
                # 更新 User 的 username, password 字段
                if user.username != obj.username:
                    # 确保新的 username 唯一
                    if User.objects.filter(username=obj.username).exists():
                        raise ValueError("Username already exists. Please choose a different username.")
                    user.username = obj.username
                # 确保密码更新时加密处理
                if user.password != obj.password:
                    user.password = make_password(obj.password)
                user.save()
            except User.DoesNotExist:
                pass  # 如果没有找到对应的 User，则不做任何操作


        # 如果是新建（change == False）
        else:
            user = User.objects.create_user(
                username=obj.username,
                password=obj.password,
            )
            # 确保 User 被添加到 '管理员' 组
            group, created = Group.objects.get_or_create(name='管理员')
            user.groups.add(group)
            user.save()
            obj.user = user  # 将创建的 User 关联到 Admin 对象
        # 保存 Admin 模型实例
        super().save_model(request, obj, form, change)


class Teacher_list(admin.ModelAdmin):
    # 要展示的内容
    list_display = ['name', 'username', 'password']
    search_fields = ('username', 'name',)
    readonly_fields = ('user',)

    def save_model(self, request, obj, form, change):
        # 如果修改了账号信息（change == True）
        if change:
            try:
                user = obj.user  # 通过外键关系获取关联的 User 对象
                # 更新 User 的 username, password 字段
                if user.username != obj.username:
                    # 确保新的 username 唯一
                    if User.objects.filter(username=obj.username).exists():
                        raise ValueError("Username already exists. Please choose a different username.")
                    user.username = obj.username
                # 确保密码更新时加密处理
                if user.password != obj.password:
                    user.password = make_password(obj.password)
                user.save()
            except User.DoesNotExist:
                pass  # 如果没有找到对应的 User，则不做任何操作


        # 如果是新建（change == False）
        else:
            user = User.objects.create_user(
                username=obj.username,
                password=obj.password,
            )
            # 确保 User 被添加到 '教师' 组
            group, created = Group.objects.get_or_create(name='教师')
            user.groups.add(group)
            user.save()
            obj.user = user  # 将创建的 User 关联到 Teacher 对象
        # 保存 Teacher 模型实例
        super().save_model(request, obj, form, change)



class Student_list(admin.ModelAdmin):
    # 要展示的内容
    list_display = ['username', 'name', 'class_instance', 'password']
    list_filter = ('class_instance', 'class_instance__course__grade')
    search_fields = ('username', 'name', 'class_instance__class_name')
    readonly_fields = ('user',)
    list_per_page = 10

    actions = ['export_xlsx']

    # 设定自定义模板
    change_list_template = "admin/student_change_list.html"

    # 自定义URL处理CSV文件上传
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.import_students_view, name='import_students')
        ]
        return custom_urls + urls

    def import_students_view(self, request):
        if request.method == "POST" and request.FILES["xlsx_file"]:
            file = request.FILES["xlsx_file"]

            try:
                # 打开 Excel 文件
                wb = openpyxl.load_workbook(file)
                sheet = wb.active  # 获取当前活动的工作表
            except Exception as e:
                return HttpResponse(f"Error opening file: {e}")

            # 读取每一行数据，跳过表头
            for row in sheet.iter_rows(min_row=2, values_only=True):  # 从第二行开始读取
                student_username = row[0]
                student_name = row[1]
                teacher_username = row[2]
                year = row[3]
                grade = row[4]
                semester = row[5]
                class_name = row[6]
                start_date = row[7]
                week = row[8]
                start_time = row[9]
                end_time = row[10]

                # 创建/获取教师
                teacher_user, created = User.objects.get_or_create(username=teacher_username)
                # 确保被添加到 '教师' 组
                group, created = Group.objects.get_or_create(name='教师')
                teacher_user.groups.add(group)
                teacher_user.save()

                teacher, created = Teachers.objects.get_or_create(
                    name=teacher_username,
                    username=teacher_username,
                    user=teacher_user
                )

                # 创建课程
                course, created = Course.objects.get_or_create(
                    year=year,
                    grade=grade,
                    semester=semester
                )

                # 创建班级
                course_class, created = Class.objects.get_or_create(
                    class_name=class_name,
                    course=course,
                    teacher=teacher,
                    start_date=start_date,
                    week=week,
                    start_time=start_time,
                    end_time=end_time
                )

                # 创建/获取学生
                student_user, created = User.objects.get_or_create(username=student_username)
                # 确保被添加到 '学生' 组
                group, created = Group.objects.get_or_create(name='学生')
                student_user.groups.add(group)
                student_user.save()

                student, created = Students.objects.get_or_create(
                    username=student_username,
                    name=student_name,
                    password=student_username,
                    class_instance=course_class,
                    user=student_user
                )
                # 检查该学生是否已经有考勤记录
                if not Attendance.objects.filter(student=student).exists():
                    # 如果没有考勤记录，创建1-16周的考勤记录
                    with transaction.atomic():  # 使用事务，确保数据一致性
                        for week in range(1, 17):  # 1到16周
                            Attendance.objects.create(
                                student=student,
                                week=week,
                                status='absent',
                            )

            self.message_user(request, "学生数据导入成功！")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return render(request, 'admin/import_students.html', {})


    def export_xlsx(self, request, queryset):
        """
        导出 Excel 格式的文件
        """
        # 使用 select_related 预加载关联的 Class 对象
        queryset = queryset.select_related('student_class')

        # 创建一个新的工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Student_username', 'Class', 'Name', 'Password'])  # 添加表头

        # 写入数据
        for obj in queryset:
            ws.append([obj.username, obj.class_instance.class_name, obj.name, obj.password])

        # 设置响应头，定义文件类型为 Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'

        # 保存工作簿到响应
        wb.save(response)
        return response
    export_xlsx.short_description = "导出为Excel"

    def save_model(self, request, obj, form, change):
        # 如果修改了账号信息（change == True）
        if change:
            try:
                user = obj.user  # 通过外键关系获取关联的 User 对象
                # 更新 User 的 username, password 字段
                if user.username != obj.username:
                    # 确保新的 username 唯一
                    if User.objects.filter(username=obj.username).exists():
                        raise ValueError("Username already exists. Please choose a different username.")
                    user.username = obj.username
                # 确保密码更新时加密处理
                if user.password != obj.password:
                    user.password = make_password(obj.password)
                user.save()
            except User.DoesNotExist:
                pass  # 如果没有找到对应的 User，则不做任何操作


        # 如果是新建（change == False）
        else:
            user = User.objects.create_user(
                username=obj.username,
                password=obj.password,
            )
            # 确保 User 被添加到 '学生' 组
            group, created = Group.objects.get_or_create(name='学生')
            user.groups.add(group)
            user.save()
            obj.user = user  # 将创建的 User 关联到 Student 对象
            # 保存 Student 对象，确保已保存到数据库
            obj.save()

            # 自动为该学生创建1-16周的考勤记录
            with transaction.atomic():  # 使用事务处理，确保所有操作成功
                for week in range(1, 17):  # 1到16周
                    Attendance.objects.create(
                        student=obj,
                        week=week,
                        status='absent',  # 默认考勤状态为 '缺勤'
                    )
        # 保存 Student 模型实例
        super().save_model(request, obj, form, change)



class Class_list(admin.ModelAdmin):
    form = ClassForm
    # 要展示的内容
    list_display = ['class_name', 'course', 'start_date', 'week', 'start_time', 'end_time', 'teacher']
    list_filter = ('course__grade', 'teacher')
    search_fields = ('class_name', 'course__grade', 'week', 'start_time', 'teacher__name')
    list_per_page = 15

    actions = ['export_xlsx']

    def export_xlsx(self, request, queryset):
        """
        导出 Excel 格式的文件
        """
        # 使用 select_related 预加载关联的 Class 对象
        queryset = queryset.select_related('course')

        # 创建一个新的工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['开课年份', '年级', '开课学期', '班级', '授课老师','上课星期', '上课时间', '下课时间'])  # 添加表头

        # 写入数据
        for obj in queryset:
            ws.append([obj.course.year, obj.course.grade, obj.course.semester, obj.class_name, obj.teacher.name, obj.week, obj.start_time, obj.end_time])

        # 设置响应头，定义文件类型为 Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="classes.xlsx"'

        # 保存工作簿到响应
        wb.save(response)
        return response

    export_xlsx.short_description = "导出为Excel"


class Course_list(admin.ModelAdmin):
    # 要展示的内容
    list_display = ['year', 'grade', 'semester']
    list_filter = ('year', 'grade', 'semester')

class Attendance_list(admin.ModelAdmin):
    # 要展示的内容
    list_display = ['student', 'week', 'status', 'adjusted_class_time', 'added_class_time']
    list_filter = ('student__class_instance', 'week', 'status')
    list_per_page = 20


class CustomUserAdmin(UserAdmin):
    """ 所有账号 """
    def has_add_permission(self, request):
        return False  # 禁用新增用户按钮

    def has_change_permission(self, request, obj=None):
        return True  # 允许修改用户

    def has_delete_permission(self, request, obj=None):
        return False  # 不允许删除用户

    # 将 'username' 字段设置为只读
    readonly_fields = ('username',)






admin.site.register(Admins, Admin_list)
admin.site.register(Teachers, Teacher_list)
admin.site.register(Students, Student_list)
admin.site.register(Course, Course_list)
admin.site.register(Class, Class_list)
admin.site.register(Attendance, Attendance_list)

# 使用自定义的“所有账号”模块
admin.site.unregister(User) # 取消默认的注册
admin.site.register(User, CustomUserAdmin)


admin.site.site_header = "管理员端系统"
admin.site.site_title = '管理员端系统'