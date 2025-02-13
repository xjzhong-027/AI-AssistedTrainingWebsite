from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm,CommentForm
from django.contrib.auth.decorators import login_required #登陆后才能访问
from django.db import models

# Create your views here.


def forum(request):
    username = request.session.get('username')
    role = request.session.get('role')
    posts = Post.objects.all()
    # 帖子分类 目前仅完成全部帖子的类别
    category = request.GET.get('category', 'all')
    if category != 'all':
        posts = posts.filter(category=category)
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
    if role == 'Teacher':
        return render(request, 'forum/forum_teacher.html', {
            'top_posts': top_posts,
            'star_posts': star_posts,
            'rest_posts': rest_posts,
            'username': username,
        })
    elif role == 'Student':
        return render(request, 'forum/forum_student.html', {
            'top_posts': top_posts,
            'star_posts': star_posts,
            'rest_posts': rest_posts,
            'username': username,
        })
    # return render(request, forum/forum.html, {
    #     'top_posts': top_posts,
    #     'star_posts': star_posts,
    #     'rest_posts': rest_posts,
    #     'username': username,
    # })
    #return render(request, 'forum/forum.html', {'posts': posts})


def post_detail(request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        comments = post.comments.all().order_by('created_at')  # 按时间顺序显示评论
        comments = post.comments.filter(parent_comment__isnull=True)
        author = models.ForeignKey(User, on_delete=models.CASCADE) #获取user信息
        return render(request, 'forum/post_detail.html', {'post': post, 'comments': comments})



def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # post = Post.objects.create(author=request.username)
            # post.author = request.user # 设置发帖人为当前登录用户
            #post = Post(author=request.user)
            post.created_at = timezone.now()
            post.save()
            return redirect('forum')
    else:
        form = PostForm()
    return render(request, 'forum/add_post.html', {'form': form})

def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('forum')

def post_top(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.is_top = True if not post.is_top else False
    post.save()
    return redirect('forum')

def search_posts(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(title__icontains=query) | Post.objects.filter(content__icontains=query)
    else:
        posts = Post.objects.none()  # 如果没有查询词，则不显示任何帖子
    return render(request, 'forum/searchforum.html', {'posts': posts, 'query': query})


def add_comment(request, post_id, parent_comment_id=None):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if parent_comment_id:
                comment.parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
            comment.save()
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()
    return render(request, 'forum/add_comment.html', {'form': form, 'post_id': post_id, 'parent_comment_id': parent_comment_id})


