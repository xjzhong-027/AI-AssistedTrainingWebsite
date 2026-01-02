from contextlib import nullcontext

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from collections import defaultdict
from .forms import MessageForm,AnnouncementForm
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect
from .models import Announcement, Message
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from ELW.models import Class, Course
from Account.services.user_service_impl import UserServiceImpl
from forum.models import Post
from announce.services.communication_service_impl import CommunicationServiceImpl
from announce.services.notification_service_impl import NotificationServiceImpl
from django.utils import timezone
from datetime import timedelta
from English_Listening_Website.scheduler import scheduler
from django.http import HttpResponseRedirect


# def message_list(request):
#     messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
#     return render(request, 'announce/message_list.html', {'messages': messages})

def message_list(request):
    """ 信息箱 """
    # 获取接收者的消息，并按时间倒序排序
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('login')

    messages = Message.objects.filter(receiver=username).order_by('-created_at')
    unread_count = Message.objects.filter(receiver=username, is_read=False).count()  # 获取未读消息数量
    request.session['unread_count'] = unread_count

    # 根据 status 参数筛选已读/未读消息
    status_filter = request.GET.get('status')
    if status_filter == 'read':
        messages = messages.filter(is_read=True)
    elif status_filter == 'unread':
        messages = messages.filter(is_read=False)
    elif status_filter == 'announcement':
        messages = messages.filter(is_announcement=True)

    # 标记消息已读/未读
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        action = request.POST.get('action')

        try:
            message = Message.objects.get(id=message_id)
            if action == 'mark_read':
                message.is_read = True
                message.read_at = timezone.now()
            elif action == 'mark_unread':
                message.is_read = False
                message.read_at = None
            message.save()
        except Message.DoesNotExist:
            pass

    return render(request, 'announce/message_list.html', {
        'messages': messages,
        'unread_count': unread_count,
        'username': username,
        'role': role
    })

def mark_all_as_read(request):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('logintest:login')
    messages = Message.objects.filter(receiver=username, is_read=False)
    for message in messages:
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
    return redirect('announce:message_list')

@require_POST
def mark_as_read(request, message_id):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('logintest:login')
    message = Message.objects.get(id=message_id, receiver=username)
    message.is_read = True
    message.read_at = timezone.now()
    message.save()
    return render(request, 'announce/message_list.html')

def mark_unread(request, announcement_id):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('logintest:login')
    if request.method == 'POST':
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        if request.user in announcement.receivers.all():
            messages = Message.objects.filter(
                announcement=announcement,
                receiver=request.user,
                is_announcement=True,
                is_read=True
            )
            for message in messages:
                message.is_read = False
                message.read_at = None
                message.save()

            return JsonResponse({'status': 'success', 'message': 'Announcement marked as unread.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to view this announcement.'}, status=403)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def handle_view_request(request, message_id):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('logintest:login')
    message = Message.objects.get(receiver=username, id=message_id)
    if message.post:
        return HttpResponseRedirect(f'/forum/post/{message.post.id}/')
    elif message.announcement:
        return HttpResponseRedirect(f'/announce/announcements/detail/{message.announcement.id}/')
    else:
        return JsonResponse({'error': 'Invalid message type'}, status=400)

def message_view(request):
    sender = request.session.get('request.user')  # 从 session 中获取用户名
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # 获取表单数据
            receiver = form.cleaned_data['receiver']
            content = form.cleaned_data['content']
            print(request.user)
            # Use CommunicationService to send message
            CommunicationServiceImpl.send_message(
                sender_username=sender,
                receiver_username=receiver,
                content=content,
                message_type='private'
            )
            # 显示发送成功页面
            return render(request,'announce/message_success.html', {'content': content})
    else:
        form = MessageForm()  # GET 请求时，显示空表单
    return render(request, 'announce/message_form.html', {'form': form})


# @login_required
# @require_http_methods(["GET", "POST"])
# def announcements(request):
#     role = request.session.get('role', 'none')
#     if role != 'Teacher':
#         return JsonResponse({'error': '只有教师可以管理公告'}, status=403)
#     if request.method == 'GET':
#         form = AnnouncementForm()
#         announcements = Announcement.objects.all().order_by('-created_at')
#         paginator = Paginator(announcements, 3)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#         return render(request, 'announce/announcements.html', {'form': form, 'page_obj': page_obj})
#
#     elif request.method == 'POST':
#         p_type = request.POST.get('type')
#         if p_type == 'delete':
#             a_id = request.POST.get('a_id')
#             Announcement.objects.filter(id=a_id).delete()
#             return JsonResponse({'success': '公告已删除'}, status=200)
#         elif p_type == 'create':
#             form = AnnouncementForm(request.POST)
#             if form.is_valid():
#                 announcement = form.save(commit=False)
#                 announcement.save()
#                 receivers = form.cleaned_data['receivers']
#                 if form.cleaned_data['send_to_all']:
#                     receivers = User.objects.all()
#                 announcement.receivers.set(receivers)
#                 for receiver in receivers:
#                     Message.objects.create(
#                         sender=request.user,
#                         receiver=receiver,
#                         content=announcement.a_content,
#                         is_announcement=True
#                     )
#                     async_to_sync(get_channel_layer().group_send)(
#                         f'user_{receiver.id}',
#                         {
#                             'type': 'notification_message',
#                             'message': f"New announcement: {announcement.a_title}"
#                         }
#                     )
#                 return JsonResponse({'success': '公告已发布'}, status=200)
#             else:
#                 return JsonResponse({'error': '表单验证失败'}, status=400)
#         return JsonResponse({'error': '请求类型错误'}, status=400)

    # a_title = request.POST.get('a_title')
            # a_content = request.POST.get('a_content')
            # receivers = request.POST.getlist('receivers[]')  # 获取选中的接收者ID列表
            # if not a_title or not a_content:
            #     return JsonResponse({'error': '标题和内容不能为空'}, status=400)
        #     announcement = Announcement.objects.create(a_title=a_title, a_content=a_content)
        #     for receiver_id in receivers:
        #         receiver = User.objects.get(id=receiver_id)
        #         announcement.receivers.add(receiver)
        #     return JsonResponse({'success': '公告已发布'}, status=200)
        # return JsonResponse({'error': '请求类型错误'}, status=400)


@require_http_methods(["GET", "POST"])
def announcements(request):
    username = request.session.get('username')
    role = request.session.get('role', 'none')
    if role != 'teacher':
        return JsonResponse({'error': '只有教师可以管理公告'}, status=403)

    if request.method == 'POST':
        p_type = request.POST.get('type')
        if p_type == 'delete':
            a_id = request.POST.get('a_id')
            CommunicationServiceImpl.delete_announcement(int(a_id))
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
                teacher = UserServiceImpl.get_teacher_by_username(username)
                if not teacher:
                    return JsonResponse({'error': '教师不存在'}, status=400)

                if select_all:
                    # 获取所有学生：需要遍历所有班级，然后获取每个班级的学生
                    # 由于 UserService 没有 get_all_students 方法，暂时保留直接查询
                    # TODO: 考虑扩展 UserService 接口添加 get_all_students 方法
                    from Account.services.user_service_impl import UserServiceImpl
                    receivers = UserServiceImpl.get_all_students()
                    receiver_student_ids = [r.id for r in receivers]
                else:
                    receiver_student_ids = [r.id for r in receivers]

                # Use CommunicationService to create announcement
                try:
                    announcement = CommunicationServiceImpl.create_announcement(
                        title=a_title,
                        content=a_content,
                        teacher_id=teacher.id,
                        receiver_student_ids=receiver_student_ids
                    )
                except ValueError as e:
                    return JsonResponse({'error': str(e)}, status=400)

                # Send messages to receivers
                receiver_usernames = []
                for receiver in receivers:
                    CommunicationServiceImpl.send_message(
                        sender_username=username,
                        receiver_username=receiver.username,
                        content=a_content,
                        message_type='announcement'
                    )
                    receiver_usernames.append(receiver.username)
                
                # Use NotificationService to send announcement notifications
                if receiver_usernames:
                    NotificationServiceImpl.send_announcement_notification(
                        announcement_id=announcement.id,
                        receiver_usernames=receiver_usernames
                    )
                
                return JsonResponse({'success': '公告已发布'}, status=200)
            else:
                # 返回具体的表单错误信息
                return JsonResponse({'error': form.errors.as_json()}, status=400)


    elif request.method == 'GET':
        form = AnnouncementForm()
        # Note: CommunicationService doesn't have get_all_announcements method
        # We'll keep direct query for now, but this should be added to the interface
        announcements = Announcement.objects.all().order_by('-created_at').prefetch_related('receivers')
        paginator = Paginator(announcements, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # 按班级分组学生
        from Account.services.user_service_impl import UserServiceImpl
        students_by_class = defaultdict(list)
        for student in UserServiceImpl.get_all_students():
            students_by_class[student.class_instance].append(student)

        return render(request, 'announce/announcements.html', {
            'form': form,
            'page_obj': page_obj,
            'students_by_class': students_by_class.items()
        })


# def announcement_detail(request):
#     student = request.user
#     announcements = Announcement.objects.filter(receivers=student).order_by('-created_at')
#     return render(request, 'announce/announcement_student.html', {'announcements': announcements})
#     # current_user = request.user
#     # announcement = get_object_or_404(Announcement, pk=announcement_id)
#     #
    # # 检查当前用户是否有此公告的未读消息
    # unread_message = Message.objects.filter(
    #     content=announcement.a_content,
    #     receiver=current_user,
    #     is_announcement=True,
    #     is_read=False
    # ).first()
    #
    # # 如果存在未读消息，则标记为已读
    # if unread_message:
    #     unread_message.is_read = True
    #     unread_message.save()
    #
    # return render(request, 'announce/announcement_student.html', {'announcement': announcement})

# #
# def message_detail(request, message_id):
#     message = get_object_or_404(Message, pk=message_id, receiver=request.user)
#     if message.is_announcement:
#         return redirect('announce:announcement_detail', announcement_id=message.id)
#     else:
#         return redirect('forum:post_detail', post_id=message.content)


@require_http_methods(["GET"])
def load_receivers(request):
    class_id = request.GET.get('class_id')
    if class_id:
        try:
            class_id = int(class_id)  # 确保 class_id 是整数
            # 使用 UserService 获取班级学生
            students = UserServiceImpl.get_class_students(class_id)
            # 按名称排序
            students = sorted(students, key=lambda s: s.name)
            receivers_html = render_to_string('announce/receivers.html', {'receivers': students})
            return JsonResponse({'receiversHtml': receivers_html})
        except ValueError:
            # 如果 class_id 不是有效的整数，返回空列表
            return JsonResponse({'receiversHtml': ''})
    return JsonResponse({'receiversHtml': ''})


def announcement_state(request, announcement_id):
    role = request.session.get('role', 'none')
    if role != 'teacher':
        return JsonResponse({'error': '只有教师可以查看公告阅读状态'}, status=403)

    announcement = get_object_or_404(Announcement, pk=announcement_id)
    messages = Message.objects.filter(
        announcement=announcement,
        is_announcement=True
    )

    # 将消息按接收者分组
    messages_by_receiver = {}
    for message in messages:
        if message.receiver not in messages_by_receiver:
            messages_by_receiver[message.receiver] = []
        messages_by_receiver[message.receiver].append(message)

    return render(request, 'announce/announce_state.html', {
        'announcement': announcement,
        'messages_by_receiver': messages_by_receiver
    })


# @login_required
# def student_announcements(request):
#     student = request.user
#     announcements = Announcement.objects.filter(receivers=student).order_by('-created_at')
#     announcement_status = {}
#
#     for announcement in announcements:
#         messages = Message.objects.filter(
#             announcement=announcement,
#             receiver=student,
#             is_announcement=True
#         ).first()  # 使用 first() 来获取最新的消息（如果有的话）
#
#         if messages:
#             announcement_status[announcement.id] = {
#                 'is_read': messages.is_read,
#                 'read_at': messages.read_at
#             }
#         else:
#             announcement_status[announcement.id] = {
#                 'is_read': False,
#                 'read_at': None
#             }
#
#
#     paginator = Paginator(announcements, 5)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#
#     return render(request, 'announce/student_announcements.html', {'page_obj': page_obj})
#
#
# @login_required
# def announcement_detail(request, announcement_id):
#     announcement = get_object_or_404(Announcement, pk=announcement_id)
#     if request.user in announcement.receivers.all():
#         messages = Message.objects.filter(
#             announcement=announcement,
#             receiver=request.user,
#             is_announcement=True
#         )
#         for message in messages:
#             if not message.is_read:
#                 message.is_read = True
#                 message.read_at = timezone.now()  # 设置已读时间
#                 message.save()
#
#         return render(request, 'announce/announcement_detail.html',
#                       {'announcement': announcement, 'messages': messages})
#     else:
#         return JsonResponse("您没有权限查看此公告", status=403)



def student_announcements(request):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('logintest:login')
    student = UserServiceImpl.get_student_by_username(username)
    if not student:
        return redirect('logintest:login')
    announcements = student.announcements.all().order_by('-created_at')

    # 设置每页显示的公告数量
    paginator = Paginator(announcements, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    announcement_list = []
    for announcement in page_obj:
        message = Message.objects.filter(announcement=announcement, receiver=username).first()
        if message:
            is_read = message.is_read
            read_at = message.read_at if message.read_at else None
        else:
            is_read = False
            read_at = None
        announcement_list.append({
            'a_title': announcement.a_title,
            'created_at': announcement.created_at,
            'is_read': is_read,
            'read_at': read_at,
            'announcement_id': announcement.id
        })

    return render(request, 'announce/student_announcements.html',
                  {'page_obj': page_obj, 'announcement_list': announcement_list})


def announcement_detail(request, announcement_id):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        # 如果用户未登录，重定向到登录页面
        return redirect('logintest:login')
    student = UserServiceImpl.get_student_by_username(username)
    if not student:
        return redirect('logintest:login')
    announcement = get_object_or_404(Announcement, pk=announcement_id)
    if student in announcement.receivers.all():
        messages = Message.objects.filter(
            announcement=announcement,
            receiver=username,
            is_announcement=True
        )
        for message in messages:
            if not message.is_read:
                message.is_read = True
                message.read_at = timezone.now()  # 设置已读时间
                message.save()
        return render(request, 'announce/announcement_detail.html',
                      {'announcement': announcement, 'messages': messages})
    else:
        return JsonResponse({"error": "您没有权限查看此公告"}, status=403)



# @login_required
# def announcement_detail(request, announcement_id):
#     announcement = get_object_or_404(Announcement, pk=announcement_id)
#     if request.user in announcement.receivers.all():
#         messages = Message.objects.filter(
#             announcement=announcement,
#             receiver=request.user,
#             is_announcement=True
#         )
#         for message in messages:
#             if not message.is_read:
#                 message.is_read = True
#                 message.read_at = timezone.now()  # 设置已读时间
#                 message.save()
#
#         return render(request, 'announce/announcement_detail.html',
#                       {'announcement': announcement, 'messages': messages})
#     else:
#         return JsonResponse("您没有权限查看此公告", status=403)

# @login_required
# def mark_unread(request, announcement_id):
#     if request.method == 'POST':
#         announcement = get_object_or_404(Announcement, pk=announcement_id)
#         if request.user in announcement.receivers.all():
#             messages = Message.objects.filter(
#                 content=announcement.a_content,
#                 receiver=request.user,
#                 is_announcement=True,
#                 is_read=True
#             )
#             for message in messages:
#                 message.is_read = False
#                 message.read_at = None  # 清除已读时间
#                 message.save()
#
#
#             reminder_minutes = int(request.POST.get('reminder_minutes', 10))  # 默认为10分钟
#
#             # 安排在指定分钟后重新提醒
#             schedule_notification(request.user.id, reminder_minutes, f"New announcement: {announcement.a_title}",announcement.id)
#
#             return JsonResponse({'status': 'success', 'message': 'Announcement marked as unread and reminder set.'})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'You do not have permission to view this announcement.'}, status=403)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)





def reminder(request, announcement_id):
    if request.method == 'POST':
        username = request.session.get('username')
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return JsonResponse({'error': '学生不存在'}, status=400)

        reminder_minutes = int(request.POST.get('reminder_minutes', 10))  # 默认为10分钟
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        if student in announcement.receivers.all():
            user_id = student.id
            # 安排在指定分钟后重新提醒
            schedule_notification(user_id, reminder_minutes, f"New announcement: {announcement.a_title}", announcement.id)
            return JsonResponse({'status': 'success', 'message': 'Reminder set.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to view this announcement.'}, status=403)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def send_notification(student_id, message, announcement_id):
    # 获取学生对象
    student = UserServiceImpl.get_student_by_id(student_id)
    if not student:
        return JsonResponse({'error': '学生不存在'}, status=400)
    # Use NotificationService to send announcement notification
    NotificationServiceImpl.send_announcement_notification(
        announcement_id=announcement_id,
        receiver_usernames=[student.username]
    )

def schedule_notification(student_id, minutes, message, announcement_id):
    scheduler.add_job(
        send_notification,
        'date',
        run_date=timezone.now() + timedelta(minutes=minutes),
        args=[student_id, message, announcement_id]
    )