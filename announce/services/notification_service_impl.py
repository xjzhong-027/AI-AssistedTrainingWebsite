"""
NotificationService implementation for announce module.

This module implements the NotificationService interface, providing unified notification
and messaging functionality via WebSocket.
"""
from typing import List, Optional, Dict
from common.services.notification_service import NotificationService
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from announce.models import Message, Announcement
from Account.services.user_service_impl import UserServiceImpl


class NotificationServiceImpl(NotificationService):
    """通知服务实现"""
    
    @staticmethod
    def send_announcement_notification(
        announcement_id: int,
        receiver_usernames: List[str]
    ) -> bool:
        """发送公告通知（WebSocket）"""
        try:
            # Get announcement
            try:
                announcement = Announcement.objects.get(id=announcement_id)
            except Announcement.DoesNotExist:
                return False
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                return False
            
            # Send notification to each receiver
            for username in receiver_usernames:
                async_to_sync(channel_layer.group_send)(
                    f'user_{username}',
                    {
                        'type': 'notification_message',
                        'message': f"New announcement: {announcement.a_title}",
                        'announcement_id': announcement_id
                    }
                )
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def send_forum_reply_notification(
        post_id: int,
        comment_id: int,
        receiver_username: str
    ) -> bool:
        """发送论坛回复通知"""
        try:
            from forum.models import Post, Comment
            
            # Get post and comment
            try:
                post = Post.objects.get(id=post_id)
                comment = Comment.objects.get(id=comment_id)
            except (Post.DoesNotExist, Comment.DoesNotExist):
                return False
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                return False
            
            # Send notification
            async_to_sync(channel_layer.group_send)(
                f'user_{receiver_username}',
                {
                    'type': 'notification_message',
                    'message': f"You have a new reply on your post '{post.title}'",
                    'post_id': post_id
                }
            )
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def send_exam_result_notification(
        student_id: int,
        exam_id: int,
        score: float
    ) -> bool:
        """发送考试结果通知"""
        try:
            student = UserServiceImpl.get_student_by_id(student_id)
            if not student:
                return False
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                return False
            
            # Send notification
            async_to_sync(channel_layer.group_send)(
                f'user_{student.username}',
                {
                    'type': 'notification_message',
                    'message': f"Your exam result is ready. Score: {score}",
                    'exam_id': exam_id
                }
            )
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def mark_message_as_read(message_id: int, username: str) -> bool:
        """标记消息为已读"""
        try:
            message = Message.objects.get(id=message_id, receiver=username)
            message.is_read = True
            from django.utils import timezone
            message.read_at = timezone.now()
            message.save()
            return True
        except Message.DoesNotExist:
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_unread_count(username: str) -> int:
        """获取未读消息数量"""
        try:
            return Message.objects.filter(receiver=username, is_read=False).count()
        except Exception:
            return 0
    
    @staticmethod
    def broadcast_to_class(
        class_id: int,
        message: Dict,
        message_type: str = 'announcement'
    ) -> bool:
        """向班级广播消息"""
        try:
            # Get class students
            students = UserServiceImpl.get_class_students(class_id)
            if not students:
                return False
            
            channel_layer = get_channel_layer()
            if not channel_layer:
                return False
            
            # Broadcast to all students in the class
            for student in students:
                async_to_sync(channel_layer.group_send)(
                    f'user_{student.username}',
                    {
                        'type': 'notification_message',
                        'message': message.get('content', ''),
                        'message_type': message_type,
                        **message  # Include any additional fields
                    }
                )
            
            return True
        except Exception:
            return False




