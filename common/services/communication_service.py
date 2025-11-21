"""
Communication service interface.

This interface provides unified access to forum, announcement, and messaging functionality.
"""
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from django.http import HttpRequest


class CommunicationService(ABC):
    """通信服务接口"""
    
    @staticmethod
    @abstractmethod
    def create_post(
        title: str,
        content: str,
        author_username: str,
        author_role: str,
        main_question_id: Optional[int] = None,
        sub_question_id: Optional[int] = None,
        is_anonymous: bool = False
    ) -> 'Post':
        """创建论坛帖子"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_post_by_id(post_id: int) -> Optional['Post']:
        """根据ID获取帖子"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_posts_by_question(
        main_question_id: Optional[int] = None,
        sub_question_id: Optional[int] = None
    ) -> List['Post']:
        """获取与题目相关的帖子列表"""
        pass
    
    @staticmethod
    @abstractmethod
    def create_comment(
        post_id: int,
        content: str,
        author_username: str,
        author_role: str,
        parent_comment_id: Optional[int] = None
    ) -> 'Comment':
        """创建评论"""
        pass
    
    @staticmethod
    @abstractmethod
    def create_announcement(
        title: str,
        content: str,
        teacher_id: int,
        receiver_student_ids: Optional[List[int]] = None
    ) -> 'Announcement':
        """创建公告"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_announcements_for_student(student_id: int) -> List['Announcement']:
        """获取学生的公告列表"""
        pass
    
    @staticmethod
    @abstractmethod
    def send_message(
        sender_username: str,
        receiver_username: str,
        content: str,
        message_type: str = 'private'
    ) -> 'Message':
        """发送消息"""
        pass

