"""
Forum API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from forum.api.serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer
)
from forum.services.communication_service_impl import CommunicationServiceImpl
from announce.services.notification_service_impl import NotificationServiceImpl
from Account.services.user_service_impl import UserServiceImpl
from rest_framework_simplejwt.tokens import UntypedToken


@extend_schema(tags=['论坛'])
class PostListView(APIView):
    """
    获取帖子列表 API
    
    GET /api/v1/forum/posts/
    
    Query Parameters:
    - category: 可选，分类筛选
    - search: 可选，搜索关键词
    - is_question: 可选，是否关于题目
    - main_question_id: 可选，按大题筛选
    - sub_question_id: 可选，按小题筛选
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取帖子列表"""
        from forum.models import Post
        
        # 获取用户角色
        role = self._get_user_role(request)
        
        # 基础查询
        if role == 'teacher':
            posts = Post.objects.all()
        else:
            # 学生只能看到公开的帖子或自己的帖子
            username = self._get_username(request)
            student = UserServiceImpl.get_student_by_username(username)
            if student:
                posts = Post.objects.filter(
                    Q(is_public=True) | Q(student=student)
                )
            else:
                posts = Post.objects.filter(is_public=True)
        
        # 筛选条件
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        is_question = request.query_params.get('is_question')
        main_question_id = request.query_params.get('main_question_id')
        sub_question_id = request.query_params.get('sub_question_id')
        
        if category and category != 'all':
            # 可以根据需要添加分类筛选
            pass
        
        if search:
            posts = posts.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        if is_question is not None:
            posts = posts.filter(is_question=is_question.lower() == 'true')
        
        if main_question_id:
            posts = posts.filter(main_question_id=main_question_id)
        
        if sub_question_id:
            posts = posts.filter(sub_question_id=sub_question_id)
        
        # 排序：置顶优先，然后按时间
        posts = posts.order_by('-is_top', '-created_at')
        
        serializer = PostSerializer(posts, many=True)
        return Result.success(data=serializer.data, message='success')
    
    def _get_user_role(self, request):
        """从 token 中获取用户角色"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except:
                pass
        return ''
    
    def _get_username(self, request):
        """从 token 中获取用户名"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('username', '')
            except:
                pass
        return ''


@extend_schema(tags=['论坛'])
class PostDetailView(APIView):
    """
    获取帖子详情 API
    
    GET /api/v1/forum/posts/{post_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """获取帖子详情"""
        post = CommunicationServiceImpl.get_post_by_id(post_id)
        if not post:
            return Result.not_found(message='Post not found')
        
        serializer = PostSerializer(post)
        return Result.success(data=serializer.data, message='success')


@extend_schema(tags=['论坛'])
class PostCreateView(APIView):
    """
    创建帖子 API
    
    POST /api/v1/forum/posts/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """创建帖子"""
        serializer = PostCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        # 获取用户信息
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        # 创建帖子
        try:
            post = CommunicationServiceImpl.create_post(
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                author_username=username,
                author_role=role,
                main_question_id=serializer.validated_data.get('main_question_id'),
                sub_question_id=serializer.validated_data.get('sub_question_id'),
                is_anonymous=serializer.validated_data.get('is_anonymous', False)
            )
            
            # 更新其他字段
            if 'is_public' in serializer.validated_data:
                post.is_public = serializer.validated_data['is_public']
            if 'anonymous_name' in serializer.validated_data:
                post.anonymous_name = serializer.validated_data['anonymous_name']
            if 'is_question' in serializer.validated_data:
                post.is_question = serializer.validated_data['is_question']
            post.save()
            
            result_serializer = PostSerializer(post)
            return Result.created(data=result_serializer.data, message='Post created successfully')
        except Exception as e:
            return Result.error(message=f'Failed to create post: {str(e)}', code=500)
    
    def _get_user_role(self, request):
        """从 token 中获取用户角色"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except:
                pass
        return ''
    
    def _get_username(self, request):
        """从 token 中获取用户名"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('username', '')
            except:
                pass
        return ''


@extend_schema(tags=['论坛'])
class PostUpdateView(APIView):
    """
    更新帖子 API
    
    PUT /api/v1/forum/posts/{post_id}/
    PATCH /api/v1/forum/posts/{post_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, post_id):
        """更新帖子"""
        return self._update(request, post_id, partial=False)
    
    def patch(self, request, post_id):
        """部分更新帖子"""
        return self._update(request, post_id, partial=True)
    
    def _update(self, request, post_id, partial=False):
        """更新帖子"""
        post = CommunicationServiceImpl.get_post_by_id(post_id)
        if not post:
            return Result.not_found(message='Post not found')
        
        serializer = PostUpdateSerializer(post, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        updated_post = CommunicationServiceImpl.update_post(post_id, serializer.validated_data)
        if not updated_post:
            return Result.error(message='Failed to update post', code=500)
        
        result_serializer = PostSerializer(updated_post)
        return Result.success(data=result_serializer.data, message='Post updated successfully')


@extend_schema(tags=['论坛'])
class PostDeleteView(APIView):
    """
    删除帖子 API
    
    DELETE /api/v1/forum/posts/{post_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, post_id):
        """删除帖子"""
        success = CommunicationServiceImpl.delete_post(post_id)
        if success:
            return Result.success(message='Post deleted successfully')
        return Result.not_found(message='Post not found')


@extend_schema(tags=['论坛'])
class CommentListView(APIView):
    """
    获取评论列表 API
    
    GET /api/v1/forum/posts/{post_id}/comments/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """获取评论列表"""
        comments = CommunicationServiceImpl.get_comments_by_post(post_id)
        serializer = CommentSerializer(comments, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(tags=['论坛'])
class CommentCreateView(APIView):
    """
    创建评论 API
    
    POST /api/v1/forum/posts/{post_id}/comments/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """创建评论"""
        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        # 获取用户信息
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        # 创建评论
        try:
            comment = CommunicationServiceImpl.create_comment(
                post_id=post_id,
                content=serializer.validated_data['content'],
                author_username=username,
                author_role=role,
                parent_comment_id=serializer.validated_data.get('parent_comment_id')
            )
            
            # 更新其他字段
            if 'is_anonymous' in serializer.validated_data:
                comment.is_anonymous = serializer.validated_data['is_anonymous']
            if 'anonymous_name' in serializer.validated_data:
                comment.anonymous_name = serializer.validated_data['anonymous_name']
            comment.save()
            
            # 发送回复通知（如果是回复帖子或回复评论）
            try:
                from forum.models import Post
                post = Post.objects.get(id=post_id)
                # 如果是回复帖子，通知帖子作者
                if not comment.parent_comment and post.author:
                    NotificationServiceImpl.send_forum_reply_notification(
                        post_id=post.id,
                        comment_id=comment.id,
                        receiver_username=post.author
                    )
                # 如果是回复评论，通知父评论作者
                elif comment.parent_comment and comment.parent_comment.author:
                    NotificationServiceImpl.send_forum_reply_notification(
                        post_id=post.id,
                        comment_id=comment.id,
                        receiver_username=comment.parent_comment.author
                    )
            except Exception as e:
                # 通知发送失败不影响评论创建
                print(f"Failed to send forum reply notification: {e}")
            
            result_serializer = CommentSerializer(comment)
            return Result.created(data=result_serializer.data, message='Comment created successfully')
        except Exception as e:
            return Result.error(message=f'Failed to create comment: {str(e)}', code=500)
    
    def _get_user_role(self, request):
        """从 token 中获取用户角色"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except:
                pass
        return ''
    
    def _get_username(self, request):
        """从 token 中获取用户名"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('username', '')
            except:
                pass
        return ''


@extend_schema(tags=['论坛'])
class CommentUpdateView(APIView):
    """
    更新评论 API
    
    PUT /api/v1/forum/comments/{comment_id}/
    PATCH /api/v1/forum/comments/{comment_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, comment_id):
        """更新评论"""
        return self._update(request, comment_id, partial=False)
    
    def patch(self, request, comment_id):
        """部分更新评论"""
        return self._update(request, comment_id, partial=True)
    
    def _update(self, request, comment_id, partial=False):
        """更新评论"""
        from forum.models import Comment
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Result.not_found(message='Comment not found')
        
        serializer = CommentUpdateSerializer(comment, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        updated_comment = CommunicationServiceImpl.update_comment(comment_id, serializer.validated_data)
        if not updated_comment:
            return Result.error(message='Failed to update comment', code=500)
        
        result_serializer = CommentSerializer(updated_comment)
        return Result.success(data=result_serializer.data, message='Comment updated successfully')


@extend_schema(tags=['论坛'])
class CommentDeleteView(APIView):
    """
    删除评论 API
    
    DELETE /api/v1/forum/comments/{comment_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, comment_id):
        """删除评论"""
        success = CommunicationServiceImpl.delete_comment(comment_id)
        if success:
            return Result.success(message='Comment deleted successfully')
        return Result.not_found(message='Comment not found')









