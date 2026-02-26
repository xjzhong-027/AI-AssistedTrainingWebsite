"""
Exam API views.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from accessment.api.serializers import (
    StudentExamRecordSerializer, StudentPageRecordSerializer, StudentAnswerSerializer,
    PageAnswersSaveSerializer, MediaPlayUpdateSerializer
)
from accessment.services.exam_service_impl import ExamServiceImpl
from Account.services.user_service_impl import UserServiceImpl
from ELW.services.content_service_impl import ContentServiceImpl


@extend_schema(tags=['考试'])
class ExamListView(APIView):
    """
    获取考试列表 API
    
    GET /api/v1/exams/
    
    Query Parameters:
    - student_id: 可选，按学生筛选
    - unit_type: 可选，按类型筛选（exam/practice）
    
    Headers:
    Authorization: Bearer <access_token>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取考试列表"""
        from accessment.models import StudentExamRecord
        from ELW.models import Unit
        
        student_id = request.query_params.get('student_id')
        unit_type = request.query_params.get('unit_type', 'exam')
        
        # 如果指定了学生ID，获取该学生的考试记录
        if student_id:
            records = ExamServiceImpl.get_exam_records_by_user(int(student_id))
            if unit_type:
                records = [r for r in records if r.exam.type == unit_type]
        else:
            # 获取当前用户的考试记录
            username = self._get_username(request)
            role = self._get_user_role(request)
            
            if role == 'student':
                student = UserServiceImpl.get_student_by_username(username)
                if student:
                    records = ExamServiceImpl.get_exam_records_by_user(student.id)
                    if unit_type:
                        records = [r for r in records if r.exam.type == unit_type]
                else:
                    records = []
            else:
                # 教师或管理员可以查看所有记录
                records = StudentExamRecord.objects.filter(exam__type=unit_type).order_by('-started_at')
        
        serializer = StudentExamRecordSerializer(records, many=True)
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


@extend_schema(tags=['考试'])
class ExamDetailView(APIView):
    """
    获取考试详情 API
    
    GET /api/v1/exams/{exam_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, exam_id):
        """获取考试详情"""
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'student':
            return Result.forbidden(message='Only students can view exam details')
        
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='Student not found')
        
        exam_record = ExamServiceImpl.get_exam_record(student.id, exam_id)
        if not exam_record:
            return Result.not_found(message='Exam record not found')
        
        serializer = StudentExamRecordSerializer(exam_record)
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


@extend_schema(tags=['考试'])
class ExamStartView(APIView):
    """
    开始考试 API
    
    POST /api/v1/exams/{exam_id}/start/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, exam_id):
        """开始考试"""
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'student':
            return Result.forbidden(message='Only students can start exams')
        
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='Student not found')
        
        # 检查单元是否存在
        unit = ContentServiceImpl.get_unit_by_id(exam_id)
        if not unit:
            return Result.not_found(message='Exam not found')
        
        # 获取或创建考试记录
        exam_record = ExamServiceImpl.get_exam_record(student.id, exam_id)
        if not exam_record:
            exam_record = ExamServiceImpl.create_exam_record(student.id, exam_id)
        
        serializer = StudentExamRecordSerializer(exam_record)
        return Result.success(data=serializer.data, message='Exam started successfully')
    
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


@extend_schema(tags=['考试'])
class ExamPageView(APIView):
    """
    获取考试页面 API
    
    GET /api/v1/exams/{exam_id}/pages/{page_order}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, exam_id, page_order):
        """获取考试页面"""
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'student':
            return Result.forbidden(message='Only students can view exam pages')
        
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='Student not found')
        
        # 获取考试记录
        exam_record = ExamServiceImpl.get_exam_record(student.id, exam_id)
        if not exam_record:
            return Result.not_found(message='Exam record not found')
        
        # 获取页面
        pages = ContentServiceImpl.get_pages_by_unit(exam_id)
        page = None
        for p in pages:
            if p.order == page_order:
                page = p
                break
        
        if not page:
            return Result.not_found(message='Page not found')
        
        # 获取或创建页面记录
        page_record = ExamServiceImpl.get_or_create_page_record(exam_record.id, page.id)
        
        serializer = StudentPageRecordSerializer(page_record)
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


@extend_schema(tags=['考试'])
class ExamPageAnswersSaveView(APIView):
    """
    保存页面答案 API
    
    POST /api/v1/exams/pages/{page_record_id}/answers/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, page_record_id):
        """保存页面答案"""
        serializer = PageAnswersSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        # 保存每个答案
        saved_answers = []
        for answer_data in serializer.validated_data['answers']:
            try:
                answer = ExamServiceImpl.save_answer(
                    student_page_record_id=page_record_id,
                    sub_question_id=answer_data['sub_question_id'],
                    answer_text=answer_data.get('text', ''),
                    is_correct=None
                )
                
                # 更新其他字段
                if 'index' in answer_data:
                    answer.index = answer_data['index']
                if 'type' in answer_data:
                    answer.type = answer_data['type']
                answer.save()
                
                saved_answers.append(answer)
            except Exception as e:
                return Result.error(message=f'Failed to save answer: {str(e)}', code=500)
        
        result_serializer = StudentAnswerSerializer(saved_answers, many=True)
        return Result.success(data=result_serializer.data, message='Answers saved successfully')


@extend_schema(tags=['考试'])
class ExamSubmitView(APIView):
    """
    提交考试 API
    
    POST /api/v1/exams/{exam_id}/submit/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, exam_id):
        """提交考试"""
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'student':
            return Result.forbidden(message='Only students can submit exams')
        
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='Student not found')
        
        exam_record = ExamServiceImpl.get_exam_record(student.id, exam_id)
        if not exam_record:
            return Result.not_found(message='Exam record not found')
        
        # 提交考试：先逐页批改（选择题等直接出分，主观题走 AI 异步评分），再标记已提交
        try:
            page_records = ExamServiceImpl.get_page_records_by_exam(exam_record.id)
            for pr in page_records:
                if not pr.is_graded:
                    ExamServiceImpl.grade_page(pr.id)
            ExamServiceImpl.submit_exam(exam_record.id)
            exam_record.refresh_from_db()
            
            serializer = StudentExamRecordSerializer(exam_record)
            return Result.success(data=serializer.data, message='Exam submitted successfully')
        except Exception as e:
            return Result.error(message=f'Failed to submit exam: {str(e)}', code=500)
    
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


@extend_schema(tags=['考试'])
class ExamResultView(APIView):
    """
    获取考试结果 API
    
    GET /api/v1/exams/{exam_id}/result/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, exam_id):
        """获取考试结果"""
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'student':
            return Result.forbidden(message='Only students can view exam results')
        
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='Student not found')
        
        exam_record = ExamServiceImpl.get_exam_record(student.id, exam_id)
        if not exam_record:
            return Result.not_found(message='Exam record not found')
        
        serializer = StudentExamRecordSerializer(exam_record)
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


@extend_schema(tags=['考试'])
class MediaPlayUpdateView(APIView):
    """
    更新媒体播放记录 API
    
    POST /api/v1/exams/{exam_id}/media-play/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, exam_id):
        """更新媒体播放记录"""
        serializer = MediaPlayUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Result.bad_request(message='Invalid data', data=serializer.errors)
        
        username = self._get_username(request)
        role = self._get_user_role(request)
        
        if role != 'student':
            return Result.forbidden(message='Only students can update media play records')
        
        student = UserServiceImpl.get_student_by_username(username)
        if not student:
            return Result.not_found(message='Student not found')
        
        exam_record = ExamServiceImpl.get_exam_record(student.id, exam_id)
        if not exam_record:
            return Result.not_found(message='Exam record not found')
        
        # 更新播放记录
        try:
            play_record = ExamServiceImpl.update_media_play_record(
                exam_record_id=exam_record.id,
                main_question_id=serializer.validated_data['main_question_id'],
                media_material_id=serializer.validated_data.get('media_material_id'),
                play_count=serializer.validated_data.get('play_count', 0),
                last_pause_time=serializer.validated_data.get('last_pause_time', 0)
            )
            
            from accessment.api.serializers import StudentMediaPlayRecordSerializer
            result_serializer = StudentMediaPlayRecordSerializer(play_record)
            return Result.success(data=result_serializer.data, message='Media play record updated successfully')
        except Exception as e:
            return Result.error(message=f'Failed to update media play record: {str(e)}', code=500)
    
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







