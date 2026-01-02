"""
Announcement API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken

from common.api.response import Result
from announce.api.serializers import (
    AnnouncementSerializer, AnnouncementCreateSerializer, AnnouncementUpdateSerializer,
    MessageSerializer
)
from announce.services.communication_service_impl import CommunicationServiceImpl
from Account.services.user_service_impl import UserServiceImpl


class AnnouncementListView(APIView):
    """
    获取公告列表 API
    
    GET /api/v1/announcements/
    
    Query Parameters:
    - student_id: 可选，按学生筛选
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取公告列表"""
        from announce.models import Announcement
        
        student_id = request.query_params.get('student_id')
        
        if student_id:
            announcements = CommunicationServiceImpl.get_announcements_for_student(int(student_id))
        else:
            announcements = Announcement.objects.all().order_by('-created_at')
        
        serializer = AnnouncementSerializer(announcements, many=True)
        return Result.success(data=serializer.data, message='success')


class AnnouncementDetailView(APIView):
    """
    获取公告详情 API
    
    GET /api/v1/announcements/{announcement_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, announcement_id):
        """获取公告详情"""
        from announce.models import Announcement
        try:
            announcement = Announcement.objects.get(id=announcement_id)
        except Announcement.DoesNotExist:
            return Result.not_found(message='Announcement not found')
        
        serializer = AnnouncementSerializer(announcement)
        return Result.success(data=serializer.data, message='success')


class AnnouncementCreateView(APIView):
    """
    创建公告 API
    
    POST /api/v1/announcements/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """创建公告"""
        serializer = AnnouncementCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        # 获取教师ID
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'teacher':
            return Result.forbidden(message='Only teachers can create announcements')
        
        teacher = UserServiceImpl.get_teacher_by_username(username)
        if not teacher:
            return Result.not_found(message='Teacher not found')
        
        # 创建公告
        try:
            announcement = CommunicationServiceImpl.create_announcement(
                title=serializer.validated_data['a_title'],
                content=serializer.validated_data.get('a_content', ''),
                teacher_id=teacher.id,
                receiver_student_ids=serializer.validated_data.get('receiver_student_ids', [])
            )
            
            result_serializer = AnnouncementSerializer(announcement)
            return Result.created(data=result_serializer.data, message='Announcement created successfully')
        except Exception as e:
            return Result.error(message=f'Failed to create announcement: {str(e)}', code=500)
    
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


class AnnouncementUpdateView(APIView):
    """
    更新公告 API
    
    PUT /api/v1/announcements/{announcement_id}/
    PATCH /api/v1/announcements/{announcement_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, announcement_id):
        """更新公告"""
        return self._update(request, announcement_id, partial=False)
    
    def patch(self, request, announcement_id):
        """部分更新公告"""
        return self._update(request, announcement_id, partial=True)
    
    def _update(self, request, announcement_id, partial=False):
        """更新公告"""
        from announce.models import Announcement
        try:
            announcement = Announcement.objects.get(id=announcement_id)
        except Announcement.DoesNotExist:
            return Result.not_found(message='Announcement not found')
        
        serializer = AnnouncementUpdateSerializer(announcement, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        updated_announcement = CommunicationServiceImpl.update_announcement(
            announcement_id, serializer.validated_data
        )
        if not updated_announcement:
            return Result.error(message='Failed to update announcement', code=500)
        
        result_serializer = AnnouncementSerializer(updated_announcement)
        return Result.success(data=result_serializer.data, message='Announcement updated successfully')


class AnnouncementDeleteView(APIView):
    """
    删除公告 API
    
    DELETE /api/v1/announcements/{announcement_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, announcement_id):
        """删除公告"""
        success = CommunicationServiceImpl.delete_announcement(announcement_id)
        if success:
            return Result.success(message='Announcement deleted successfully')
        return Result.not_found(message='Announcement not found')


class MessageListView(APIView):
    """
    获取消息列表 API
    
    GET /api/v1/messages/
    
    Query Parameters:
    - receiver: 可选，接收者用户名
    - sender: 可选，发送者用户名
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取消息列表"""
        from announce.models import Message
        
        receiver = request.query_params.get('receiver')
        sender = request.query_params.get('sender')
        
        messages = Message.objects.all()
        
        if receiver:
            messages = messages.filter(receiver=receiver)
        
        if sender:
            messages = messages.filter(sender=sender)
        
        messages = messages.order_by('-created_at')
        
        serializer = MessageSerializer(messages, many=True)
        return Result.success(data=serializer.data, message='success')


class MessageDetailView(APIView):
    """
    获取消息详情 API
    
    GET /api/v1/messages/{message_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, message_id):
        """获取消息详情"""
        from announce.models import Message
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Result.not_found(message='Message not found')
        
        serializer = MessageSerializer(message)
        return Result.success(data=serializer.data, message='success')







