"""
API views for Account (authentication).
"""
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status

from common.api.response import Result
from Account.api.serializers import CustomTokenObtainPairSerializer, UserInfoSerializer
from Account.services.auth_service_impl import AuthServiceImpl
from Account.services.user_service_impl import UserServiceImpl


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

