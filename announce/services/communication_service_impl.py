"""
CommunicationService implementation for announcement functionality.

This module provides the concrete implementation of CommunicationService
for announcement-related operations (Announcement, Message).
"""
from typing import Optional, List
from common.services.communication_service import CommunicationService
from announce.models import Announcement, Message
from Account.services.user_service_impl import UserServiceImpl


class CommunicationServiceImpl(CommunicationService):
    """CommunicationService implementation for announcement functionality"""
    
    # Note: create_post, get_post_by_id, get_posts_by_question, and create_comment
    # are implemented in forum/services/communication_service_impl.py
    # These methods are not part of announcement functionality
    
    @staticmethod
    def create_post(
        title: str,
        content: str,
        author_username: str,
        author_role: str,
        main_question_id: Optional[int] = None,
        sub_question_id: Optional[int] = None,
        is_anonymous: bool = False
    ) -> 'Post':
        """创建论坛帖子 - 此方法应在 forum 模块中实现"""
        raise NotImplementedError("create_post should be implemented in forum module")
    
    @staticmethod
    def get_post_by_id(post_id: int) -> Optional['Post']:
        """根据ID获取帖子 - 此方法应在 forum 模块中实现"""
        raise NotImplementedError("get_post_by_id should be implemented in forum module")
    
    @staticmethod
    def get_posts_by_question(
        main_question_id: Optional[int] = None,
        sub_question_id: Optional[int] = None
    ) -> List['Post']:
        """获取与题目相关的帖子列表 - 此方法应在 forum 模块中实现"""
        raise NotImplementedError("get_posts_by_question should be implemented in forum module")
    
    @staticmethod
    def create_comment(
        post_id: int,
        content: str,
        author_username: str,
        author_role: str,
        parent_comment_id: Optional[int] = None
    ) -> 'Comment':
        """创建评论 - 此方法应在 forum 模块中实现"""
        raise NotImplementedError("create_comment should be implemented in forum module")
    
    @staticmethod
    def create_announcement(
        title: str,
        content: str,
        teacher_id: int,
        receiver_student_ids: Optional[List[int]] = None
    ) -> Announcement:
        """创建公告"""
        # Get teacher
        teacher = UserServiceImpl.get_teacher_by_id(teacher_id)
        if not teacher:
            raise ValueError(f"Teacher not found: {teacher_id}")
        
        # Create announcement
        announcement = Announcement.objects.create(
            a_title=title,
            a_content=content,
            teachers=teacher
        )
        
        # Add receivers if provided
        if receiver_student_ids:
            for student_id in receiver_student_ids:
                student = UserServiceImpl.get_student_by_id(student_id)
                if student:
                    announcement.receivers.add(student)
        
        return announcement
    
    @staticmethod
    def get_announcements_for_student(student_id: int) -> List[Announcement]:
        """获取学生的公告列表"""
        student = UserServiceImpl.get_student_by_id(student_id)
        if not student:
            return []
        
        # Get all announcements where student is a receiver
        announcements = Announcement.objects.filter(receivers=student).order_by('-created_at')
        return list(announcements)
    
    @staticmethod
    def send_message(
        sender_username: str,
        receiver_username: str,
        content: str,
        message_type: str = 'private'
    ) -> Message:
        """发送消息"""
        message = Message.objects.create(
            sender=sender_username,
            receiver=receiver_username,
            content=content,
            is_announcement=(message_type == 'announcement')
        )
        return message

