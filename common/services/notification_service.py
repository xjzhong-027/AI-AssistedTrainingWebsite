"""
Notification service interface.

This interface provides unified notification and messaging functionality.
"""
from typing import List, Optional, Dict
from abc import ABC, abstractmethod


class NotificationService(ABC):
    """通知服务接口"""
    
    @staticmethod
    @abstractmethod
    def send_announcement_notification(
        announcement_id: int,
        receiver_usernames: List[str]
    ) -> bool:
        """发送公告通知（WebSocket）"""
        pass
    
    @staticmethod
    @abstractmethod
    def send_forum_reply_notification(
        post_id: int,
        comment_id: int,
        receiver_username: str
    ) -> bool:
        """发送论坛回复通知"""
        pass
    
    @staticmethod
    @abstractmethod
    def send_exam_result_notification(
        student_id: int,
        exam_id: int,
        score: float
    ) -> bool:
        """发送考试结果通知"""
        pass
    
    @staticmethod
    @abstractmethod
    def mark_message_as_read(message_id: int, username: str) -> bool:
        """标记消息为已读"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_unread_count(username: str) -> int:
        """获取未读消息数量"""
        pass
    
    @staticmethod
    @abstractmethod
    def broadcast_to_class(
        class_id: int,
        message: Dict,
        message_type: str = 'announcement'
    ) -> bool:
        """向班级广播消息"""
        pass

