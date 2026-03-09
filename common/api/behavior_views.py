"""
行为统计与查询 API 视图。
"""
import datetime

from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from Account.services.user_service_impl import UserServiceImpl


@extend_schema(tags=['行为统计'])
class StudentBehaviorSummaryView(APIView):
    """
    当前学生的行为统计概览。

    GET /api/v1/behavior/student/summary/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='获取当前学生的行为统计概览',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_exams': {'type': 'integer'},
                    'completed_exams': {'type': 'integer'},
                    'total_practices': {'type': 'integer'},
                    'completed_practices': {'type': 'integer'},
                    'total_media_plays': {'type': 'integer'},
                    'hint_count': {'type': 'integer'},
                    'login_count_last_7_days': {'type': 'integer'},
                },
            }
        },
    )
    def get(self, request):
        """获取当前登录学生的行为统计概览。"""
        from accessment.models import StudentExamRecord, StudentMediaPlayRecord
        from AI_module.models import HintRequestLog
        from Account.models import LoginInfo

        username = self._get_username(request)
        role = self._get_user_role(request)

        if role != 'student':
            return Result.forbidden(message='仅学生可以查看个人行为统计')

        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='学生不存在')

        exam_qs = StudentExamRecord.objects.filter(user=student)

        total_exams = exam_qs.filter(exam__type='exam').count()
        completed_exams = exam_qs.filter(exam__type='exam', submitted=True).count()

        total_practices = exam_qs.filter(exam__type='practice').count()
        completed_practices = exam_qs.filter(exam__type='practice', submitted=True).count()

        media_qs = StudentMediaPlayRecord.objects.filter(student_exam_record__user=student)
        total_media_plays = media_qs.aggregate(total=Sum('play_count'))['total'] or 0

        hint_count = HintRequestLog.objects.filter(student=student).count()

        now = timezone.now()
        seven_days_ago = now - datetime.timedelta(days=7)
        login_count_last_7_days = LoginInfo.objects.filter(
            username=student.username,
            action='login',
            action_time__gte=seven_days_ago,
        ).count()

        data = {
            'total_exams': total_exams,
            'completed_exams': completed_exams,
            'total_practices': total_practices,
            'completed_practices': completed_practices,
            'total_media_plays': total_media_plays,
            'hint_count': hint_count,
            'login_count_last_7_days': login_count_last_7_days,
        }
        return Result.success(data=data, message='success')

    def _get_user_role(self, request) -> str:
        """从 JWT token 中获取用户角色。"""
        from rest_framework_simplejwt.tokens import UntypedToken

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except Exception:
                pass
        return ''

    def _get_username(self, request) -> str:
        """从 JWT token 中获取用户名。"""
        from rest_framework_simplejwt.tokens import UntypedToken

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('username', '')
            except Exception:
                pass
        return ''


@extend_schema(tags=['行为统计'])
class ClassBehaviorSummaryView(APIView):
    """
    教师端按班级查看学生行为统计。

    GET /api/v1/behavior/teacher/class-summary/?class_id=1
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='获取指定班级下每个学生的行为统计',
        parameters=[
            {
                'name': 'class_id',
                'in': 'query',
                'required': True,
                'schema': {'type': 'integer'},
                'description': '班级ID',
            }
        ],
    )
    def get(self, request):
        """获取指定班级下每个学生的行为统计。"""
        from accessment.models import StudentExamRecord, StudentMediaPlayRecord
        from AI_module.models import HintRequestLog
        from Account.models import Class, Students

        role = self._get_user_role(request)
        if role not in ('teacher', 'admin', 'TEACHER', 'ADMIN'):
            return Result.forbidden(message='仅教师或管理员可以查看班级行为统计')

        class_id = request.query_params.get('class_id')
        if not class_id:
            return Result.invalid(message='缺少 class_id 参数')

        try:
            class_id = int(class_id)
        except ValueError:
            return Result.invalid(message='class_id 参数必须是整数')

        cls = Class.objects.filter(id=class_id).first()
        if not cls:
            return Result.not_found(message='班级不存在')

        students = Students.objects.filter(class_instance=cls).all()
        student_stats = []

        for stu in students:
            exam_qs = StudentExamRecord.objects.filter(user=stu)
            total_exams = exam_qs.filter(exam__type='exam').count()
            completed_exams = exam_qs.filter(exam__type='exam', submitted=True).count()
            total_practices = exam_qs.filter(exam__type='practice').count()
            completed_practices = exam_qs.filter(exam__type='practice', submitted=True).count()

            media_qs = StudentMediaPlayRecord.objects.filter(student_exam_record__user=stu)
            total_media_plays = media_qs.aggregate(total=Sum('play_count'))['total'] or 0

            hint_count = HintRequestLog.objects.filter(student=stu).count()

            student_stats.append(
                {
                    'student_id': stu.id,
                    'student_username': stu.username,
                    'student_name': stu.name,
                    'total_exams': total_exams,
                    'completed_exams': completed_exams,
                    'total_practices': total_practices,
                    'completed_practices': completed_practices,
                    'total_media_plays': total_media_plays,
                    'hint_count': hint_count,
                }
            )

        data = {
            'class_id': cls.id,
            'class_name': cls.class_name,
            'students': student_stats,
        }
        return Result.success(data=data, message='success')

    def _get_user_role(self, request) -> str:
        """从 JWT token 中获取用户角色。"""
        from rest_framework_simplejwt.tokens import UntypedToken

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except Exception:
                pass
        return ''

