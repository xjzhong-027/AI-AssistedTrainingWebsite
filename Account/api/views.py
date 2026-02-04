"""
API views for Account (authentication).
"""
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from common.api.response import Result
from Account.api.serializers import CustomTokenObtainPairSerializer, UserInfoSerializer
from Account.api.create_serializers import ChangePasswordSerializer
from Account.services.auth_service_impl import AuthServiceImpl
from Account.services.user_service_impl import UserServiceImpl


@extend_schema(
    tags=['认证'],
    summary='用户登录',
    description='用户登录接口，支持学生、教师、管理员三种角色登录，返回 JWT Token',
    request=CustomTokenObtainPairSerializer,
    responses={
        200: {
            'description': '登录成功',
            'examples': {
                'application/json': {
                    'code': 200,
                    'message': 'success',
                    'data': {
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                        'username': 'student001',
                        'role': 'student',
                        'user_id': 1
                    }
                }
            }
        },
        401: {'description': '认证失败，用户名或密码错误'}
    },
    examples=[
        OpenApiExample(
            '学生登录',
            value={
                'username': 'student001',
                'password': 'student123',
                'role': 'student'
            }
        ),
        OpenApiExample(
            '教师登录',
            value={
                'username': 'teacher001',
                'password': 'teacher123',
                'role': 'teacher'
            }
        ),
    ]
)
class LoginView(TokenObtainPairView):
    """
    用户登录 API
    
    POST /api/v1/auth/login/
    
    Request Body:
    {
        "username": "string",
        "password": "string",
        "role": "student" | "teacher" | "admin"
    }
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "access": "string",
            "refresh": "string",
            "username": "string",
            "role": "string",
            "user_id": int
        }
    }
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        处理登录请求
        """
        # 获取角色（从请求体中）
        role = request.data.get('role')
        if not role:
            return Result.bad_request(message='Role is required')
        
        # 将角色添加到 serializer context
        serializer = self.get_serializer(
            data=request.data,
            context={'role': role, 'request': request}
        )
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Result.unauthorized(message=f'Authentication failed: {str(e)}')
        
        # 获取 token
        tokens = serializer.validated_data
        
        # 获取用户信息（学生/教师/管理员的 ID）
        username = request.data.get('username')
        custom_user_id = 0  # 初始化为 0，避免未定义错误
        
        # 从 serializer 的 validated_data 中获取用户信息
        # 由于我们在 validate 中已经验证了用户，这里可以直接获取
        if role == 'student':
            student = UserServiceImpl.get_student_by_username(username)
            custom_user_id = student.id if student else 0
        elif role == 'teacher':
            teacher = UserServiceImpl.get_teacher_by_username(username)
            custom_user_id = teacher.id if teacher else 0
        elif role == 'admin':
            from Account.models import Admins
            try:
                admin = Admins.objects.get(username=username)
                custom_user_id = admin.id
            except Admins.DoesNotExist:
                custom_user_id = 0
        
        # 创建登录记录
        try:
            AuthServiceImpl.create_login_record(username, role, request)
        except Exception as e:
            # 登录记录创建失败不影响登录流程
            print(f"Failed to create login record: {e}")
        
        # 返回响应
        response_data = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'username': username,
            'role': role,
            'user_id': custom_user_id
        }
        
        return Result.success(data=response_data, message='Login successful')


@extend_schema(
    tags=['认证'],
    summary='Token 获取（兼容接口）',
    description='JWT Token 获取接口（兼容旧版本），建议使用 /api/v1/auth/login/ 接口',
    deprecated=True
)
class TokenObtainPairViewWithTag(TokenObtainPairView):
    """
    Token 获取视图（带标签，兼容接口）
    
    POST /api/v1/auth/token/
    
    注意：此接口为兼容旧版本保留，建议使用 /api/v1/auth/login/ 接口
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=['认证'])
class RefreshTokenView(TokenRefreshView):
    """
    Token 刷新 API
    
    POST /api/v1/auth/token/refresh/
    
    Request Body:
    {
        "refresh": "string"
    }
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "access": "string"
        }
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        处理 Token 刷新请求
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Result.unauthorized(message=f'Token refresh failed: {str(e)}')
        
        return Result.success(
            data={'access': serializer.validated_data['access']},
            message='Token refreshed successfully'
        )


@extend_schema(
    tags=['认证'],
    operation_id='logout',
    summary='用户登出',
    description='用户登出接口，可选择性将 refresh token 加入黑名单',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh_token': {'type': 'string', 'description': 'Refresh Token（可选）'}
            }
        }
    },
    responses={
        200: {
            'description': '登出成功',
            'content': {
                'application/json': {
                    'example': {
                        'code': 200,
                        'message': 'Logout successful',
                        'data': None
                    }
                }
            }
        }
    }
)
class LogoutView(APIView):
    """
    用户登出 API

    POST /api/v1/auth/logout/

    Headers:
    Authorization: Bearer <access_token>

    Response:
    {
        "code": 200,
        "message": "Logout successful",
        "data": null
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        处理登出请求
        
        注意：IsAuthenticated 权限已经确保 request.user 是已认证的用户
        """
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # 将 token 加入黑名单
        except Exception as e:
            # 如果黑名单失败，不影响登出流程
            print(f"Failed to blacklist token: {e}")
        
        return Result.success(message='Logout successful')


@extend_schema(
    tags=['认证'],
    operation_id='get_current_user',
    summary='获取当前用户信息',
    description='从 JWT Token 中获取当前登录用户的基本信息',
    responses={
        200: {
            'description': '获取成功',
            'content': {
                'application/json': {
                    'example': {
                        'code': 200,
                        'message': 'success',
                        'data': {
                            'username': 'student001',
                            'role': 'student',
                            'user_id': 1
                        }
                    }
                }
            }
        },
        401: {'description': 'Token 无效或已过期'}
    }
)
class CurrentUserView(APIView):
    """
    获取当前用户信息 API

    GET /api/v1/auth/user/

    Headers:
    Authorization: Bearer <access_token>

    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "username": "string",
            "role": "string",
            "user_id": int
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取当前用户信息
        
        注意：IsAuthenticated 权限已经确保 request.user 是已认证的用户
        """
        # 从 JWT token 中获取用户信息
        # IsAuthenticated 权限已经确保 request.user 是已认证的用户
        user = request.user
        
        # 从 token payload 中获取角色信息
        # 注意：simplejwt 默认不将自定义字段添加到 request.user
        # 我们需要从 token 中解析
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                untyped_token = UntypedToken(token)
                token_payload = untyped_token.payload
                
                # 获取自定义 user_id（学生/教师/管理员的 ID）
                custom_user_id = 0
                role = token_payload.get('role', '')
                if role == 'student':
                    custom_user_id = token_payload.get('student_id', 0)
                elif role == 'teacher':
                    custom_user_id = token_payload.get('teacher_id', 0)
                elif role == 'admin':
                    custom_user_id = token_payload.get('admin_id', 0)
                
                user_data = {
                    'username': token_payload.get('username', user.username if hasattr(user, 'username') else ''),
                    'role': role,
                    'user_id': custom_user_id
                }
                
                return Result.success(data=user_data, message='success')
            except (InvalidToken, TokenError) as e:
                return Result.unauthorized(message=f'Invalid token: {str(e)}')
        
        # 如果无法从 token 获取，尝试从 session 获取（向后兼容）
        session_user = AuthServiceImpl.get_current_user(request)
        if session_user:
            return Result.success(data={
                'username': session_user['username'],
                'role': session_user['role'],
                'user_id': 0  # Session 中没有 user_id
            }, message='success')
        
        return Result.unauthorized(message='User information not found')


@extend_schema(
    tags=['认证'],
    request=ChangePasswordSerializer,
    responses={200: {'description': '密码修改成功'}}
)
class ChangePasswordView(APIView):
    """
    修改密码 API

    POST /api/v1/auth/change-password/

    Headers:
    Authorization: Bearer <access_token>

    Body:
    {
        "old_password": "string",
        "new_password": "string"
    }

    Response:
    {
        "code": 200,
        "message": "Password changed successfully",
        "data": null
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Result.bad_request(message='Validation failed',
                                     data=serializer.errors)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # 获取当前用户的角色和用户名
        user = request.user
        username = user.username

        # 从 JWT token 中获取角色信息
        from rest_framework_simplejwt.tokens import UntypedToken
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Result.unauthorized(message='No valid authorization token provided')

        token = auth_header.split(' ')[1]
        try:
            untyped_token = UntypedToken(token)
            token_payload = untyped_token.payload
            role = token_payload.get('role', '')
        except Exception as e:
            return Result.unauthorized(message=f'Invalid token: {str(e)}')

        # 根据角色验证旧密码并更新新密码
        if role == 'student':
            from Account.models import Students
            try:
                student = Students.objects.get(username=username)
                # 验证旧密码
                if student.password != old_password:
                    return Result.bad_request(message='Old password is incorrect')
                # 更新密码
                student.password = new_password
                student.save()
            except Students.DoesNotExist:
                return Result.not_found(message='Student not found')

        elif role == 'teacher':
            from Account.models import Teachers
            try:
                teacher = Teachers.objects.get(username=username)
                # 验证旧密码
                if teacher.password != old_password:
                    return Result.bad_request(message='Old password is incorrect')
                # 更新密码
                teacher.password = new_password
                teacher.save()
            except Teachers.DoesNotExist:
                return Result.not_found(message='Teacher not found')

        elif role == 'admin':
            from Account.models import Admins
            try:
                admin = Admins.objects.get(username=username)
                # 验证旧密码
                if admin.password != old_password:
                    return Result.bad_request(message='Old password is incorrect')
                # 更新密码
                admin.password = new_password
                admin.save()
            except Admins.DoesNotExist:
                return Result.not_found(message='Admin not found')
        else:
            return Result.bad_request(message='Invalid role')

        return Result.success(message='Password changed successfully')

