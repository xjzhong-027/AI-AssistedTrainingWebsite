import json
import threading
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from AI_module.question_generation_service import QuestionGenerationService
from ELW.models import MediaMaterial, MainQuestion, SubQuestion, ChoiceOption
from common.api.response import Result


class AIQuestionGenerateView(APIView):
    """AI自动出题接口 - 异步版本"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            material_id = data.get('material_id')
            question_type = data.get('question_type', 'choice')
            difficulty = data.get('difficulty', 'medium')
            count = data.get('count', 3)
            focus_points = data.get('focus_points', [])
            additional_requirements = data.get('additional_requirements', '')

            if not material_id:
                return Result.error(message='缺少素材ID')

            try:
                material = MediaMaterial.objects.get(id=material_id)
            except MediaMaterial.DoesNotExist:
                return Result.error(message='素材不存在')

            if not hasattr(request.user, 'teachers'):
                return Result.error(message='只有教师才能使用AI出题功能')

            transcript = material.transcript

            if not transcript:
                return Result.error(message='该素材没有听力原文，无法生成题目')

            service = QuestionGenerationService()
            task_id = service.create_task()

            thread = threading.Thread(
                target=service.generate_questions_async,
                args=(task_id, transcript, question_type, difficulty, count, focus_points, additional_requirements)
            )
            thread.daemon = True
            thread.start()

            return Result.success(data={
                'task_id': task_id,
                'status': 'pending',
                'message': '任务已提交，请轮询查询状态'
            }, message='任务已创建')

        except Exception as e:
            import traceback
            print(f"AI出题接口错误: {e}")
            print(f"错误堆栈: {traceback.format_exc()}")
            return Result.error(message=f'AI出题失败: {str(e)}')


class AIQuestionStatusView(APIView):
    """查询AI出题任务状态"""
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            task_status = QuestionGenerationService.get_task_status(task_id)

            if not task_status:
                return Result.error(message='任务不存在')

            response_data = {
                'task_id': task_id,
                'status': task_status.get('status'),
                'message': task_status.get('message', ''),
                'questions': task_status.get('questions', []),
            }

            if task_status.get('suggestions'):
                response_data['suggestions'] = task_status['suggestions']

            if task_status.get('conversation_history'):
                response_data['conversation_history'] = task_status['conversation_history']

            return Result.success(data=response_data)

        except Exception as e:
            print(f"查询任务状态错误: {e}")
            return Result.error(message=f'查询失败: {str(e)}')


class AIQuestionChatView(APIView):
    """AI出题多轮对话接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            material_id = data.get('material_id')
            message = data.get('message', '')
            current_questions = data.get('current_questions', [])
            conversation_history = data.get('conversation_history', [])

            if not material_id:
                return Result.error(message='缺少素材ID')

            if not message:
                return Result.error(message='消息内容不能为空')

            try:
                material = MediaMaterial.objects.get(id=material_id)
            except MediaMaterial.DoesNotExist:
                return Result.error(message='素材不存在')

            transcript = material.transcript

            if not transcript:
                return Result.error(message='该素材没有听力原文')

            service = QuestionGenerationService()
            result = service.chat_revise(
                message=message,
                transcript=transcript,
                current_questions=current_questions,
                conversation_history=conversation_history
            )

            if result['success']:
                return Result.success(data={
                    'questions': result['questions'],
                    'conversation_history': result.get('conversation_history', [])
                }, message='修订成功')
            else:
                return Result.error(
                    message=result.get('message', '修订失败'),
                    data={'suggestions': result.get('suggestions', [])}
                )

        except Exception as e:
            import traceback
            print(f"AI出题对话接口错误: {e}")
            print(f"错误堆栈: {traceback.format_exc()}")
            return Result.error(message=f'对话失败: {str(e)}')


class AIQuestionApplyView(APIView):
    """应用AI生成的题目到题库"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            material_id = data.get('material_id')
            questions_to_apply = data.get('questions', [])

            if not material_id:
                return Result.error(message='缺少素材ID')

            if not questions_to_apply:
                return Result.error(message='没有要应用的题目')

            try:
                material = MediaMaterial.objects.get(id=material_id)
            except MediaMaterial.DoesNotExist:
                return Result.error(message='素材不存在')

            if not hasattr(request.user, 'teachers'):
                return Result.error(message='只有教师才能添加题目')

            applied_questions = []

            for q in questions_to_apply:
                main_q_data = q.get('main_question', {})
                question_type = main_q_data.get('question_type', 'choice')

                main_question = MainQuestion.objects.create(
                    media_material=material,
                    question_type=question_type,
                    question_text=main_q_data.get('question_text', '')
                )

                for sq_data in q.get('sub_questions', []):
                    answer = self._get_answer_from_sub_question(sq_data, question_type)

                    sub_question = SubQuestion.objects.create(
                        main_question=main_question,
                        question_text=sq_data.get('question_text', ''),
                        answer=answer,
                        analysis=sq_data.get('analysis', ''),
                        score=sq_data.get('score', 2.0)
                    )

                    if question_type == 'choice' and 'options' in sq_data:
                        options = sq_data['options']
                        correct_answer = sq_data.get('correct_answer', 'A')

                        for opt_label, opt_content in options.items():
                            if opt_content:
                                ChoiceOption.objects.create(
                                    sub_question=sub_question,
                                    option_label=opt_label,
                                    option_content=opt_content,
                                    is_answer=(opt_label == correct_answer)
                                )

                    applied_questions.append({
                        'main_question_id': main_question.id,
                        'sub_question_ids': [sub_question.id]
                    })

            return Result.success(data={
                'applied_questions': applied_questions,
                'total_count': len(applied_questions)
            }, message=f'已成功添加 {len(applied_questions)} 道题目到题库')

        except Exception as e:
            import traceback
            print(f"应用题目接口错误: {e}")
            print(f"错误堆栈: {traceback.format_exc()}")
            return Result.error(message=f'应用题目失败: {str(e)}')

    def _get_answer_from_sub_question(self, sq_data, question_type):
        """从小题数据中提取答案"""
        if question_type == 'choice':
            return sq_data.get('correct_answer', 'A')
        elif 'answer' in sq_data:
            return sq_data['answer']
        elif 'reference_answer' in sq_data:
            return sq_data['reference_answer']
        elif 'correct_matching' in sq_data:
            return json.dumps(sq_data['correct_matching'])
        return ''

