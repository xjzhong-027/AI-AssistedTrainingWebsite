"""
Serializers for Announcement API.
"""
from rest_framework import serializers
from announce.models import Announcement, Message


class AnnouncementSerializer(serializers.ModelSerializer):
    """公告序列化器"""
    teacher_name = serializers.CharField(source='teachers.name', read_only=True)
    teacher_id = serializers.IntegerField(source='teachers.id', read_only=True)
    receiver_ids = serializers.SerializerMethodField()
    receiver_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = ['id', 'a_title', 'a_content', 'created_at', 'teacher_id', 
                  'teacher_name', 'receiver_ids', 'receiver_count']
        read_only_fields = ['id', 'created_at']
    
    def get_receiver_ids(self, obj):
        """获取接收者ID列表"""
        return [student.id for student in obj.receivers.all()]
    
    def get_receiver_count(self, obj):
        """获取接收者数量"""
        return obj.receivers.count()


class AnnouncementCreateSerializer(serializers.Serializer):
    """创建公告序列化器"""
    a_title = serializers.CharField(max_length=64)
    a_content = serializers.CharField(max_length=3000, allow_blank=True, required=False)
    receiver_student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )


class AnnouncementUpdateSerializer(serializers.ModelSerializer):
    """更新公告序列化器"""
    
    class Meta:
        model = Announcement
        fields = ['a_title', 'a_content']


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'is_read', 'read_at', 
                  'created_at', 'post_id', 'announcement_id', 'is_announcement']
        read_only_fields = ['id', 'created_at', 'read_at']
    
    post_id = serializers.IntegerField(source='post.id', read_only=True, allow_null=True)
    announcement_id = serializers.IntegerField(source='announcement.id', read_only=True, allow_null=True)











