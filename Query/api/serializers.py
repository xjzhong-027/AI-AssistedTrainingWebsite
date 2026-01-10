"""
Serializers for Query API.
"""
from rest_framework import serializers
from Account.models import Attendance, ClassScheduleAdjustment, ClassScheduleAddition
from Query.models import ClassroomLayout, OverdueDeductionRule, OverduePeriod
from accessment.models import StudentExamRecord, StudentPageRecord, StudentAnswer


class AttendanceSerializer(serializers.ModelSerializer):
    """考勤记录序列化器"""
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = ['id', 'student_id', 'student_name', 'student_username', 
                  'week', 'status', 'status_display']
        read_only_fields = ['id']
    
    def get_status_display(self, obj):
        """获取状态显示文本"""
        status_choices = dict(Attendance._meta.get_field('status').choices)
        return status_choices.get(obj.status, '未知状态')


class ClassScheduleAdjustmentSerializer(serializers.ModelSerializer):
    """调课记录序列化器"""
    class_id = serializers.IntegerField(source='class_instance.id', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_name', read_only=True)
    
    class Meta:
        model = ClassScheduleAdjustment
        fields = ['id', 'class_id', 'class_name', 'week', 'new_week_day', 
                  'new_class_begin_time', 'new_class_end_time']
        read_only_fields = ['id']


class ClassScheduleAdditionSerializer(serializers.ModelSerializer):
    """补课记录序列化器"""
    class_id = serializers.IntegerField(source='class_instance.id', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_name', read_only=True)
    
    class Meta:
        model = ClassScheduleAddition
        fields = ['id', 'class_id', 'class_name', 'week', 'weekday', 
                  'class_begin_time', 'class_end_time']
        read_only_fields = ['id']


class ClassroomLayoutSerializer(serializers.ModelSerializer):
    """教室布局序列化器"""
    class_id = serializers.IntegerField(source='class_instance.id', read_only=True)
    class_name = serializers.CharField(source='class_instance.class_name', read_only=True)
    
    class Meta:
        model = ClassroomLayout
        fields = ['id', 'class_id', 'class_name', 'seat_rows', 'seat_cols']
        read_only_fields = ['id']


class OverduePeriodSerializer(serializers.ModelSerializer):
    """逾期时间段序列化器"""
    
    class Meta:
        model = OverduePeriod
        fields = ['id', 'period_name', 'min_days', 'max_days', 'deduction_rate', 'description']
        read_only_fields = ['id']


class OverdueDeductionRuleSerializer(serializers.ModelSerializer):
    """逾期扣分规则序列化器"""
    periods = OverduePeriodSerializer(many=True, read_only=True)
    
    class Meta:
        model = OverdueDeductionRule
        fields = ['id', 'rule_name', 'description', 'is_active', 'is_default', 
                  'created_at', 'updated_at', 'periods']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentLearningRecordSerializer(serializers.Serializer):
    """学生学习记录序列化器"""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_username = serializers.CharField()
    unit_id = serializers.IntegerField()
    unit_name = serializers.CharField()
    unit_type = serializers.CharField()
    started_at = serializers.DateTimeField()
    submitted = serializers.BooleanField()
    score = serializers.DecimalField(max_digits=5, decimal_places=1, allow_null=True)
    integrity_score = serializers.DecimalField(max_digits=2, decimal_places=1)
    late_score = serializers.DecimalField(max_digits=2, decimal_places=1)


class ClassStatisticSerializer(serializers.Serializer):
    """班级统计序列化器"""
    class_id = serializers.IntegerField()
    class_name = serializers.CharField()
    total_students = serializers.IntegerField()
    total_units = serializers.IntegerField()
    completed_units = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=1, allow_null=True)


class UnitStatisticSerializer(serializers.Serializer):
    """单元统计序列化器"""
    unit_id = serializers.IntegerField()
    unit_name = serializers.CharField()
    unit_type = serializers.CharField()
    total_students = serializers.IntegerField()
    completed_students = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=1, allow_null=True)
    completion_rate = serializers.FloatField()











