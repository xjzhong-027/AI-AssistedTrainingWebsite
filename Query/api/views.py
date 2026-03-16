"""
Query API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken
from django.db.models import Avg, Count, Q
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from Query.api.serializers import (
    AttendanceSerializer, ClassScheduleAdjustmentSerializer, ClassScheduleAdditionSerializer,
    ClassroomLayoutSerializer, OverdueDeductionRuleSerializer, OverduePeriodSerializer,
    StudentLearningRecordSerializer, ClassStatisticSerializer, UnitStatisticSerializer
)
from Account.services.user_service_impl import UserServiceImpl
from Account.models import Attendance, ClassScheduleAdjustment, ClassScheduleAddition
from Query.models import ClassroomLayout, OverdueDeductionRule, OverduePeriod
from accessment.models import StudentExamRecord
from accessment.services.exam_service_impl import ExamServiceImpl
from ELW.models import Unit


@extend_schema(tags=['数据查询'])
class AttendanceQueryView(APIView):
    """
    考勤查询 API
    
    GET /api/v1/query/attendance/
    
    Query Parameters:
    - class_id: 班级ID（必需）
    - week: 周次（必需）
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """查询考勤记录"""
        class_id = request.query_params.get('class_id')
        week = request.query_params.get('week')
        
        if not class_id or not week:
            return Result.bad_request(message='class_id and week are required')
        
        # 验证班级权限
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        role_lower = (role or '').lower()
        if role_lower not in ('teacher', 'admin'):
            return Result.forbidden(message='仅教师或管理员可查询考勤')

        if role_lower == 'admin':
            pass
        else:
            teacher = UserServiceImpl.get_teacher_by_username(username)
            if not teacher:
                return Result.not_found(message='Teacher not found')
            classes = UserServiceImpl.get_teacher_classes(teacher.id)
            class_instance = UserServiceImpl.get_class_by_id(int(class_id))
            if not class_instance or class_instance not in classes:
                return Result.forbidden(message='No permission to access this class')
        
        # 获取班级学生
        students = UserServiceImpl.get_class_students(int(class_id))
        
        # 查询考勤记录
        attendances = []
        for student in students:
            student_attendances = Attendance.objects.filter(student=student, week=int(week))
            attendances.extend(student_attendances)
        
        serializer = AttendanceSerializer(attendances, many=True)
        return Result.success(data=serializer.data, message='success')
    
    def _get_user_role(self, request):
        """从 token 中获取用户角色"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except:
                pass
        return ''
    
    def _get_username(self, request):
        """从 token 中获取用户名"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('username', '')
            except:
                pass
        return ''


@extend_schema(tags=['数据查询'])
class StudentLearningRecordView(APIView):
    """
    学生学习记录查询 API
    
    GET /api/v1/query/learning-records/
    
    Query Parameters:
    - student_id: 可选，学生ID
    - class_id: 可选，班级ID
    - unit_type: 可选，单元类型（exam/practice）
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """查询学生学习记录"""
        student_id = request.query_params.get('student_id')
        class_id = request.query_params.get('class_id')
        unit_type = request.query_params.get('unit_type')
        
        # 获取用户信息
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        role_lower = (role or '').lower()
        if role_lower == 'student':
            # 学生只能查看自己的记录
            student = UserServiceImpl.get_student_by_username(username)
            if not student:
                return Result.not_found(message='Student not found')
            records = ExamServiceImpl.get_student_exam_records_by_user(student.id)
        elif role_lower in ('teacher', 'admin'):
            # 教师可以查看指定学生或班级的记录
            if student_id:
                records = ExamServiceImpl.get_student_exam_records_by_user(int(student_id))
            elif class_id:
                students = UserServiceImpl.get_class_students(int(class_id))
                records = []
                for student in students:
                    student_records = ExamServiceImpl.get_student_exam_records_by_user(student.id)
                    records.extend(student_records)
            else:
                return Result.bad_request(message='student_id or class_id is required for teachers')
        else:
            return Result.forbidden(message='Invalid role')
        
        # 按类型筛选
        if unit_type:
            records = [r for r in records if r.exam.type == unit_type]
        
        # 转换为序列化数据
        data = []
        for record in records:
            data.append({
                'student_id': record.user.id,
                'student_name': record.user.name,
                'student_username': record.user.username,
                'unit_id': record.exam.id,
                'unit_name': record.exam.title,
                'unit_type': record.exam.type,
                'started_at': record.started_at,
                'submitted': record.submitted,
                'score': record.score,
                'total_score': 100,
                'completion_time': record.finished_at or record.ended_at,
                'integrity_score': record.integrity_score,
                'late_score': 1.0
            })
        return Result.success(data=data, message='success')
    
    def _get_user_role(self, request):
        """从 token 中获取用户角色"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('role', '')
            except:
                pass
        return ''
    
    def _get_username(self, request):
        """从 token 中获取用户名"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                untyped_token = UntypedToken(token)
                return untyped_token.payload.get('username', '')
            except:
                pass
        return ''


@extend_schema(tags=['数据查询'])
class ClassStatisticView(APIView):
    """
    班级统计 API
    
    GET /api/v1/query/statistics/class/{class_id}/
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, class_id):
        """获取班级统计"""
        class_instance = UserServiceImpl.get_class_by_id(class_id)
        if not class_instance:
            return Result.not_found(message='Class not found')
        
        # 获取学生数量
        students = UserServiceImpl.get_class_students(class_id)
        total_students = len(students)
        
        # 获取单元数量
        from ELW.services.content_service_impl import ContentServiceImpl
        units = ContentServiceImpl.get_units_by_class(class_id)
        total_units = len(units)
        
        # 计算完成情况
        from accessment.services.exam_service_impl import ExamServiceImpl
        completed_units = 0
        total_score = 0
        score_count = 0
        
        for unit in units:
            unit_completed = False
            for student in students:
                record = ExamServiceImpl.get_exam_record(student.id, unit.id)
                if record and record.submitted:
                    unit_completed = True
                    if record.score is not None:
                        total_score += float(record.score)
                        score_count += 1
                    break
            if unit_completed:
                completed_units += 1
        
        average_score = total_score / score_count if score_count > 0 else None
        
        completion_rate = (completed_units / total_units * 100) if total_units > 0 else 0
        exam_count = sum(1 for u in units if u.type == 'exam')
        practice_count = sum(1 for u in units if u.type == 'practice')

        data = {
            'class_id': class_instance.id,
            'class_name': class_instance.class_name,
            'total_students': total_students,
            'completed_students': completed_units,
            'completion_rate': round(completion_rate, 1),
            'average_score': round(average_score, 1) if average_score is not None else None,
            'exam_count': exam_count,
            'practice_count': practice_count
        }
        return Result.success(data=data, message='success')


@extend_schema(tags=['数据查询'])
class UnitStatisticView(APIView):
    """
    单元统计 API
    
    GET /api/v1/query/statistics/unit/{unit_id}/
    
    Query Parameters:
    - class_id: 可选，班级ID（用于筛选学生）
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, unit_id):
        """获取单元统计"""
        from ELW.services.content_service_impl import ContentServiceImpl
        from accessment.services.exam_service_impl import ExamServiceImpl
        
        unit = ContentServiceImpl.get_unit_by_id(unit_id)
        if not unit:
            return Result.not_found(message='Unit not found')
        
        class_id = request.query_params.get('class_id')
        
        # 获取学生列表
        if class_id:
            students = UserServiceImpl.get_class_students(int(class_id))
        else:
            # 如果没有指定班级，获取单元所属班级的学生
            if unit.class_instance:
                students = UserServiceImpl.get_class_students(unit.class_instance.id)
            else:
                students = []
        
        total_students = len(students)
        completed_students = 0
        total_score = 0
        score_count = 0
        
        for student in students:
            record = ExamServiceImpl.get_exam_record(student.id, unit_id)
            if record and record.submitted:
                completed_students += 1
                if record.score is not None:
                    total_score += float(record.score)
                    score_count += 1
        
        average_score = total_score / score_count if score_count > 0 else None
        completion_rate = completed_students / total_students if total_students > 0 else 0
        
        highest_score = None
        lowest_score = None
        if score_count > 0:
            scores = []
            for student in students:
                record = ExamServiceImpl.get_exam_record(student.id, unit_id)
                if record and record.submitted and record.score is not None:
                    scores.append(float(record.score))
            if scores:
                highest_score = max(scores)
                lowest_score = min(scores)

        data = {
            'unit_id': unit.id,
            'unit_name': unit.title,
            'unit_type': unit.type,
            'total_students': total_students,
            'completed_students': completed_students,
            'average_score': round(average_score, 1) if average_score is not None else None,
            'completion_rate': round(completion_rate * 100, 1),
            'highest_score': highest_score,
            'lowest_score': lowest_score
        }
        return Result.success(data=data, message='success')


@extend_schema(tags=['数据查询'])
class OverdueRuleListView(APIView):
    """
    获取逾期扣分规则列表 API
    
    GET /api/v1/query/overdue-rules/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取逾期扣分规则列表"""
        rules = OverdueDeductionRule.objects.all().order_by('-is_default', '-created_at')
        serializer = OverdueDeductionRuleSerializer(rules, many=True)
        return Result.success(data=serializer.data, message='success')


@extend_schema(tags=['数据查询'])
class OverdueRuleDetailView(APIView):
    """
    获取逾期扣分规则详情 API
    
    GET /api/v1/query/overdue-rules/{rule_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, rule_id):
        """获取逾期扣分规则详情"""
        try:
            rule = OverdueDeductionRule.objects.get(id=rule_id)
        except OverdueDeductionRule.DoesNotExist:
            return Result.not_found(message='Overdue rule not found')
        
        serializer = OverdueDeductionRuleSerializer(rule)
        return Result.success(data=serializer.data, message='success')

