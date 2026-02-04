"""
Serializers for creating users, classes, and courses.
"""
from rest_framework import serializers
from Account.models import Students, Teachers, Admins, Class, Course
from django.contrib.auth.models import User


class CourseCreateSerializer(serializers.ModelSerializer):
    """课程创建序列化器"""
    
    class Meta:
        model = Course
        fields = ['id', 'year', 'grade', 'semester']
        read_only_fields = ['id']


class CourseSerializer(serializers.ModelSerializer):
    """课程列表/详情序列化器（只读）"""
    
    class Meta:
        model = Course
        fields = ['id', 'year', 'grade', 'semester']
        read_only_fields = ['id', 'year', 'grade', 'semester']


class TeacherCreateSerializer(serializers.ModelSerializer):
    """教师创建序列化器"""
    
    class Meta:
        model = Teachers
        fields = ['username', 'name', 'password']
    
    def create(self, validated_data):
        """创建教师并关联 Django User"""
        teacher = Teachers.objects.create(**validated_data)
        
        # 创建或获取 Django User
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'is_active': True}
        )
        teacher.user = user
        teacher.save()
        
        return teacher


class ClassCreateSerializer(serializers.ModelSerializer):
    """班级创建序列化器"""
    
    class Meta:
        model = Class
        fields = ['class_name', 'course', 'teacher', 'start_date', 'week', 
                  'start_time', 'end_time']


class ClassUpdateSerializer(serializers.ModelSerializer):
    """班级更新序列化器（部分更新）"""
    
    class Meta:
        model = Class
        fields = ['class_name', 'course', 'teacher', 'start_date', 'week', 
                  'start_time', 'end_time']
        extra_kwargs = {f: {'required': False} for f in ['class_name', 'course', 'teacher', 'start_date', 'week', 'start_time', 'end_time']}


class StudentCreateSerializer(serializers.ModelSerializer):
    """学生创建序列化器"""
    
    class Meta:
        model = Students
        fields = ['username', 'name', 'password', 'class_instance', 'seat_number']
    
    def create(self, validated_data):
        """创建学生并关联 Django User"""
        student = Students.objects.create(**validated_data)
        
        # 创建或获取 Django User
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'is_active': True}
        )
        student.user = user
        student.save()

        return student


class StudentUpdateSerializer(serializers.ModelSerializer):
    """学生更新序列化器"""

    class Meta:
        model = Students
        fields = ['name', 'seat_number']

    def update(self, instance, validated_data):
        """更新学生信息"""
        instance.name = validated_data.get('name', instance.name)
        instance.seat_number = validated_data.get('seat_number', instance.seat_number)
        instance.save()
        return instance


class TeacherUpdateSerializer(serializers.ModelSerializer):
    """教师更新序列化器"""

    class Meta:
        model = Teachers
        fields = ['name']

    def update(self, instance, validated_data):
        """更新教师信息"""
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """验证旧密码"""
        if not value:
            raise serializers.ValidationError("旧密码不能为空")
        return value

    def validate_new_password(self, value):
        """验证新密码"""
        if not value:
            raise serializers.ValidationError("新密码不能为空")
        if len(value) < 6:
            raise serializers.ValidationError("新密码长度至少为6位")
        return value











