"""
Serializers for Account API.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_field
from Account.models import Students, Teachers, Admins, Class
from Account.services.user_service_impl import UserServiceImpl


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义 JWT Token 序列化器，添加用户角色信息。
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # 注意：不要覆盖 token['user_id']，因为 JWT 认证需要使用 Django User 的 ID
        # token['user_id'] 应该保持为 Django User 的 ID（由 super().get_token(user) 设置）
        
        # 添加用户角色信息到 token
        # 查找用户是学生、教师还是管理员
        username = user.username if hasattr(user, 'username') else None
        if not username:
            return token
        
        # 检查是否是学生
        student = UserServiceImpl.get_student_by_username(username)
        if student:
            token['role'] = 'student'
            token['student_id'] = student.id  # 使用不同的 claim 名称
            token['username'] = username
            return token
        
        # 检查是否是教师
        teacher = UserServiceImpl.get_teacher_by_username(username)
        if teacher:
            token['role'] = 'teacher'
            token['teacher_id'] = teacher.id  # 使用不同的 claim 名称
            token['username'] = username
            return token
        
        # 检查是否是管理员
        try:
            admin = Admins.objects.get(username=username)
            token['role'] = 'admin'
            token['admin_id'] = admin.id  # 使用不同的 claim 名称
            token['username'] = username
        except Admins.DoesNotExist:
            pass
        
        return token
    
    def validate(self, attrs):
        """
        验证用户凭据并返回 token。
        
        注意：这里需要根据实际的认证逻辑来验证。
        由于当前系统使用自定义的认证方式（不是 Django User），
        我们需要重写验证逻辑。
        """
        # 获取角色和用户名密码
        role = self.context.get('role')
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not role:
            raise serializers.ValidationError('Role is required')
        
        # 使用 AuthService 进行认证
        from Account.services.auth_service_impl import AuthServiceImpl
        from django.contrib.auth.models import User
        
        auth_result = None
        if role == 'student':
            auth_result = AuthServiceImpl.authenticate_student(username, password)
        elif role == 'teacher':
            auth_result = AuthServiceImpl.authenticate_teacher(username, password)
        elif role == 'admin':
            auth_result = AuthServiceImpl.authenticate_admin(username, password)
        else:
            raise serializers.ValidationError('Invalid role')
        
        if not auth_result:
            raise serializers.ValidationError('Invalid username or password')
        
        # 获取用户对象（Django User）
        user = None
        if role == 'student':
            student = auth_result['student']
            user = student.user
            # 如果 user 不存在，创建一个
            if not user:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_active': True}
                )
                student.user = user
                student.save()
        elif role == 'teacher':
            teacher = auth_result['teacher']
            user = teacher.user
            # 如果 user 不存在，创建一个
            if not user:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_active': True}
                )
                teacher.user = user
                teacher.save()
        elif role == 'admin':
            admin = auth_result.get('admin')
            if admin:
                user = admin.user
                # 如果 user 不存在，创建一个
                if not user:
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={'is_active': True, 'is_staff': True, 'is_superuser': True}
                    )
                    admin.user = user
                    admin.save()
        
        if not user:
            raise serializers.ValidationError('User object not found or could not be created')
        
        # 使用 Django User 生成 token
        refresh = self.get_token(user)
        
        # 添加角色信息到 token（已经在 get_token 中添加了，这里确保一下）
        refresh['role'] = role
        refresh['username'] = username
        
        # 注意：不要覆盖 refresh['user_id']，因为 JWT 认证需要使用 Django User 的 ID
        # refresh['user_id'] 应该保持为 Django User 的 ID（由 get_token 设置）
        
        # 获取自定义 user_id（学生/教师/管理员的 ID）
        custom_user_id = 0
        if role == 'student':
            custom_user_id = auth_result['student'].id
            refresh['student_id'] = custom_user_id
        elif role == 'teacher':
            custom_user_id = auth_result['teacher'].id
            refresh['teacher_id'] = custom_user_id
        elif role == 'admin' and auth_result.get('admin'):
            custom_user_id = auth_result['admin'].id
            refresh['admin_id'] = custom_user_id
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return data


class UserInfoSerializer(serializers.Serializer):
    """用户信息序列化器"""
    username = serializers.CharField()
    role = serializers.CharField()
    user_id = serializers.IntegerField()
    
    def to_representation(self, instance):
        """将用户信息转换为字典"""
        if isinstance(instance, dict):
            return instance
        
        # 如果 instance 是 token payload
        return {
            'username': instance.get('username', ''),
            'role': instance.get('role', ''),
            'user_id': instance.get('user_id', 0)
        }


class StudentSerializer(serializers.ModelSerializer):
    """学生序列化器"""
    class_name = serializers.CharField(source='class_instance.class_name', read_only=True)
    class_id = serializers.IntegerField(source='class_instance.id', read_only=True)
    
    class Meta:
        model = Students
        fields = ['id', 'username', 'name', 'seat_number', 'class_id', 'class_name']
        read_only_fields = ['id', 'username']


class TeacherSerializer(serializers.ModelSerializer):
    """教师序列化器"""
    
    class Meta:
        model = Teachers
        fields = ['id', 'username', 'name']
        read_only_fields = ['id', 'username']


class ClassSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    teacher_id = serializers.IntegerField(source='teacher.id', read_only=True)
    course_id = serializers.IntegerField(source='course.id', read_only=True, allow_null=True)
    course_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id', 'class_name', 'teacher_id', 'teacher_name', 'course_id', 'course_name',
                  'start_date', 'week', 'start_time', 'end_time']
        read_only_fields = ['id']
    
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_course_name(self, obj) -> str:
        """获取课程名称"""
        if obj.course:
            return f"{obj.course.year}-{obj.course.grade}-{obj.course.semester}"
        return None

