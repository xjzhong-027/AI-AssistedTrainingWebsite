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
        return _get_user_role(request)

    def _get_username(self, request) -> str:
        return _get_username(request)


def _get_user_role(request) -> str:
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


def _get_username(request) -> str:
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
        return _get_user_role(request)


@extend_schema(tags=['行为统计'])
class StudentBehaviorScoreView(APIView):
    """
    学生个人行为评分（BSA-IFM 周度评分）。

    GET /api/v1/behavior/student/score/?period_start=2026-03-01
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='获取当前学生的周度行为评分',
        parameters=[
            {
                'name': 'period_start',
                'in': 'query',
                'required': False,
                'schema': {'type': 'string', 'format': 'date'},
                'description': '周期开始日期 YYYY-MM-DD，默认最新周期',
            }
        ],
    )
    def get(self, request):
        """获取当前登录学生的周度行为评分。"""
        from common.models import StudentBehaviorWeeklyScore
        from common.utils.date_utils import parse_period_param

        role = _get_user_role(request)
        if role != 'student':
            return Result.forbidden(message='仅学生可以查看个人行为评分')

        student = UserServiceImpl.get_student_by_username(_get_username(request))
        if not student:
            return Result.not_found(message='学生不存在')

        period_str = request.query_params.get('period_start')
        if period_str:
            try:
                period_start, period_end = parse_period_param(period_str)
            except ValueError:
                return Result.invalid(message='period_start 格式应为 YYYY-MM-DD')
        else:
            record = StudentBehaviorWeeklyScore.objects.filter(
                student=student
            ).order_by('-period_start').first()
            if not record:
                return Result.success(data=None, message='暂无周度评分数据')
            period_start = record.period_start
            period_end = record.period_end

        record = StudentBehaviorWeeklyScore.objects.filter(
            student=student,
            period_start=period_start,
        ).first()
        if not record:
            return Result.success(data=None, message='该周暂无评分数据')

        feedback = _simple_feedback(float(record.F_score or 0))

        data = {
            'student_id': student.id,
            'period': {'start': str(period_start), 'end': str(period_end)},
            'dimensions': {
                'S_A': float(record.S_A or 0),
                'S_B': float(record.S_B or 0),
                'S_C': float(record.S_C or 0),
                'S_D': float(record.S_D or 0),
            },
            'F_score': float(record.F_score or 0),
            'P_score': float(record.P_score or 0),
            'growth_bonus': record.growth_bonus or 0,
            'feedback': feedback,
        }
        return Result.success(data=data, message='success')


def _simple_feedback(f_score: float) -> str:
    """根据 F 分生成简单反馈。"""
    if f_score >= 85:
        return '您的学习投入与专注度较高，继续保持。'
    if f_score >= 70:
        return '您的学习投入与专注度尚可，建议回顾错题并增加练习。'
    if f_score >= 60:
        return '您的学习投入有待提高，建议按时出勤、完成练习并减少过快作答。'
    return '您的学习投入较低，建议加强出勤、完成练习并合理使用提示。'


@extend_schema(tags=['行为统计'])
class ClassBehaviorRankingView(APIView):
    """
    班级行为评分排名。

    GET /api/v1/behavior/class/ranking/?class_id=1&period_start=2026-03-01
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='获取指定班级的行为评分排名',
        parameters=[
            {'name': 'class_id', 'in': 'query', 'required': True, 'schema': {'type': 'integer'}},
            {'name': 'period_start', 'in': 'query', 'required': False, 'schema': {'type': 'string', 'format': 'date'}},
        ],
    )
    def get(self, request):
        """获取指定班级的行为评分排名。"""
        from common.models import StudentBehaviorWeeklyScore
        from Account.models import Class, Students
        from common.utils.date_utils import parse_period_param
        from datetime import date

        role = _get_user_role(request)
        if role not in ('teacher', 'admin', 'TEACHER', 'ADMIN'):
            return Result.forbidden(message='仅教师或管理员可以查看班级排名')

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

        period_str = request.query_params.get('period_start')
        if period_str:
            try:
                period_start, _ = parse_period_param(period_str)
            except ValueError:
                return Result.invalid(message='period_start 格式应为 YYYY-MM-DD')
        else:
            latest = StudentBehaviorWeeklyScore.objects.order_by('-period_start').first()
            if latest:
                period_start = latest.period_start
            else:
                from common.utils.date_utils import get_week_period
                period_start, _ = get_week_period(date.today())

        student_ids = list(Students.objects.filter(class_instance=cls).values_list('id', flat=True))
        records = StudentBehaviorWeeklyScore.objects.filter(
            student_id__in=student_ids,
            period_start=period_start,
        ).select_related('student').order_by('-F_score')

        ranking = []
        for rank, rec in enumerate(records, 1):
            ranking.append({
                'student_id': rec.student_id,
                'name': rec.student.name,
                'F_score': float(rec.F_score or 0),
                'rank': rank,
            })

        data = {
            'class_id': class_id,
            'period_start': str(period_start),
            'ranking': ranking,
        }
        return Result.success(data=data, message='success')


@extend_schema(tags=['行为统计'])
class CalculateWeeklyScoresView(APIView):
    """
    教师端触发周度行为评分计算。

    POST /api/v1/behavior/calculate-weekly/
    参数：period_start（可选，YYYY-MM-DD，默认本周一）
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='计算指定周的学生行为评分',
        request={
            'application/json': {
                'type': 'object',
                'properties': {'period_start': {'type': 'string', 'format': 'date'}},
            }
        },
    )
    def post(self, request):
        """教师或管理员触发周度评分计算。"""
        from common.utils.date_utils import parse_period_param, get_week_period
        from common.services.weekly_behavior_job import calculate_weekly_behavior_scores
        from datetime import date

        role = _get_user_role(request)
        if role not in ('teacher', 'admin', 'TEACHER', 'ADMIN'):
            return Result.forbidden(message='仅教师或管理员可以执行此操作')

        period_str = request.data.get('period_start') or request.query_params.get('period_start')
        if period_str:
            try:
                period_start, period_end = parse_period_param(
                    period_str if isinstance(period_str, str) else str(period_str)
                )
            except ValueError:
                return Result.invalid(message='period_start 格式应为 YYYY-MM-DD')
        else:
            period_start, period_end = get_week_period(date.today())

        count = calculate_weekly_behavior_scores(period_start)
        return Result.success(
            data={
                'period_start': str(period_start),
                'period_end': str(period_end),
                'updated_count': count,
            },
            message=f'成功计算 {period_start} ~ {period_end} 周度评分，更新 {count} 条记录'
        )

