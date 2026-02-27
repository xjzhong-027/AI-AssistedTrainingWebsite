from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from AI_module.models import AIScoreRecord, AIExplanationRecord, AIConversationHistory
from AI_module.scoring_service import AIScoringService
from AI_module.chat_service import ChatService
from Account.models import Students
from ELW.models import SubQuestion
from common.api.response import Result
import json


class AIScoringView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            sub_question_id = data.get('sub_question_id')
            student_answer = data.get('student_answer', '')
            transcript = data.get('transcript', '')

            if not sub_question_id:
                return Result.error(message='缺少题目ID')

            try:
                question = SubQuestion.objects.get(id=sub_question_id)
            except SubQuestion.DoesNotExist:
                return Result.error(message='题目不存在')

            if not hasattr(request.user, 'students'):
                return Result.error(message='只有学生才能使用AI评分功能')

            student = request.user.students

            scoring_service = AIScoringService()
            result = scoring_service.score_subjective_answer(
                question=question,
                student_answer=student_answer,
                transcript=transcript
            )

            score_record = AIScoreRecord.objects.create(
                student=student,
                sub_question=question,
                content_accuracy=result['content_accuracy'],
                language_expression=result['language_expression'],
                completeness=result['completeness'],
                logical_coherence=result['logical_coherence'],
                total_score=result['total_score'],
                feedback=result['feedback'],
                suggestions=result['suggestions'],
                grammar_errors=result['grammar_errors'],
                vocabulary_suggestions=result['vocabulary_suggestions'],
                student_answer=student_answer,
                ai_model=scoring_service.ai_client.get_AI_module_name()
            )

            return Result.success(data={
                'score_id': score_record.id,
                'content_accuracy': score_record.content_accuracy,
                'language_expression': score_record.language_expression,
                'completeness': score_record.completeness,
                'logical_coherence': score_record.logical_coherence,
                'total_score': score_record.total_score,
                'feedback': score_record.feedback,
                'suggestions': score_record.suggestions,
                'grammar_errors': score_record.grammar_errors,
                'vocabulary_suggestions': score_record.vocabulary_suggestions,
                'score_time': score_record.score_time.strftime('%Y-%m-%d %H:%M:%S')
            }, message='AI评分完成')

        except Exception as e:
            import traceback
            print(f"AI评分接口错误: {e}")
            print(f"错误堆栈: {traceback.format_exc()}")
            return Result.error(message=f'AI评分失败: {str(e)}')


class AIExplanationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            sub_question_id = data.get('sub_question_id')
            transcript = data.get('transcript', '')

            if not sub_question_id:
                return Result.error(message='缺少题目ID')

            try:
                question = SubQuestion.objects.get(id=sub_question_id)
            except SubQuestion.DoesNotExist:
                return Result.error(message='题目不存在')

            scoring_service = AIScoringService()
            result = scoring_service.generate_explanation(
                question=question,
                transcript=transcript
            )

            explanation_record = AIExplanationRecord.objects.create(
                sub_question=question,
                correct_answer_explanation=result['correct_answer_explanation'],
                distractor_analysis=result['distractor_analysis'],
                key_points=result['key_points'],
                listening_tips=result['listening_tips'],
                related_knowledge=result.get('related_knowledge', ''),
                ai_model=scoring_service.ai_client.get_AI_module_name()
            )

            return Result.success(data={
                'explanation_id': explanation_record.id,
                'correct_answer_explanation': explanation_record.correct_answer_explanation,
                'distractor_analysis': explanation_record.distractor_analysis,
                'key_points': explanation_record.key_points,
                'listening_tips': explanation_record.listening_tips,
                'related_knowledge': explanation_record.related_knowledge,
                'generate_time': explanation_record.generate_time.strftime('%Y-%m-%d %H:%M:%S')
            }, message='解释生成完成')

        except Exception as e:
            print(f"AI解释接口错误: {e}")
            return Result.error(message=f'解释生成失败: {str(e)}')


class AIScoreHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not hasattr(request.user, 'students'):
                return Result.error(message='只有学生才能查看评分历史')

            student = request.user.students
            sub_question_id = request.query_params.get('sub_question_id')

            queryset = AIScoreRecord.objects.filter(student=student)

            if sub_question_id:
                queryset = queryset.filter(sub_question_id=sub_question_id)

            queryset = queryset.order_by('-score_time')[:10]

            records = []
            for record in queryset:
                records.append({
                    'score_id': record.id,
                    'sub_question_id': record.sub_question.id,
                    'question_text': record.sub_question.question_text,
                    'total_score': record.total_score,
                    'feedback': record.feedback,
                    'score_time': record.score_time.strftime('%Y-%m-%d %H:%M:%S')
                })

            return Result.success(data=records, message='获取评分历史成功')

        except Exception as e:
            print(f"获取评分历史错误: {e}")
            return Result.error(message=f'获取评分历史失败: {str(e)}')


class AIConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not hasattr(request.user, 'students'):
                return Result.error(message='只有学生才能查看对话历史')

            student = request.user.students
            context_id = request.query_params.get('context_id')

            queryset = AIConversationHistory.objects.filter(student=student)

            if context_id:
                queryset = queryset.filter(context__context_id=context_id)

            queryset = queryset.order_by('message_time')[:50]

            messages = []
            for msg in queryset:
                messages.append({
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'context': msg.context,
                    'message_time': msg.message_time.strftime('%Y-%m-%d %H:%M:%S')
                })

            return Result.success(data=messages, message='获取对话历史成功')

        except Exception as e:
            print(f"获取对话历史错误: {e}")
            return Result.error(message=f'获取对话历史失败: {str(e)}')

    def post(self, request):
        try:
            data = request.data
            role = data.get('role', 'user')
            content = data.get('content', '')
            context = data.get('context', {})

            if not content:
                return Result.error(message='消息内容不能为空')

            if not hasattr(request.user, 'students'):
                return Result.error(message='只有学生才能发送对话消息')

            student = request.user.students

            conversation = AIConversationHistory.objects.create(
                student=student,
                role=role,
                content=content,
                context=context,
                ai_model='VolcEngine'
            )

            return Result.success(data={
                'id': conversation.id,
                'role': conversation.role,
                'content': conversation.content,
                'message_time': conversation.message_time.strftime('%Y-%m-%d %H:%M:%S')
            }, message='保存对话消息成功')

        except Exception as e:
            print(f"保存对话消息错误: {e}")
            return Result.error(message=f'保存对话消息失败: {str(e)}')


class AIChatReplyView(APIView):
    """
    AI 聊天回复接口（调用火山引擎生成回复）

    POST /api/v1/scoring/chat/
    请求: { "message": "用户消息", "context": { "practice_id": 1, "page_id": 2, "sub_question_id": 3 } }
    响应: { "reply": "AI回复", "timestamp": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            message = request.data.get('message', '').strip()
            if not message:
                return Result.error(message='消息内容不能为空')

            context = request.data.get('context', {}) or {}

            chat_service = ChatService()
            reply = chat_service.get_reply(message=message, context=context)

            return Result.success(data={
                'reply': reply,
                'timestamp': datetime.now().isoformat()
            }, message='success')
        except ValueError as e:
            return Result.error(message=str(e), code=400)
        except Exception as e:
            print(f"AI聊天接口错误: {e}")
            return Result.error(message=f'AI回复失败: {str(e)}', code=500)
