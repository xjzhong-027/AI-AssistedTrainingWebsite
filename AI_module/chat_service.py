"""
AI 聊天服务（火山引擎）

提供用户消息 → AI 回复的对话能力，供前端 AIWindow 等组件调用。
"""
import os
from typing import Optional

from .Get_from_VolcEngine import Get_from_VolcEngine


# 环境变量配置（与项目现有 VolcEngine 配置一致）
# 保持你当前项目使用的 endpoint_id 默认值
VOLCENGINE_API_KEY = os.getenv("VOLCENGINE_API_KEY", os.getenv("USER_AI_API_KEY", ""))
VOLCENGINE_ENDPOINT_ID = os.getenv("VOLCENGINE_ENDPOINT_ID", "ep-20260316000236-ck7h7")


class ChatService:
    """AI 聊天服务，使用火山引擎生成回复"""

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        key = api_key or VOLCENGINE_API_KEY or ""
        ep = endpoint_id or VOLCENGINE_ENDPOINT_ID or ""
        self._client = Get_from_VolcEngine(api_key=key, endpoint_id=ep)

    def get_reply(self, message: str, context: Optional[dict] = None) -> str:
        """
        发送用户消息，获取 AI 回复

        Args:
            message: 用户消息内容
            context: 可选上下文（practice_id, page_id, sub_question_id, learning_data 等）

        Returns:
            AI 回复文本
        """
        message = (message or "").strip()
        if not message:
            raise ValueError("消息内容不能为空")

        # 系统提示：引导模型利用学习数据做个性化分析
        system_prompt = '''You are an AI learning assistant integrated into an English Listening Practice System.

IMPORTANT: You have access to the student's actual learning data, including practice results, exam results, and incorrect answers. When a student asks about their learning situation or mistakes, you MUST use this data to provide specific, personalized analysis. Do NOT say you don't have access to their data.

Your role is to help students analyze their listening practice and exam performance, understand their mistakes, and improve their listening skills through guided discussion.

You have access to the student's learning context, which includes:
- Listening practice results (practice name, score, date, duration)
- Exam results (exam name, score, date, duration)
- Incorrect answers (question text, student answer, correct answer, date)
- Learning trajectory (progress over time)
- Listening transcripts
- Student responses
- Question types (multiple choice, short answer, summarization)

Your responsibilities include:

1. Learning Situation Analysis
When a student asks a question or discusses a listening task, first identify whether they are referring to:
- Practice exercises
- Exam results
- Incorrect answers
- Listening comprehension difficulties

Then briefly summarize the student's learning situation using the actual data provided, before giving advice.

2. Error Analysis with Actual Data
When analyzing mistakes, use the specific incorrect answers from the learning data:
- Identify which questions the student got wrong
- Compare the student's answer with the correct answer
- Explain why the correct answer is right and why the student's answer was wrong
- Help them understand the specific concepts or vocabulary they missed

3. Guided Discussion
Encourage the student to think and explain their reasoning. Instead of immediately giving the answer, ask guiding questions such as:
- "What part of the audio was difficult for you?"
- "Why did you choose that option?"
- "Which words in the transcript helped you decide?"

4. Explanation and Feedback
Provide clear explanations based on the listening transcript and question logic. Explain:
- why the correct answer is correct
- why other options are wrong
- how the student could identify the correct answer in the audio

5. Learning Suggestions
Provide practical strategies for improving listening skills, such as:
- focusing on keywords
- predicting information
- listening for signal words
- improving vocabulary recognition

6. Communication Style
Use clear and simple English appropriate for college English learners.
Be supportive, patient, and encouraging.

Avoid overly technical explanations.

7. Response Strategy
- If the user greets you (e.g., "你好", "hello", "hi"), respond with a friendly greeting first, then offer to help with their learning.
- If the user asks about their learning situation, exam results, or specific questions, ALWAYS use the learning data to provide a detailed, personalized analysis. Never say you don't have access to their data.
- If the user asks about specific practice or exam (e.g., "Alice in wonderland这个练习"), find the matching practice in the learning data and analyze their performance on that specific practice.
- If the user asks about mistakes or wrong answers, list their actual incorrect answers from the learning data and explain each one.
- If the user asks non-learning related questions, respond appropriately but gently guide them back to learning topics.

Your goal is not only to give answers but to help the student understand their learning problems and develop better listening strategies. Always base your analysis on the actual learning data provided.'''

        # 组装 Prompt：系统提示 + 上下文 + 用户消息
        prompt_parts = [system_prompt]
        if context:
            ctx_parts = []
            if context.get("practice_id"):
                ctx_parts.append(f'[练习ID: {context["practice_id"]}]')
            if context.get("page_id"):
                ctx_parts.append(f'[页面ID: {context["page_id"]}]')
            if context.get("sub_question_id"):
                ctx_parts.append(f'[题目ID: {context["sub_question_id"]}]')

            # 学习数据（练习结果、考试结果、错题等）
            learning_data = context.get("learning_data")
            if learning_data:
                ctx_parts.append("\n[学习数据]")
                if learning_data.get("practice_results"):
                    ctx_parts.append(f'\n练习结果: {len(learning_data["practice_results"])}次练习')
                    for i, practice in enumerate(learning_data["practice_results"]):
                        ctx_parts.append(f'\n  练习{i+1}: {practice.get("name", "")}')
                        ctx_parts.append(f'  得分: {practice.get("score", "")}')
                        ctx_parts.append(f'  日期: {practice.get("date", "")}')
                        ctx_parts.append(f'  时长: {practice.get("duration", "")}分钟')
                if learning_data.get("exam_results"):
                    ctx_parts.append(f'\n考试结果: {len(learning_data["exam_results"])}次考试')
                    for i, exam in enumerate(learning_data["exam_results"]):
                        ctx_parts.append(f'\n  考试{i+1}: {exam.get("name", "")}')
                        ctx_parts.append(f'  得分: {exam.get("score", "")}')
                        ctx_parts.append(f'  日期: {exam.get("date", "")}')
                        ctx_parts.append(f'  时长: {exam.get("duration", "")}分钟')
                if learning_data.get("incorrect_answers"):
                    ctx_parts.append(f'\n错题: {len(learning_data["incorrect_answers"])}道')
                    for i, error in enumerate(learning_data["incorrect_answers"]):
                        ctx_parts.append(f'\n  错题{i+1}: {error.get("question_text", "")}')
                        ctx_parts.append(f'  学生答案: {error.get("student_answer", "")}')
                        ctx_parts.append(f'  正确答案: {error.get("correct_answer", "")}')
                        ctx_parts.append(f'  日期: {error.get("date", "")}')
                if learning_data.get("learning_trajectory"):
                    ctx_parts.append(f'\n学习轨迹: {len(learning_data["learning_trajectory"])}个数据点')
                    for i, point in enumerate(learning_data["learning_trajectory"]):
                        ctx_parts.append(f'\n  日期: {point.get("date", "")}, 得分: {point.get("score", "")}')

            if ctx_parts:
                prompt_parts.append("\n" + " ".join(ctx_parts))

        # 添加用户消息
        prompt_parts.append("\n[用户消息]\n" + message)
        prompt = "".join(prompt_parts)

        return self._client.get_msg(prompt)
