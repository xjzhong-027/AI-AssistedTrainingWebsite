"""
Serializers for ELW (content) API.
"""
from rest_framework import serializers
from ELW.models import (
    MediaMaterial, MainQuestion, SubQuestion, Unit, PaperPage,
    ChoiceOption, MatchingOption, Correction
)


class MediaMaterialSerializer(serializers.ModelSerializer):
    """媒体素材序列化器"""
    
    class Meta:
        model = MediaMaterial
        fields = ['id', 'title', 'theme', 'abstract', 'keywords', 'transcript', 
                  'media_url', 'image_url']
        read_only_fields = ['id']


class ChoiceOptionSerializer(serializers.ModelSerializer):
    """选择题选项序列化器"""
    
    class Meta:
        model = ChoiceOption
        fields = ['id', 'option_label', 'option_content', 'image_url', 'is_answer']
        read_only_fields = ['id']


class MatchingOptionSerializer(serializers.ModelSerializer):
    """连线题选项序列化器"""
    
    class Meta:
        model = MatchingOption
        fields = ['id', 'option_label', 'option_content', 'image_url']
        read_only_fields = ['id']


class CorrectionSerializer(serializers.ModelSerializer):
    """改错题选项序列化器"""
    
    class Meta:
        model = Correction
        fields = ['id', 'type', 'index']
        read_only_fields = ['id']


class SubQuestionSerializer(serializers.ModelSerializer):
    """小题序列化器"""
    options = ChoiceOptionSerializer(many=True, read_only=True)  # related_name='options'
    matchingOptions = MatchingOptionSerializer(many=True, read_only=True)  # related_name='matchingOptions'
    corrections = CorrectionSerializer(many=True, read_only=True)
    question_type = serializers.CharField(source='main_question.question_type', read_only=True)
    
    class Meta:
        model = SubQuestion
        fields = ['id', 'question_text', 'answer', 'score', 'question_type',
                  'image_url', 'tips', 'analysis', 'options', 'matchingOptions', 'corrections']
        read_only_fields = ['id']


class MainQuestionSerializer(serializers.ModelSerializer):
    """大题序列化器"""
    sub_questions = SubQuestionSerializer(many=True, read_only=True)
    media_material_id = serializers.IntegerField(source='media_material.id', read_only=True)
    media_material_title = serializers.CharField(source='media_material.title', read_only=True)
    media_material_url = serializers.CharField(source='media_material.media_url', read_only=True, allow_null=True)
    
    class Meta:
        model = MainQuestion
        fields = ['id', 'question_text', 'question_type', 'image_url', 'media_material_id', 
                  'media_material_title', 'media_material_url', 'maximum_play', 'minimum_play', 'start_time', 
                  'end_time', 'allow_pause', 'limited_time', 'no_media', 'sub_questions', 'created_at']
        read_only_fields = ['id', 'created_at']


class PaperPageSerializer(serializers.ModelSerializer):
    """试卷页面序列化器"""
    unit_id = serializers.IntegerField(source='unit.id', read_only=True)
    unit_name = serializers.CharField(source='unit.title', read_only=True)
    main_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = PaperPage
        fields = ['id', 'order', 'text', 'limited_time', 'can_modify', 'unit_id', 'unit_name', 
                  'main_questions', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_main_questions(self, obj):
        """获取页面的大题列表"""
        from ELW.models import PageMainQuestion
        page_main_questions = PageMainQuestion.objects.filter(page=obj).select_related('main_question')
        main_questions = [pmq.main_question for pmq in page_main_questions]
        serializer = MainQuestionSerializer(main_questions, many=True)
        return serializer.data


class UnitSerializer(serializers.ModelSerializer):
    """单元序列化器"""
    class_id = serializers.IntegerField(source='class_instance.id', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_name', read_only=True)
    pages = PaperPageSerializer(many=True, read_only=True, source='paper_pages')
    week = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ['id', 'title', 'type', 'order', 'class_id', 'class_name', 'pages', 'week', 'status']
        read_only_fields = ['id']

    def get_week(self, obj):
        """获取周次信息"""
        from ELW.models import TimeManagement
        time_mgmt = TimeManagement.objects.filter(unit=obj).first()
        return time_mgmt.week if time_mgmt else None

    def get_status(self, obj):
        """获取任务状态"""
        from ELW.models import TimeManagement
        from datetime import datetime, date

        time_mgmt = TimeManagement.objects.filter(unit=obj).first()
        if not time_mgmt:
            return '未设置'

        if time_mgmt.exam_date:
            today = date.today()
            if time_mgmt.exam_date > today:
                return '未开始'
            elif time_mgmt.exam_date == today:
                return '进行中'
            else:
                return '已结束'

        return '已发布'

