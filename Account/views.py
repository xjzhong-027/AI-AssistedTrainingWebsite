"""
Account views for authentication and user management.
"""
import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from Account.models import Students, Teachers, Class, Attendance, LoginInfo, Admins
from Account.services.auth_service_impl import AuthServiceImpl
from Account.services.user_service_impl import UserServiceImpl


# 登录板块
def user_login(request):
    """用户登录视图"""
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        role = request.POST['role']
        username = request.POST['username']
        password = request.POST['password']
        # 初始化最后活跃时间（在认证成功后通过 AuthService 更新）
        request.session['last_active_time'] = datetime.datetime.now().isoformat()
        
        # 验证学生登录
        if role == 'student':
            # 使用 AuthService 进行认证
            auth_result = AuthServiceImpl.authenticate_student(username, password)
            if auth_result:
                student_instance = auth_result['student']
                student_user = auth_result['user']
                
                # 写入session
                request.session['role'] = 'student'
                request.session['username'] = username
                request.session['is_login'] = True
                print(f'{username}: Login.')

                # 使用 AuthService 创建登录记录
                AuthServiceImpl.create_login_record(username, 'student', request)
                
                # Django 用户登录
                if student_user is not None:
                    login(request, student_user)

                class_instance = UserServiceImpl.get_class_by_id(student_instance.class_instance_id)
                if not class_instance:
                    return render(request, 'login.html', {
                        'error_message': 'Class not found！',
                    })
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
                    print(week)
                    # 使用 try-except 处理 Attendance 不存在的情况
                    try:
                        attendance_record = Attendance.objects.get(week=week, student_id=student_instance.id)
                        status = attendance_record.status
                    except Attendance.DoesNotExist:
                        # 如果考勤记录不存在，跳过考勤逻辑
                        status = None
                        print(f'Attendance record for week {week} not found, skipping attendance check')
                    
                    if status is not None:
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

                return redirect('student_ELW:student_index')
        
        # 验证教师登录
        if role == 'teacher':
            # 使用 AuthService 进行认证
            auth_result = AuthServiceImpl.authenticate_teacher(username, password)
            if auth_result:
                teacher_instance = auth_result['teacher']
                teacher_user = auth_result['user']
                
                request.session['role'] = 'teacher'
                request.session['username'] = username
                request.session['is_login'] = True
                request.session['teacher_name'] = teacher_instance.name
                
                # 使用 AuthService 创建登录记录
                AuthServiceImpl.create_login_record(username, 'teacher', request)
                
                # Django 用户登录
                if teacher_user is not None:
                    login(request, teacher_user)
                return redirect('teacher_index')
        
        # 验证管理员登录
        if role == 'admin':
            # 使用 AuthService 进行认证
            auth_result = AuthServiceImpl.authenticate_admin(username, password)
            if auth_result:
                request.session['role'] = 'admin'
                request.session['username'] = username
                request.session['is_login'] = True
                
                # 使用 AuthService 创建登录记录
                AuthServiceImpl.create_login_record(username, 'admin', request)
                
                return redirect('/admin/')
        
        return render(request, 'login.html', {
            'error_message': 'Invalid username or password！',
        })


# 登出板块
def log_out(request):
    """用户登出视图"""
    username = request.session.get('username', '')
    last_active_time = request.session.get('last_active_time', '')
    
    # 创建登出记录（使用 AuthService 创建登录记录，但 action 为 'logout'）
    if username:
        # 注意：AuthService.create_login_record 只支持 'login' action
        # 登出记录暂时直接创建，后续可以扩展 AuthService 支持 logout
        LoginInfo.objects.create(
            username=username,
            week=0,
            action='logout',
            action_time=datetime.datetime.now(),
            last_active_time=last_active_time,
            device_info=request.META.get('HTTP_USER_AGENT', ''),
        )
    
    logout(request)
    return redirect('login')


# 更新用户活跃时间
@csrf_exempt
def update_last_activity(request):
    """更新用户最后活跃时间（包含心跳机制）"""
    if request.method == 'POST':
        print('last_active_time updated.')
        if request.session.get('is_login', False):
            # 使用 AuthService 更新活跃时间
            username = request.session.get('username', '')
            if username:
                AuthServiceImpl.update_last_activity(username, request)
        return JsonResponse({"status": "success"})
    
    # 接受心跳机制数据
    if request.method == 'GET':
        if request.session.get('is_login', False):
            this_datetime = datetime.datetime.now()
            if request.session.get('last_active_time', None):
                last_active_time = datetime.datetime.fromisoformat(request.session.get('last_active_time'))
                print(f'interval: {(this_datetime - last_active_time).total_seconds()}')
                if (this_datetime-last_active_time).total_seconds() > 60 * 10:  # 10分钟
                    # 心跳机制验证失败1，学生异常挂机
                    username = request.session.get('username')
                    try:
                        student_instance = UserServiceImpl.get_student_by_username(username)
                        if not student_instance:
                            return redirect('logout')
                        class_instance = UserServiceImpl.get_class_by_id(student_instance.class_instance_id)
                        if not class_instance:
                            return redirect('logout')
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
                    except (Students.DoesNotExist, Class.DoesNotExist, Attendance.DoesNotExist):
                        # 如果找不到相关记录，直接登出
                        print(f'心跳机制验证失败1,超时登出（找不到相关记录）')
                        return redirect('logout')
                else:
                    # 心跳机制验证成功，学生正常活动
                    print(f' 心跳机制验证成功，正常活动')
            else:
                # 心跳机制验证失败2，学生异常挂机
                print(f'心跳机制验证失败2,超时登出')
                return redirect('logout')
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error"}, status=400)
