"""
CommunicationService implementation for forum functionality.

This module provides the concrete implementation of CommunicationService
for forum-related operations (Post, Comment).
"""
from typing import Optional, List
from common.services.communication_service import CommunicationService
from forum.models import Post, Comment, Anonymous
from Account.services.user_service_impl import UserServiceImpl
from ELW.services.content_service_impl import ContentServiceImpl
import random
import string
from faker import Faker

fake = Faker()


def random_generate():
    """Generate a random anonymous name"""
    random_length = random.randint(4, 5)
    random_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(random_chars) for _ in range(random_length))
    username = fake.first_name() + fake.last_name() + "_" + random_string
    return username


class CommunicationServiceImpl(CommunicationService):
    """CommunicationService implementation for forum functionality"""
    
    @staticmethod
    def create_post(
        title: str,
        content: str,
        author_username: str,
        author_role: str,
        main_question_id: Optional[int] = None,
        sub_question_id: Optional[int] = None,
        is_anonymous: bool = False
    ) -> Post:
        """创建论坛帖子"""
        # Get user based on role
        if author_role == 'teacher':
            user = UserServiceImpl.get_teacher_by_username(author_username)
            if not user:
                raise ValueError(f"Teacher not found: {author_username}")
            post = Post.objects.create(
                title=title,
                content=content,
                teacher=user,
                author=author_username,
                name=user.name,
                is_anonymous=is_anonymous
            )
        elif author_role == 'student':
            user = UserServiceImpl.get_student_by_username(author_username)
            if not user:
                raise ValueError(f"Student not found: {author_username}")
            post = Post.objects.create(
                title=title,
                content=content,
                student=user,
                author=author_username,
                name=user.name,
                is_anonymous=is_anonymous
            )
        else:
            raise ValueError(f"Invalid role: {author_role}")
        
        # Set question-related fields
        if main_question_id:
            main_question = ContentServiceImpl.get_main_question_by_id(main_question_id)
            if main_question:
                post.main_question = main_question
                post.is_question = True
        
        if sub_question_id:
            sub_question = ContentServiceImpl.get_sub_question_by_id(sub_question_id)
            if sub_question:
                post.sub_question = sub_question
                post.is_question = True
                # Ensure main_question is also set
                if not post.main_question and sub_question.main_question:
                    post.main_question = sub_question.main_question
        
        # Handle anonymous post
        if is_anonymous:
            anonymous_name = random_generate()
            while Anonymous.objects.filter(anonymous_name=anonymous_name, post=post).exists():
                anonymous_name = random_generate()
            Anonymous.objects.create(user=user, post=post, anonymous_name=anonymous_name)
            post.anonymous_name = anonymous_name
            post.name = anonymous_name
        
        post.save()
        return post
    
    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[Post]:
        """根据ID获取帖子"""
        try:
            return Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None
    
    @staticmethod
    def get_posts_by_question(
        main_question_id: Optional[int] = None,
        sub_question_id: Optional[int] = None
    ) -> List[Post]:
        """获取与题目相关的帖子列表"""
        posts = Post.objects.all()
        
        if sub_question_id:
            posts = posts.filter(sub_question_id=sub_question_id)
        elif main_question_id:
            posts = posts.filter(main_question_id=main_question_id)
        else:
            return []
        
        return list(posts.order_by('-created_at'))
    
    @staticmethod
    def create_comment(
        post_id: int,
        content: str,
        author_username: str,
        author_role: str,
        parent_comment_id: Optional[int] = None
    ) -> Comment:
        """创建评论"""
        # Get post
        post = CommunicationServiceImpl.get_post_by_id(post_id)
        if not post:
            raise ValueError(f"Post not found: {post_id}")
        
        # Get user based on role
        if author_role == 'teacher':
            user = UserServiceImpl.get_teacher_by_username(author_username)
            if not user:
                raise ValueError(f"Teacher not found: {author_username}")
            comment = Comment.objects.create(
                post=post,
                content=content,
                teacher=user,
                author=author_username,
                name=user.name
            )
        elif author_role == 'student':
            user = UserServiceImpl.get_student_by_username(author_username)
            if not user:
                raise ValueError(f"Student not found: {author_username}")
            comment = Comment.objects.create(
                post=post,
                content=content,
                student=user,
                author=author_username,
                name=user.name
            )
        else:
            raise ValueError(f"Invalid role: {author_role}")
        
        # Set parent comment if provided
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                comment.parent_comment = parent_comment
                comment.save()
            except Comment.DoesNotExist:
                pass  # Parent comment not found, but continue anyway
        
        return comment
    
    # Note: create_announcement, get_announcements_for_student, and send_message
    # are implemented in announce/services/communication_service_impl.py
    # These methods are not part of forum functionality
    
    @staticmethod
    def create_announcement(
        title: str,
        content: str,
        teacher_id: int,
        receiver_student_ids: Optional[List[int]] = None
    ) -> 'Announcement':
        """创建公告 - 此方法应在 announce 模块中实现"""
        raise NotImplementedError("create_announcement should be implemented in announce module")
    
    @staticmethod
    def get_announcements_for_student(student_id: int) -> List['Announcement']:
        """获取学生的公告列表 - 此方法应在 announce 模块中实现"""
        raise NotImplementedError("get_announcements_for_student should be implemented in announce module")
    
    @staticmethod
    def send_message(
        sender_username: str,
        receiver_username: str,
        content: str,
        message_type: str = 'private'
    ) -> 'Message':
        """发送消息 - 此方法应在 announce 模块中实现"""
        raise NotImplementedError("send_message should be implemented in announce module")




