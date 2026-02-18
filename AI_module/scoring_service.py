import json
import re
from AI_module.Get_from_AI import Get_from_AI


class AIScoringService:
    def __init__(self, model='VolcEngine'):
        self.ai_client = Get_from_AI(model=model)

    def score_subjective_answer(self, question, student_answer, transcript=None):
        """
        评分主观题答案

        Args:
            question: SubQuestion对象
            student_answer: 学生答案
            transcript: 听力原文（可选）

        Returns:
            评分结果字典
        """
        if not student_answer or not student_answer.strip():
            return self._get_empty_answer_result()

        question_type = question.main_question.question_type if hasattr(question, 'main_question') else 'text'

        prompt = self._build_scoring_prompt(
            question_type=question_type,
            question_text=question.question_text,
            transcript=transcript,
            reference_answer=question.answer,
            student_answer=student_answer
        )

        try:
            response = self.ai_client.get_answer(prompt)
            print(f"AI原始响应: {response[:500]}...")  # 打印前500字符
            result = self._parse_scoring_response(response)

            result['total_score'] = (
                result['content_accuracy'] * 0.4 +
                result['language_expression'] * 0.3 +
                result['completeness'] * 0.2 +
                result['logical_coherence'] * 0.1
            )

            return result
        except Exception as e:
            import traceback
            print(f"AI评分失败: {e}")
            print(f"错误堆栈: {traceback.format_exc()}")
            return self._get_fallback_result(student_answer)

    def generate_explanation(self, question, transcript=None):
        """
        生成客观题解释

        Args:
            question: SubQuestion对象
            transcript: 听力原文（可选）

        Returns:
            解释结果字典
        """
        question_type = question.main_question.question_type if hasattr(question, 'main_question') else 'text'
        options = question.options if hasattr(question, 'options') else None

        prompt = self._build_explanation_prompt(
            question_type=question_type,
            question_text=question.question_text,
            options=options,
            correct_answer=question.answer,
            transcript=transcript
        )

        try:
            response = self.ai_client.get_answer(prompt)
            return self._parse_explanation_response(response)
        except Exception as e:
            print(f"AI解释生成失败: {e}")
            return self._get_fallback_explanation(question)

    def _build_scoring_prompt(self, question_type, question_text, transcript,
                            reference_answer, student_answer):
        # 清理输入数据，移除多余的空白字符
        def clean_text(text):
            if not text:
                return ""
            # 将多个空白字符替换为单个空格
            text = ' '.join(text.split())
            return text.strip()

        question_text = clean_text(question_text)
        transcript = clean_text(transcript) if transcript else "未提供"
        reference_answer = clean_text(reference_answer)
        student_answer = clean_text(student_answer)

        prompt_template = """你是一位专业的英语听力评分专家。请根据以下信息对学生答案进行评分和反馈。

【题目信息】
题目类型：{question_type}
题目内容：{question_text}
听力原文：{transcript}
参考答案：{reference_answer}

【学生答案】
学生回答：{student_answer}

【评分标准】
请按照以下维度进行评分（每项0-100分）：
1. 内容准确性（40%）：是否正确回答了问题核心要点
2. 语言表达（30%）：语法正确性、词汇使用
3. 完整性（20%）：是否完整回答了问题
4. 逻辑连贯性（10%）：表达是否清晰、有条理

【输出要求】
请严格按照以下JSON格式输出，不要包含任何其他文字说明、markdown标记或代码块标记：
{{
  "content_accuracy": 分数,
  "language_expression": 分数,
  "completeness": 分数,
  "logical_coherence": 分数,
  "feedback": "整体反馈（2-3句话）",
  "suggestions": ["具体建议1", "具体建议2", "具体建议3"],
  "grammar_errors": [{{"error": "错误类型", "correction": "修改建议", "location": "位置"}}],
  "vocabulary_suggestions": [{{"word": "原词", "better": "更好的词", "reason": "原因"}}]
}}

注意：
- 只输出JSON对象，不要有任何前缀或后缀文字
- 不要使用```json```或其他markdown标记
- 分数必须是0-100的整数
- 建议必须具体、可操作
- 语法错误要指出具体位置
- 词汇建议要说明原因"""

        return prompt_template.format(
            question_type=question_type,
            question_text=question_text,
            transcript=transcript,
            reference_answer=reference_answer,
            student_answer=student_answer
        )

    def _build_explanation_prompt(self, question_type, question_text, options,
                               correct_answer, transcript):
        prompt_template = """
你是一位专业的英语听力教学专家。请根据以下信息为学生提供详细的答案解析。

【题目信息】
题目类型：{question_type}
题目内容：{question_text}
选项：
{options}
正确答案：{correct_answer}

【听力原文】
{transcript}

【输出要求】
请严格按照以下JSON格式输出（不要包含其他内容）：
{{
  "correct_answer_explanation": "详细解释为什么这个答案是正确的，引用听力原文",
  "distractor_analysis": [
    {{"option": "A", "reason": "为什么这个选项是错误的"}},
    {{"option": "B", "reason": "为什么这个选项是错误的"}},
    {{"option": "C", "reason": "为什么这个选项是错误的"}}
  ],
  "key_points": [
    "听力材料中的关键点1",
    "听力材料中的关键点2"
  ],
  "listening_tips": "针对这类题目的听力技巧建议",
  "related_knowledge": "相关的语言知识点（语法/词汇）"
}}

注意：
- 解释要引用听力原文的具体内容
- 干扰项分析要指出具体的误导点
- 听力技巧要实用、可操作
"""
        if isinstance(options, dict):
            options_text = "\n".join([
                f"{opt}: {text}" for opt, text in options.items()
            ])
        elif isinstance(options, str):
            options_text = options
        else:
            options_text = "未提供选项"

        return prompt_template.format(
            question_type=question_type,
            question_text=question_text,
            options=options_text,
            correct_answer=correct_answer,
            transcript=transcript or "未提供"
        )

    def _parse_scoring_response(self, response):
        result = self._extract_json_from_response(response)

        if result:
            required_fields = ['content_accuracy', 'language_expression', 'completeness',
                            'logical_coherence', 'feedback', 'suggestions',
                            'grammar_errors', 'vocabulary_suggestions']

            for field in required_fields:
                if field not in result:
                    if field in ['suggestions', 'grammar_errors', 'vocabulary_suggestions']:
                        result[field] = []
                    elif field == 'feedback':
                        result[field] = 'AI生成反馈中...'
                    else:
                        result[field] = 0

            for field in ['content_accuracy', 'language_expression', 'completeness', 'logical_coherence']:
                if not isinstance(result[field], (int, float)):
                    try:
                        result[field] = int(float(result[field]))
                    except (ValueError, TypeError):
                        result[field] = 50

                result[field] = max(0, min(100, result[field]))

            if 'total_score' not in result:
                result['total_score'] = (
                    result['content_accuracy'] * 0.4 +
                    result['language_expression'] * 0.3 +
                    result['completeness'] * 0.2 +
                    result['logical_coherence'] * 0.1
                )

            return result

        return self._get_fallback_result(response)

    def _parse_explanation_response(self, response):
        result = self._extract_json_from_response(response)

        if result:
            required_fields = ['correct_answer_explanation', 'distractor_analysis',
                            'key_points', 'listening_tips']

            for field in required_fields:
                if field not in result:
                    if field in ['distractor_analysis', 'key_points']:
                        result[field] = []
                    elif field == 'listening_tips':
                        result[field] = '请仔细听听力材料，注意关键词。'
                    else:
                        result[field] = 'AI生成解释中...'

            if 'related_knowledge' not in result:
                result['related_knowledge'] = ''

            return result

        return self._get_fallback_explanation(response)

    def _extract_json_from_response(self, response):
        if not response:
            return None

        # 清理控制字符和markdown标记
        def clean_json_string(text):
            # 移除markdown代码块标记
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)

            # 先尝试找到JSON对象的边界
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                text = json_match.group()

            # 移除所有控制字符（除了空格、换行、制表符）
            # 但保留JSON字符串内部的转义字符
            cleaned = ''
            in_string = False
            escape_next = False

            for i, char in enumerate(text):
                if escape_next:
                    cleaned += char
                    escape_next = False
                    continue

                if char == '\\':
                    cleaned += char
                    escape_next = True
                    continue

                if char == '"' and (i == 0 or text[i-1] != '\\'):
                    in_string = not in_string
                    cleaned += char
                    continue

                # 在字符串内部，保留所有字符但转义控制字符
                if in_string:
                    if ord(char) < 32 and char not in ['\n', '\r', '\t']:
                        # 跳过其他控制字符
                        continue
                    elif char == '\n':
                        cleaned += '\\n'
                    elif char == '\r':
                        cleaned += '\\r'
                    elif char == '\t':
                        cleaned += '\\t'
                    else:
                        cleaned += char
                else:
                    # 在字符串外部，移除控制字符
                    if ord(char) >= 32 or char in [' ', '\n', '\r', '\t']:
                        cleaned += char

            return cleaned

        try:
            cleaned_response = clean_json_string(response)
            print(f"清理后的JSON: {cleaned_response[:300]}...")
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"失败位置: line {e.lineno} column {e.colno}")
            if hasattr(e, 'pos'):
                print(f"错误附近内容: {response[max(0, e.pos-50):e.pos+50]}")
            return None

    def _get_empty_answer_result(self):
        return {
            'content_accuracy': 0,
            'language_expression': 0,
            'completeness': 0,
            'logical_coherence': 0,
            'total_score': 0.0,
            'feedback': '请先填写答案后再进行评分。',
            'suggestions': [
                '请仔细阅读题目要求',
                '根据听力内容回答问题',
                '确保答案完整且准确'
            ],
            'grammar_errors': [],
            'vocabulary_suggestions': []
        }

    def _get_fallback_result(self, student_answer):
        return {
            'content_accuracy': 50,
            'language_expression': 50,
            'completeness': 50,
            'logical_coherence': 50,
            'total_score': 50.0,
            'feedback': 'AI评分服务暂时不可用，请等待教师评分。',
            'suggestions': [],
            'grammar_errors': [],
            'vocabulary_suggestions': []
        }

    def _get_fallback_explanation(self, question):
        return {
            'correct_answer_explanation': f'正确答案是{question.answer}。',
            'distractor_analysis': [],
            'key_points': [],
            'listening_tips': '请仔细听听力材料，注意关键词。',
            'related_knowledge': ''
        }
