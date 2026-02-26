# -*- coding: utf-8 -*-
"""
AI 提示请求 API，与 scoring_views 风格一致：Result.success/Result.error、IsAuthenticated。
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from common.api.response import Result
from AI_module.models import HintRequestLog
from AI_module.hint_service import HintService, LEVEL_DETAIL
from ELW.models import SubQuestion


@extend_schema(
    tags=['AI提示'],
    summary='请求提示',
    description='学生请求分级提示（1=轻提示 2=方向提示 3=详细解释），不泄露答案',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'sub_question_id': {'type': 'integer', 'description': '小题ID'},
                'level': {'type': 'integer', 'description': '提示级别 1/2/3'},
                'student_answer': {'type': 'string', 'description': '学生当前答案（可选）'},
                'transcript': {'type': 'string', 'description': '听力原文（可选）'},
                'context': {'type': 'object', 'description': '上下文 practice_id, page_id 等'},
            },
            'required': ['sub_question_id', 'level'],
        }
    },
    responses={
        200: {
            'description': '成功',
            'content': {
                'application/json': {
                    'example': {
                        'code': 200,
                        'message': 'success',
                        'data': {
                            'content': '提示内容',
                            'level': 1,
                            'log_id': 1,
                            'request_time': '2026-02-26 12:00:00',
                        }
                    }
                }
            }
        },
        400: {'description': '参数错误'},
        403: {'description': '仅学生可用'},
        404: {'description': '题目不存在'},
    },
)
class HintRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            sub_question_id = data.get('sub_question_id')
            level = data.get('level', 1)
            student_answer = data.get('student_answer', '')
            transcript = (data.get('transcript') or '').strip()
            context = data.get('context') or {}

            if not sub_question_id:
                return Result.error(message='缺少题目ID', code=400)

            try:
                question = SubQuestion.objects.select_related('main_question__media_material').get(id=sub_question_id)
            except SubQuestion.DoesNotExist:
                return Result.error(message='题目不存在', code=404)

            # 请求未传 transcript 时，从题目关联的媒体素材自动带出
            if not transcript and getattr(question.main_question, 'media_material', None):
                transcript = (question.main_question.media_material.transcript or '').strip()

            if not hasattr(request.user, 'students'):
                return Result.error(message='只有学生才能使用提示功能', code=403)

            student = request.user.students
            requested_level = max(1, min(3, int(level)))

            service = HintService(model='VolcEngine')
            max_allowed = service.get_max_allowed_level(student, sub_question_id)
            actual_level = min(requested_level, max_allowed)
            downgraded = requested_level > max_allowed

            result = service.get_hint(
                question=question,
                level=actual_level,
                student_answer=student_answer,
                transcript=transcript,
                context=context,
            )

            log = HintRequestLog.objects.create(
                student=student,
                sub_question=question,
                level=actual_level,
                hint_content=result['content'],
                context=context,
            )

            data = {
                'content': result['content'],
                'level': result['level'],
                'log_id': log.id,
                'request_time': log.request_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            data['requested_level'] = requested_level
            if downgraded:
                data['message'] = f'因消退机制，该题提示次数较多，本次已降级为级别 {actual_level}（轻提示=1，方向提示=2，详细解释=3）。'

            return Result.success(data=data, message='success')
        except Exception as e:
            import traceback
            print(f"HintRequest 错误: {e}\n{traceback.format_exc()}")
            return Result.error(message=f'请求提示失败: {str(e)}')


@extend_schema(
    tags=['AI提示'],
    summary='查询提示请求日志',
    description='学生本人或教师/研究用，按题目或时间查询提示使用记录',
    parameters=[
        {'name': 'sub_question_id', 'in': 'query', 'required': False, 'schema': {'type': 'integer'}},
        {'name': 'limit', 'in': 'query', 'required': False, 'schema': {'type': 'integer', 'default': 20}},
    ],
    responses={200: {'description': '成功，返回记录列表'}},
)
class HintLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not hasattr(request.user, 'students'):
                return Result.error(message='仅学生可查看本人提示记录', code=403)

            student = request.user.students
            sub_question_id = request.query_params.get('sub_question_id')
            limit = min(50, max(1, int(request.query_params.get('limit', 20))))

            qs = HintRequestLog.objects.filter(student=student).order_by('-request_time')[:limit]
            if sub_question_id:
                qs = qs.filter(sub_question_id=sub_question_id)

            records = [
                {
                    'id': r.id,
                    'sub_question_id': r.sub_question_id,
                    'level': r.level,
                    'hint_content': r.hint_content or '',
                    'request_time': r.request_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for r in qs
            ]
            return Result.success(data=records, message='success')
        except Exception as e:
            print(f"HintLog 错误: {e}")
            return Result.error(message=f'获取日志失败: {str(e)}')