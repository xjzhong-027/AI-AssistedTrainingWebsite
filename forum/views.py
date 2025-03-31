from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Post, Comment,Anonymous
from .forms import PostForm,CommentForm
from Account.models import Students, Teachers
from ELW.models import SubQuestion, MainQuestion, Unit, PaperPage, PageMainQuestion
import random
import string
from .filters import PostFilter
from announce.consumers import NotificationConsumer
from announce.models import Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from faker import Faker
fake = Faker()
# Create your views here.

def forum(request):
    username = request.session.get('username')
    print(username)
    role = request.session.get('role','none')
    if role == 'teacher':
        posts = Post.objects.all()  # 教师可以看到所有帖子
    else:
        posts = Post.objects.filter(is_public=True)  # 学生只能看到公开的帖子
    #目前帖子显示的优先级：置顶 精选 时间
    #精选目前是按照除了置顶的帖子之外，回复评论数量(>0)最多的前两条
    for post in posts:
        post.top_score = post.comments.count()
        post.save()
    top_posts = posts.filter(is_top=True).order_by('-top_score', '-created_at')
    non_top_posts = posts.filter(is_top=False).order_by('-created_at')
    reply = non_top_posts.filter(top_score__gt=0)
    star_posts_count = reply.count()
    if star_posts_count > 2:
        star_posts = reply.order_by('-top_score')[:2]
    else:
        star_posts = reply.all()
    rest_posts = non_top_posts.exclude(id__in=star_posts.values_list('id', flat=True)).order_by('-created_at')

    # 分页逻辑
    paginator_top = Paginator(top_posts, 2)
    #paginator_star = Paginator(star_posts, 2)
    paginator_rest = Paginator(rest_posts, 5)

    page_number = request.GET.get('page')
    top_page_obj = paginator_top.get_page(page_number)
    #star_page_obj = paginator_star.get_page(page_number)
    rest_page_obj = paginator_rest.get_page(page_number)

    post_lists = [
        {
            'title': '已置顶帖子',
            'posts': top_page_obj
        },
        {
            'title': '星标帖子',
            'posts': star_posts
        },
        {
            'title': '其他帖子',
            'posts': rest_page_obj
        }
    ]

    if role == 'teacher':
        template = 'forum/forum_teacher.html'
    elif role == 'student':
        template = 'forum/forum_student.html'
    else:
        template = 'forum/forum.html'
    form = PostForm()
    return render(request, template, {
        'username': username,
        'post_lists': post_lists,
        'form': form,
    })



def post_new(request):
    if not request.session.get('is_login', False):
        return redirect('login')  # 确保正确重定向到登录页面

    main_question_id = request.GET.get('main_question_id', None)
    sub_question_id = request.GET.get('sub_question_id', None)
    preset_title = request.GET.get('preset_title', '')
    announcement_id = request.GET.get('announcement_id', None)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            username = request.session.get('username')
            role = request.session.get('role', 'none')

            if role == 'teacher':
                user = Teachers.objects.get(username=username)
                post = form.save(commit=False)
                post.teacher = user
                post.author = user.username
                post.name = user.name
            elif role == 'student':
                user = Students.objects.get(username=username)
                post = form.save(commit=False)
                post.student = user
                post.author = user.username
                post.name = user.name
            else:
                messages.error(request, 'Invalid role')
                return redirect('forum:forum')

            post.created_at = timezone.now()
            if sub_question_id:
                post.is_question= True
                post.sub_question_id = sub_question_id
                post.main_question_id = main_question_id
            post.save()

            if form.cleaned_data['is_anonymous']:
                anonymous_name = random_generate()
                while Anonymous.objects.filter(anonymous_name=anonymous_name, post=post).exists():
                    anonymous_name = random_generate()
                Anonymous.objects.create(user=user, post=post, anonymous_name=anonymous_name)
                post.anonymous_name = anonymous_name
                post.name = anonymous_name
                post.save()

            return redirect('forum:forum')
    else:
        initial_data = {'title': preset_title} if preset_title else {}
        form = PostForm(initial=initial_data)

    return render(request, 'forum/add_post.html', {'form': form})

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    top_level_comments = post.comments.filter(parent_comment__isnull=True).order_by('created_at')
    form = CommentForm()
    reply_form = CommentForm()
    # 分页逻辑
    paginator = Paginator(top_level_comments, 5)  # 每页显示5个顶级评论
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'forum/post_detail.html', {
        'post': post,
        'comments': page_obj,
        'form': form,
        'reply_form': reply_form
    })

def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    role = request.session.get('role', 'none')
    username = request.session.get('username')

    if role == 'teacher':
        # 教师可以删除任何帖子
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('forum:forum')
    elif post.author == username:
        # 学生只能删除自己的帖子
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('forum:forum')
    else:
        # 无权限删除
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('forum:post_detail', post_id=post.id)

def post_top(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.is_top = True if not post.is_top else False
    post.save()
    return redirect('forum:forum')

def search_posts(request):
    filter = PostFilter(request.GET, queryset=Post.objects.all())
    return render(request, 'forum/searchforum.html', {'filter': filter})

#还需要 练习端有记录完成后才能显示 的逻辑
def question_post(request):
    role = request.session.get('role', 'none')
    username = request.session.get('username')
    selected_unit_id = request.GET.get('unit', None)
    selected_page_id = request.GET.get('page', None)

    posts = Post.objects.filter(is_question=True)

    if selected_unit_id:
        unit = Unit.objects.get(id=selected_unit_id)
        pages = PaperPage.objects.filter(unit=unit)
        page_main_questions = PageMainQuestion.objects.filter(page__in=pages)
        main_questions = MainQuestion.objects.filter(selected_main_questions__in=page_main_questions)
        sub_questions = SubQuestion.objects.filter(
            selected_sub_questions__page_main_question__in=page_main_questions
        )
        posts = posts.filter(
            Q(main_question__in=main_questions) | Q(sub_question__in=sub_questions)
        )

    if selected_page_id:
        page = PaperPage.objects.get(id=selected_page_id)
        page_main_questions = PageMainQuestion.objects.filter(page=page)
        main_questions = MainQuestion.objects.filter(selected_main_questions__in=page_main_questions)
        sub_questions = SubQuestion.objects.filter(
            selected_sub_questions__page_main_question__in=page_main_questions
        )
        posts = posts.filter(
            Q(main_question__in=main_questions) | Q(sub_question__in=sub_questions)
        )


    if role == 'student':
        student = Students.objects.get(username=username)
        class_instance = student.class_instance
        units = Unit.objects.filter(class_instance=class_instance)
        pages = PaperPage.objects.filter(unit__in=units)
        # 获取这些页面下的所有主题和小题
        page_main_questions = PageMainQuestion.objects.filter(page__in=pages)
        main_questions = MainQuestion.objects.filter(selected_main_questions__in=page_main_questions)
        sub_questions = SubQuestion.objects.filter(
            selected_sub_questions__page_main_question__in=page_main_questions
        )
        # 筛选与这些主题和小题相关的帖子
        posts = posts.filter(
            Q(main_question__in=main_questions) | Q(sub_question__in=sub_questions)
        )

    elif role != 'teacher':
        posts = Post.objects.none()



    # 分页功能
    paginator = Paginator(posts, 10)  # 每页显示 10 条帖子
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # 获取所有单元和页面，用于前端选择
    units = Unit.objects.all()
    pages = PaperPage.objects.all()

    return render(request, 'forum/question_post.html', {
        'posts': posts,
        'units': units,
        'pages': pages,
        'selected_unit_id': selected_unit_id,
        'selected_page_id': selected_page_id
    })


def my_post(request):
    username = request.session.get('username')
    role = request.session.get('role', 'none')

    if not username:
        messages.error(request, 'You are not logged in.')
        return redirect('login')

    if role == 'teacher':
        user = Teachers.objects.get(username=username)
        posts = Post.objects.filter(teacher=user)
    elif role == 'student':
        user = Students.objects.get(username=username)
        posts = Post.objects.filter(student=user)
    else:
        messages.error(request, 'Invalid role')
        return redirect('forum:forum')

    return render(request, 'forum/my_post.html', {'posts': posts})

def non_public(request):
    role = request.session.get('role', 'none')
    username = request.session.get('username')
    if role == 'student':
        # 学生只能看到自己隐藏的帖子
        posts = Post.objects.filter(is_public=False, author=username)
    elif role == 'teacher':
        # 教师可以看到所有隐藏的帖子
        posts = Post.objects.filter(is_public=False)
    else:
        # 如果用户不是学生或教师，返回空列表或重定向
        posts = Post.objects.none()

    return render(request, 'forum/non_public.html', {'posts': posts})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    username = request.session.get('username')

    if post.author != username:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('forum:my_post')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('forum:my_post')
    else:
        form = PostForm(instance=post)  # 使用当前帖子的数据初始化表单

    return render(request, 'forum/edit_post.html', {'form': form, 'post': post})


# @login_required
# def add_comment(request, post_id, parent_comment_id=None):
#     post = get_object_or_404(Post, pk=post_id)
#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             username = request.session.get('username')
#             if username:
#                 user = User.objects.get(username=username)
#                 comment = form.save(commit=False)
#                 comment.author = user
#                 comment.name = user
#                 comment.post = post
#                 if parent_comment_id:
#                     comment.parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
#                 comment.save()
#                 if form.cleaned_data['is_anonymous']:
#                     # 如果已存在 使用之前的
#                     if Anonymous.objects.filter(user=user, post=post).exists():
#                         anonymous_instance = Anonymous.objects.get(user=user, post=post)
#                         comment.anonymous_name = anonymous_instance.anonymous_name
#                         comment.name = comment.anonymous_name
#                         #comment.anonymous_name = Anonymous.objects.get(user=user, post=post)
#                         print(comment.anonymous_name)
#                         comment.save()
#                     else:
#                         anonymous_name = random_generate()
#                         while Anonymous.objects.filter(anonymous_name=anonymous_name,post=post).exists():
#                             anonymous_name = random_generate()
#                         Anonymous.objects.create(user=user, post=post, anonymous_name=anonymous_name)
#                         comment.anonymous_name = anonymous_name
#                         comment.name = anonymous_name
#                         comment.save()
#                 else:
#                     post_author = comment.post.author
#                     if post_author != comment.author:
#                         Message.objects.create(
#                             sender=comment.author,
#                             receiver=post_author,
#                             content=f"New comment on your post '{comment.post.title}'",
#                             post_id=post.id
#                         )
#                 #websocket实现实时通知
#                 if comment.post.author != comment.author:
#                     async_to_sync(get_channel_layer().group_send)(
#                         f'user_{comment.post.author.id}',
#                         {
#                             'type': 'notification_message',
#                             'message': f"You have a new reply on your post '{comment.post.title}'",
#                             'post_id': comment.post.id
#                         }
#                     )
#
#                     if comment.parent_comment and comment.parent_comment.author != comment.author:
#                         Message.objects.create(
#                             sender=comment.author,
#                             receiver=comment.parent_comment.author,
#                             content=f"New reply to your comment on post '{post.title}'",
#                             post_id=post.id
#                         )
#                     if comment.parent_comment and comment.parent_comment.author != comment.author:
#                         async_to_sync(get_channel_layer().group_send)(
#                             f'user_{comment.parent_comment.author.id}',
#                             {
#                                 'type': 'notification_message',
#                                 'message': f"You have a new reply to your comment on post '{post.title}'",
#                                 'post_id': comment.post.id
#                             }
#                         )
#
#                 return redirect('forum:post_detail', post_id=post_id)
#     else:
#         form = CommentForm()
#
#     return render(request, 'forum/add_comment.html', {'form': form, 'post_id': post_id, 'parent_comment_id': parent_comment_id})
#
#
#
# def add_comment(request, post_id, parent_comment_id=None):
#     post = get_object_or_404(Post, pk=post_id)
#     if request.method == "POST":
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             username = request.session.get('username')
#             role = request.session.get('role', 'none')
#             if role == 'Teacher':
#                 user = Teachers.objects.get(username=username)
#             else:
#                 user = Students.objects.get(username=username)
#             if username:
#                 comment = form.save(commit=False)
#                 comment.author = user.username
#                 comment.name = user.name
#                 comment.post = post
#                 if parent_comment_id:
#                     comment.parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
#                 comment.save()
#                 if form.cleaned_data['is_anonymous']:
#                     if Anonymous.objects.filter(user=user, post=post).exists():
#                         anonymous_instance = Anonymous.objects.get(user=user, post=post)
#                         comment.anonymous_name = anonymous_instance.anonymous_name
#                         comment.name = comment.anonymous_name
#                         comment.save()
#                     else:
#                         anonymous_name = random_generate()
#                         while Anonymous.objects.filter(anonymous_name=anonymous_name, post=post).exists():
#                             anonymous_name = random_generate()
#                         Anonymous.objects.create(user=user, post=post, anonymous_name=anonymous_name)
#                         comment.anonymous_name = anonymous_name
#                         comment.name = anonymous_name
#                         comment.save()
#                 else:
#                     post_author = comment.post.author
#                     if post_author != comment.author:
#                         Message.objects.create(
#                             sender=comment.author,
#                             receiver=post_author,
#                             content=f"New comment on your post '{comment.post.title}'",
#                             post_id=post.id
#                         )
#                 if comment.post.author != comment.author:
#                     async_to_sync(get_channel_layer().group_send)(
#                         f'user_{comment.post.author.id}',
#                         {
#                             'type': 'notification_message',
#                             'message': f"You have a new reply on your post '{comment.post.title}'",
#                             'post_id': comment.post.id
#                         }
#                     )
#                     if comment.parent_comment and comment.parent_comment.author != comment.author:
#                         Message.objects.create(
#                             sender=comment.author,
#                             receiver=comment.parent_comment.author,
#                             content=f"New reply to your comment on post '{post.title}'",
#                             post_id=post.id
#                         )
#                         async_to_sync(get_channel_layer().group_send)(
#                             f'user_{comment.parent_comment.author.id}',
#                             {
#                                 'type': 'notification_message',
#                                 'message': f"You have a new reply to your comment on post '{post.title}'",
#                                 'post_id': comment.post.id
#                             }
#                         )
#                 if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#                     return JsonResponse({'success': True})
#                 else:
#                     return JsonResponse({'success': True, 'redirect': reverse('forum:post_detail', args=[post_id])})
#             else:
#                 return JsonResponse({'success': False, 'message': '用户未登录'})
#         else:
#             return JsonResponse({'success': False, 'message': '表单数据无效'})
#     else:
#         form = CommentForm()
#         return render(request, 'forum/add_comment.html', {'form': form, 'post_id': post_id, 'parent_comment_id': parent_comment_id})

def add_comment(request, post_id, parent_comment_id=None):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            username = request.session.get('username')
            role = request.session.get('role', 'none')

            if role == 'teacher':
                user = Teachers.objects.get(username=username)
                comment = form.save(commit=False)
                comment.teacher = user
            elif role == 'student':
                user = Students.objects.get(username=username)
                comment = form.save(commit=False)
                comment.student = user
            else:
                return JsonResponse({'success': False, 'message': 'Invalid role'})

            comment = form.save(commit=False)
            comment.author = user.username
            comment.post = post
            if parent_comment_id:
                comment.parent_comment = get_object_or_404(Comment, pk=parent_comment_id)

            if form.cleaned_data['is_anonymous']:
                if Anonymous.objects.filter(user=user, post=post).exists():
                    anonymous_instance = Anonymous.objects.get(user=user, post=post)
                    comment.anonymous_name = anonymous_instance.anonymous_name
                    comment.name = anonymous_instance.anonymous_name
                else:
                    anonymous_name = random_generate()
                    while Anonymous.objects.filter(anonymous_name=anonymous_name, post=post).exists():
                        anonymous_name = random_generate()
                    Anonymous.objects.create(user=user, post=post, anonymous_name=anonymous_name)
                    comment.anonymous_name = anonymous_name
                    comment.name = anonymous_name
            else:
                comment.author = user.username
                comment.name = user.name

            comment.save()

            # 发送消息通知
            if not form.cleaned_data['is_anonymous']:
                if comment.post.author != comment.author:
                    Message.objects.create(
                        sender=user.username,
                        receiver=comment.post.author,
                        content=f"New comment on your post '{comment.post.title}'",
                        post=post
                    )
                    async_to_sync(get_channel_layer().group_send)(
                        f'user_{comment.post.author}',
                        {
                            'type': 'notification_message',
                            'message': f"You have a new reply on your post '{comment.post.title}'",
                            'post_id': post.id
                        }
                    )

                if comment.parent_comment and comment.parent_comment.author != comment.author:
                    Message.objects.create(
                        sender=user.username,
                        receiver=comment.parent_comment.author,
                        content=f"New reply to your comment on post '{post.title}'",
                        post=post
                    )
                    async_to_sync(get_channel_layer().group_send)(
                        f'user_{comment.parent_comment.author}',
                        {
                            'type': 'notification_message',
                            'message': f"You have a new reply to your comment on post '{post.title}'",
                            'post_id': post.id
                        }
                    )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': True, 'redirect': reverse('forum:post_detail', args=[post_id])})
        else:
            return JsonResponse({'success': False, 'message': '表单数据无效'})
    else:
        form = CommentForm()
        return render(request, 'forum/add_comment.html', {'form': form, 'post_id': post_id, 'parent_comment_id': parent_comment_id})


def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    role = request.session.get('role', 'none')
    username = request.session.get('username')

    if role == 'teacher' or comment.author == username:
        # 教师可以删除任何评论
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('forum:post_detail', post_id=comment.post.id)
    else:
        # 无权限删除
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('forum:post_detail', post_id=comment.post.id)

#生成随机匿名用户
def random_generate(length=10):
    random_length = random.randint(4, 5)
    random_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(random_chars) for _ in range(random_length))
    #username = string.ascii_uppercase + string.ascii_lowercase + string.digits
    username=fake.first_name() + fake.last_name() + "_" +random_string
    return username

# def generate_anonymous_names(request):
#     if request.method == 'POST':
#         length = int(request.POST.get('length', 10))
#         newname = random_generate(length)
#         #是否存在?
#         while Anonymous.objects.filter(anonymous_name=newname).exists():
#             newname = random_generate(length)
#         Anonymous.objects.create(anonymous_name=newname)
#         return redirect('forum:post_detail')
# #     return render(request, 'username_generator/generate.html')

def change_public(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    role = request.session.get('role', 'none')
    username = request.session.get('username')

    # 检查是否有权限更改公开状态
    if role == 'teacher' or post.author == username:
        post.is_public = not post.is_public

        if post.is_public and not post.anonymous_name:
            # 如果帖子变为公开且之前没有设置匿名名称，则生成一个匿名名称
            anonymous_name = random_generate()
            while Post.objects.filter(anonymous_name=anonymous_name).exists():
                anonymous_name = random_generate()
            post.anonymous_name = anonymous_name
            post.is_anonymous= True
            post.name = anonymous_name

        post.save()
        messages.success(request, 'Post status updated successfully.')
    else:
        # 如果用户没有权限更改公开状态，显示错误信息
        messages.error(request, 'You do not have permission to change the public status of this post.')

    return redirect('forum:post_detail', post_id=post_id)