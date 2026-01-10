"""
User management API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from Account.api.serializers import StudentSerializer, TeacherSerializer, ClassSerializer
from Account.api.create_serializers import (
    CourseCreateSerializer, TeacherCreateSerializer,
    ClassCreateSerializer, StudentCreateSerializer,
    StudentUpdateSerializer, TeacherUpdateSerializer
)
from Account.services.user_service_impl import UserServiceImpl
from Account.services.auth_service_impl import AuthServiceImpl
from Account.models import Course


@extend_schema(
    tags=['用户管理'],
    responses={200: StudentSerializer}
)
class StudentDetailView(APIView):
    """
    获取学生详细信息 API
    
    GET /api/v1/users/students/{student_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "username": "string",
            "name": "string",
            "seat_number": "string",
            "class_id": int,
            "class_name": "string"
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id):
        """获取学生详细信息"""
        student = UserServiceImpl.get_student_by_id(student_id)
        if not student:
            return Result.not_found(message='Student not found')
        
        serializer = StudentSerializer(student)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    responses={200: StudentSerializer}
)
class StudentListView(APIView):
    """
    获取学生列表 API
    
    GET /api/v1/users/students/
    
    Query Parameters:
    - class_id: 可选，按班级筛选
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "username": "string",
                "name": "string",
                "seat_number": "string",
                "class_id": int,
                "class_name": "string"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取学生列表"""
        class_id = request.query_params.get('class_id')
        
        if class_id:
            # 按班级筛选
            class_instance = UserServiceImpl.get_class_by_id(int(class_id))
            if not class_instance:
                return Result.not_found(message='Class not found')
            students = UserServiceImpl.get_students_by_class(class_instance)
        else:
            # 获取所有学生
            students = UserServiceImpl.get_all_students()
        
        serializer = StudentSerializer(students, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    responses={200: TeacherSerializer}
)
class TeacherDetailView(APIView):
    """
    获取教师详细信息 API
    
    GET /api/v1/users/teachers/{teacher_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "username": "string",
            "name": "string"
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, teacher_id):
        """获取教师详细信息"""
        teacher = UserServiceImpl.get_teacher_by_id(teacher_id)
        if not teacher:
            return Result.not_found(message='Teacher not found')
        
        serializer = TeacherSerializer(teacher)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    responses={200: TeacherSerializer}
)
class TeacherListView(APIView):
    """
    获取教师列表 API
    
    GET /api/v1/users/teachers/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "username": "string",
                "name": "string"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取教师列表"""
        from Account.models import Teachers
        teachers = Teachers.objects.all().order_by('id')
        serializer = TeacherSerializer(teachers, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    responses={200: ClassSerializer}
)
class ClassDetailView(APIView):
    """
    获取班级详细信息 API
    
    GET /api/v1/users/classes/{class_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": {
            "id": int,
            "class_name": "string",
            "teacher_id": int,
            "teacher_name": "string",
            "start_date": "string",
            "week": int,
            "start_time": "string",
            "end_time": "string",
            "course_name": "string"
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id):
        """获取班级详细信息"""
        class_instance = UserServiceImpl.get_class_by_id(class_id)
        if not class_instance:
            return Result.not_found(message='Class not found')
        
        serializer = ClassSerializer(class_instance)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    responses={200: ClassSerializer}
)
class ClassListView(APIView):
    """
    获取班级列表 API
    
    GET /api/v1/users/classes/
    
    Query Parameters:
    - teacher_id: 可选，按教师筛选
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "class_name": "string",
                "teacher_id": int,
                "teacher_name": "string",
                "start_date": "string",
                "week": int,
                "start_time": "string",
                "end_time": "string",
                "course_name": "string"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取班级列表"""
        teacher_id = request.query_params.get('teacher_id')
        
        if teacher_id:
            # 按教师筛选
            classes = UserServiceImpl.get_teacher_classes(int(teacher_id))
        else:
            # 获取所有班级
            from Account.models import Class
            classes = Class.objects.all().order_by('id')
        
        serializer = ClassSerializer(classes, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    responses={200: StudentSerializer}
)
class ClassStudentsView(APIView):
    """
    获取班级学生列表 API
    
    GET /api/v1/users/classes/{class_id}/students/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": int,
                "username": "string",
                "name": "string",
                "seat_number": "string",
                "class_id": int,
                "class_name": "string"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id):
        """获取班级学生列表"""
        class_instance = UserServiceImpl.get_class_by_id(class_id)
        if not class_instance:
            return Result.not_found(message='Class not found')
        
        students = UserServiceImpl.get_class_students(class_id)
        serializer = StudentSerializer(students, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(
    tags=['用户管理'],
    request=CourseCreateSerializer,
    responses={201: CourseCreateSerializer}
)
class CourseCreateView(APIView):
    """
    创建课程 API
    
    POST /api/v1/users/courses/create/
    
    Body:
    {
        "year": 2024,
        "grade": "1",
        "semester": "上"
    }
    """
    permission_classes = []  # 允许未认证访问，用于测试
    
    def post(self, request):
        """创建课程"""
        serializer = CourseCreateSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            return Result.created(data=CourseCreateSerializer(course).data, 
                                 message='Course created successfully')
        return Result.bad_request(message='Validation failed', 
                                 data=serializer.errors)


@extend_schema(
    tags=['用户管理'],
    request=TeacherCreateSerializer,
    responses={201: TeacherSerializer}
)
class TeacherCreateView(APIView):
    """
    创建教师 API
    
    POST /api/v1/users/teachers/create/
    
    Body:
    {
        "username": "teacher001",
        "name": "王老师",
        "password": "teacher123"
    }
    """
    permission_classes = []  # 允许未认证访问，用于测试
    
    def post(self, request):
        """创建教师"""
        serializer = TeacherCreateSerializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()
            return Result.created(data=TeacherSerializer(teacher).data, 
                                 message='Teacher created successfully')
        return Result.bad_request(message='Validation failed', 
                                 data=serializer.errors)


@extend_schema(
    tags=['用户管理'],
    request=ClassCreateSerializer,
    responses={201: ClassSerializer}
)
class ClassCreateView(APIView):
    """
    创建班级 API
    
    POST /api/v1/users/classes/create/
    
    Body:
    {
        "class_name": "英语听力1班",
        "course": 1,
        "teacher": 1,
        "start_date": "2024-01-01",
        "week": 1,
        "start_time": "08:00:00",
        "end_time": "10:00:00"
    }
    """
    permission_classes = []  # 允许未认证访问，用于测试
    
    def post(self, request):
        """创建班级"""
        serializer = ClassCreateSerializer(data=request.data)
        if serializer.is_valid():
            class_instance = serializer.save()
            return Result.created(data=ClassSerializer(class_instance).data, 
                                 message='Class created successfully')
        return Result.bad_request(message='Validation failed', 
                                 data=serializer.errors)


@extend_schema(
    tags=['用户管理'],
    request=StudentCreateSerializer,
    responses={201: StudentSerializer}
)
class StudentCreateView(APIView):
    """
    创建学生 API
    
    POST /api/v1/users/students/create/
    
    Body:
    {
        "username": "student001",
        "name": "张三",
        "password": "student123",
        "class_instance": 1,
        "seat_number": "1"
    }
    """
    permission_classes = []  # 允许未认证访问，用于测试
    
    def post(self, request):
        """创建学生"""
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Result.created(data=StudentSerializer(student).data,
                                 message='Student created successfully')
        return Result.bad_request(message='Validation failed',
                                 data=serializer.errors)


@extend_schema(
    tags=['用户管理'],
    request=StudentUpdateSerializer,
    responses={200: StudentSerializer}
)
class StudentUpdateView(APIView):
    """
    更新学生信息 API

    PUT/PATCH /api/v1/users/students/{student_id}/update/

    Body:
    {
        "name": "新姓名",
        "seat_number": "新座位号"
    }
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, student_id):
        """更新学生信息"""
        student = UserServiceImpl.get_student_by_id(student_id)
        if not student:
            return Result.not_found(message='Student not found')

        # 权限检查：只有学生本人可以更新自己的信息
        if request.user.username != student.username:
            return Result.forbidden(message='You can only update your own profile')

        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Result.success(data=StudentSerializer(student).data,
                                message='Student information updated successfully')
        return Result.bad_request(message='Validation failed',
                                 data=serializer.errors)

    def patch(self, request, student_id):
        """部分更新学生信息"""
        return self.put(request, student_id)


@extend_schema(
    tags=['用户管理'],
    request=TeacherUpdateSerializer,
    responses={200: TeacherSerializer}
)
class TeacherUpdateView(APIView):
    """
    更新教师信息 API

    PUT/PATCH /api/v1/users/teachers/{teacher_id}/update/

    Body:
    {
        "name": "新姓名"
    }
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, teacher_id):
        """更新教师信息"""
        teacher = UserServiceImpl.get_teacher_by_id(teacher_id)
        if not teacher:
            return Result.not_found(message='Teacher not found')

        # 权限检查：只有教师本人可以更新自己的信息
        if request.user.username != teacher.username:
            return Result.forbidden(message='You can only update your own profile')

        serializer = TeacherUpdateSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Result.success(data=TeacherSerializer(teacher).data,
                                message='Teacher information updated successfully')
        return Result.bad_request(message='Validation failed',
                                 data=serializer.errors)

    def patch(self, request, teacher_id):
        """部分更新教师信息"""
        return self.put(request, teacher_id)

