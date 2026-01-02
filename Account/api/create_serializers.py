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
        fields = ['year', 'grade', 'semester']


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







