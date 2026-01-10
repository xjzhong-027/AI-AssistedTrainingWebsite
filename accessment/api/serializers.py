"""
Serializers for Exam API.
"""
from rest_framework import serializers
from accessment.models import (
    StudentExamRecord, StudentPageRecord, StudentAnswer, StudentMediaPlayRecord
)
from ELW.models import Unit, PaperPage, SubQuestion, MainQuestion


class StudentAnswerSerializer(serializers.ModelSerializer):
    """学生答案序列化器"""
    sub_question_id = serializers.IntegerField(source='sub_question.id', read_only=True)
    sub_question_text = serializers.CharField(source='sub_question.question_text', read_only=True)
    
    class Meta:
        model = StudentAnswer
        fields = ['id', 'sub_question_id', 'sub_question_text', 'text', 'index', 
                  'type', 'score']
        read_only_fields = ['id', 'score']


class StudentPageRecordSerializer(serializers.ModelSerializer):
    """学生页面记录序列化器"""
    page_id = serializers.IntegerField(source='page.id', read_only=True)
    page_title = serializers.CharField(source='page.text', read_only=True)
    page_order = serializers.IntegerField(source='page.order', read_only=True)
    answers = StudentAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentPageRecord
        fields = ['id', 'page_id', 'page_title', 'page_order', 'submitted', 
                  'submitted_at', 'is_expired', 'remaining_time', 'late_score', 
                  'page_score', 'feedback', 'is_graded', 'answers']
        read_only_fields = ['id', 'submitted_at', 'is_graded', 'page_score', 'feedback']


class StudentMediaPlayRecordSerializer(serializers.ModelSerializer):
    """媒体播放记录序列化器"""
    main_question_id = serializers.IntegerField(source='main_question.id', read_only=True)
    media_material_id = serializers.IntegerField(source='media_material.id', read_only=True, allow_null=True)
    
    class Meta:
        model = StudentMediaPlayRecord
        fields = ['id', 'main_question_id', 'media_material_id', 'play_count', 'last_pause_time']
        read_only_fields = ['id']


class StudentExamRecordSerializer(serializers.ModelSerializer):
    """考试记录序列化器"""
    unit_id = serializers.IntegerField(source='exam.id', read_only=True)
    unit_name = serializers.CharField(source='exam.title', read_only=True)
    unit_type = serializers.CharField(source='exam.type', read_only=True)
    student_id = serializers.IntegerField(source='user.id', read_only=True)
    student_name = serializers.CharField(source='user.name', read_only=True)
    page_records = StudentPageRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentExamRecord
        fields = ['id', 'unit_id', 'unit_name', 'unit_type', 'student_id', 
                  'student_name', 'started_at', 'ended_at', 'finished_at', 
                  'submitted', 'integrity_score', 'score', 'page_records']
        read_only_fields = ['id', 'started_at', 'ended_at', 'finished_at', 'score']


class AnswerSaveSerializer(serializers.Serializer):
    """保存答案序列化器"""
    sub_question_id = serializers.IntegerField()
    text = serializers.CharField(required=False, allow_blank=True)
    index = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.CharField(required=False, allow_blank=True, max_length=50)


class PageAnswersSaveSerializer(serializers.Serializer):
    """保存页面答案序列化器"""
    answers = AnswerSaveSerializer(many=True)


class MediaPlayUpdateSerializer(serializers.Serializer):
    """更新媒体播放记录序列化器"""
    main_question_id = serializers.IntegerField()
    media_material_id = serializers.IntegerField(required=False, allow_null=True)
    play_count = serializers.IntegerField(required=False, min_value=0)
    last_pause_time = serializers.FloatField(required=False, min_value=0)











