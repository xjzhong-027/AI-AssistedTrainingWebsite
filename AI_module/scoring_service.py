import json
import re
from typing import Optional

from AI_module.Get_from_AI import Get_from_AI


class AIScoringService:
    def __init__(self, model: str = "VolcEngine"):
        self.ai_client = Get_from_AI(model=model)

    def score_subjective_answer(self, question, student_answer: str, transcript: Optional[str] = None):
        """
        评分主观题答案（AI 直接返回 0-100 分制各维度及 total_score）。
        """
        try:
            if not student_answer or not student_answer.strip():
                return self._get_empty_answer_result()

            # 安全获取题目信息，避免属性缺失导致异常
            try:
                question_type = (
                    question.main_question.question_type
                    if hasattr(question, "main_question") and question.main_question
                    else "text"
                )
            except Exception as e:
                print(f"获取题目类型失败: {e}")
                question_type = "text"

            try:
                question_text = question.question_text if hasattr(question, "question_text") else ""
            except Exception as e:
                print(f"获取题目文本失败: {e}")
                question_text = ""

            try:
                reference_answer = question.answer if hasattr(question, "answer") else ""
            except Exception as e:
                print(f"获取参考答案失败: {e}")
                reference_answer = ""

            # 当参考答案缺失时，回退使用听力原文作为参考
            if not reference_answer or reference_answer.strip() == "":
                reference_answer = transcript if transcript else "未提供"
                print("参考答案为空，使用听力原文作为参考")

            prompt = self._build_scoring_prompt(
                question_type=question_type,
                question_text=question_text,
                transcript=transcript,
                reference_answer=reference_answer,
                student_answer=student_answer,
            )

            print("评分Prompt信息:")
            print(f"  题目: {question_text[:100]}...")
            print(f"  参考答案: {reference_answer[:100]}...")
            print(f"  学生答案: {student_answer[:100]}...")

            try:
                response = self.ai_client.get_answer(prompt)
                print(f"AI原始响应: {response[:500]}...")
                result = self._parse_scoring_response(response)

                # 新协议：total_score 由模型直接给出，范围控制在 0-100
                print(
                    "AI评分结果: "
                    f"content_accuracy={result.get('content_accuracy')}, "
                    f"language_expression={result.get('language_expression')}, "
                    f"completeness={result.get('completeness')}, "
                    f"logical_coherence={result.get('logical_coherence')}, "
                    f"total_score={result.get('total_score')}"
                )

                return result
            except Exception as e:
                import traceback

                print(f"AI评分失败: {e}")
                print(f"错误堆栈: {traceback.format_exc()}")
                return self._get_fallback_result(student_answer)
        except Exception as e:
            import traceback

            print(f"score_subjective_answer 外部异常: {e}")
            print(f"错误堆栈: {traceback.format_exc()}")
            return self._get_fallback_result(student_answer)

    def generate_explanation(self, question, transcript: Optional[str] = None, student_answer: Optional[str] = None, score: Optional[float] = None):
        """
        生成题目解释或主观题反馈：
        - 若提供 student_answer + score，则生成主观题反馈；
        - 否则生成客观题解析。
        """
        question_type = question.main_question.question_type if hasattr(question, "main_question") else "text"
        options = question.options if hasattr(question, "options") else None

        if student_answer and score is not None:
            prompt = self._build_subjective_feedback_prompt(
                question_text=question.question_text,
                transcript=transcript,
                correct_answer=question.answer,
                student_answer=student_answer,
                score=score,
            )
            is_subjective_feedback = True
        else:
            prompt = self._build_explanation_prompt(
                question_type=question_type,
                question_text=question.question_text,
                options=options,
                correct_answer=question.answer,
                transcript=transcript,
            )
            is_subjective_feedback = False

        try:
            response = self.ai_client.get_answer(prompt)
            if is_subjective_feedback:
                return self._parse_subjective_feedback_response(response)
            return self._parse_explanation_response(response, question)
        except Exception as e:
            print(f"AI解释生成失败: {e}")
            return self._get_fallback_explanation(question)

    def _build_scoring_prompt(self, question_type, question_text, transcript, reference_answer, student_answer):
        # 清理输入数据，移除多余的空白字符
        def clean_text(text):
            if not text:
                return ""
            text = " ".join(text.split())
            return text.strip()

        question_text = clean_text(question_text)
        transcript = clean_text(transcript) if transcript else "未提供"
        reference_answer = clean_text(reference_answer)
        student_answer = clean_text(student_answer)

        prompt_template = """You are an intelligent digital tutor evaluating an English listening practice system. Your task is to evaluate a student's subjective answer (such as a short answer or summary) based on the provided audio transcript, question text, and reference answer. 

Please evaluate the student's answer across the following four pedagogically grounded dimensions, scoring each from 0 to 100: 
1. Content Accuracy (40% weight): Does the answer correctly capture the semantic core and factual details of the original audio transcript? 
2. Language Expression (30% weight): Is the grammar correct? Is the vocabulary used appropriately for an L2 English learner? 
3. Completeness (20% weight): Does the answer address all parts of the question? 
4. Logical Coherence (10% weight): Is the answer logically organized and easy to follow? 

In addition to the scores, you must provide immediate, actionable, and diagnostic feedback. 

INPUT DATA: 
- Question Type: {question_type} 
- Question Text: {question_text} 
- Audio Transcript: {transcript} 
- Reference Answer: {reference_answer} 
- Student Answer: {student_answer} 

OUTPUT FORMAT STRICT INSTRUCTIONS: 
You MUST output ONLY a raw, valid JSON object. DO NOT wrap the output in Markdown code blocks (e.g., do not use ```json). Do not add any conversational text before or after the JSON. 

The JSON object must strictly match the following keys: 
{{
  "content_accuracy": <int 0-100>, 
  "language_expression": <int 0-100>, 
  "completeness": <int 0-100>, 
  "logical_coherence": <int 0-100>, 
  "total_score": <float 0-100, calculated as: CA*0.4 + LE*0.3 + CO*0.2 + LC*0.1>, 
  "feedback": "<string, clear explanation of why the answer received this score, referencing the transcript>", 
  "suggestions": "<string, specific actionable advice for the next listening attempt>", 
  "grammar_errors": "<string, point out specific grammatical mistakes, or write 'None' if perfect>", 
  "vocabulary_suggestions": "<string, suggestions for better vocabulary usage, or write 'None'>" 
}}"""

        return prompt_template.format(
            question_type=question_type,
            question_text=question_text,
            transcript=transcript,
            reference_answer=reference_answer,
            student_answer=student_answer,
        )

    def _build_explanation_prompt(self, question_type, question_text, options, correct_answer, transcript):
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
            options_text = "\n".join([f"{opt}: {text}" for opt, text in options.items()])
        elif isinstance(options, str):
            options_text = options
        else:
            options_text = "未提供选项"

        return prompt_template.format(
            question_type=question_type,
            question_text=question_text,
            options=options_text,
            correct_answer=correct_answer,
            transcript=transcript or "未提供",
        )

    def _build_subjective_feedback_prompt(self, question_text, transcript, correct_answer, student_answer, score):
        """
        构建主观题反馈提示，用于在批改后生成自然语言反馈。
        """

        def clean_text(text):
            if not text:
                return ""
            text = " ".join(text.split())
            return text.strip()

        question_text = clean_text(question_text)
        transcript = clean_text(transcript) if transcript else "未提供"
        correct_answer = clean_text(correct_answer)
        student_answer = clean_text(student_answer)

        prompt_template = """You are an AI feedback assistant in an English Listening Practice System.

Your task is to provide clear and helpful feedback to students after their listening exercise.

You will receive:
- The question: {question_text}
- Listening transcript: {transcript}
- Correct answer: {correct_answer}
- Student answer: {student_answer}
- Student score: {score}

Your feedback should include four parts:

1. Answer Evaluation
Briefly state whether the student's answer is correct or partially correct.

2. Explanation
Explain the key sentence or information in the listening transcript that supports the correct answer.

3. Error Analysis
If the student's answer is incorrect, explain the possible reason for the mistake. Possible reasons include:
- misunderstanding vocabulary
- missing key information
- confusing distractor options
- incomplete listening

4. Learning Suggestion
Provide one or two practical suggestions to improve listening skills.

Style Requirements:
- Use clear and simple English.
- Keep the explanation concise and supportive.
- Encourage the student to reflect on the listening process.

Output Format (STRICT JSON):

{{
"answer_evaluation": "evaluation text",
"explanation": "explanation text",
"error_analysis": "error analysis text",
"learning_suggestion": "learning suggestion text"
}}

Do not provide explanations outside the JSON format.
"""

        return prompt_template.format(
            question_text=question_text,
            transcript=transcript,
            correct_answer=correct_answer,
            student_answer=student_answer,
            score=score,
        )

    def _parse_scoring_response(self, response: str):
        print(f"_parse_scoring_response 输入: {response[:500]}...")
        result = self._extract_json_from_response(response)
        print(f"_extract_json_from_response 结果: {result}")

        if result:
            # 直接使用 0-100 分制
            score_fields = ["content_accuracy", "language_expression", "completeness", "logical_coherence", "total_score"]
            string_fields = ["feedback", "suggestions", "grammar_errors", "vocabulary_suggestions"]

            print(f"解析前原始分数: {result}")
            for field in score_fields:
                if field not in result:
                    result[field] = 0
                else:
                    original_value = result[field]
                    if not isinstance(result[field], (int, float)):
                        try:
                            result[field] = float(result[field])
                            print(f"  {field}: '{original_value}' -> {result[field]}")
                        except (ValueError, TypeError):
                            print(f"  {field}: '{original_value}' 转换失败，设置为 0")
                            result[field] = 0
                    # 限制在 0~100
                    result[field] = max(0, min(100, result[field]))
                    if result[field] != original_value:
                        print(f"  {field}: 限制范围到 {result[field]}")

            for field in string_fields:
                if field not in result:
                    result[field] = ""

            # 当 feedback/suggestions 等为空时设置默认值
            if not result["feedback"]:
                result["feedback"] = "Your answer partially addresses the question, but needs more specific details from the video. Please provide a more comprehensive response that directly references content from the transcript."
            if not result["suggestions"]:
                result["suggestions"] = "Please carefully read the question requirements and provide a more detailed answer that incorporates specific details from the video. Focus on directly addressing all parts of the question."
            if not result["grammar_errors"]:
                result["grammar_errors"] = "None"
            if not result["vocabulary_suggestions"]:
                result["vocabulary_suggestions"] = "None"

            # 确保 suggestions 是字符串类型（AI 可能返回 list）
            if not isinstance(result["suggestions"], str):
                try:
                    if isinstance(result["suggestions"], list):
                        result["suggestions"] = " ".join(result["suggestions"])
                    else:
                        result["suggestions"] = str(result["suggestions"])
                except Exception:
                    result["suggestions"] = "Please carefully read the question requirements and provide a more detailed answer that incorporates specific details from the video. Focus on directly addressing all parts of the question."

            result["content_accuracy"] = max(0, min(100, result["content_accuracy"]))
            result["language_expression"] = max(0, min(100, result["language_expression"]))
            result["completeness"] = max(0, min(100, result["completeness"]))
            result["logical_coherence"] = max(0, min(100, result["logical_coherence"]))
            result["total_score"] = max(0, min(100, result["total_score"]))

            print(
                "解析后分数: "
                f"content_accuracy={result['content_accuracy']}, "
                f"language_expression={result['language_expression']}, "
                f"completeness={result['completeness']}, "
                f"logical_coherence={result['logical_coherence']}, "
                f"total_score={result['total_score']}"
            )

            return result

        # 当 JSON 解析失败时返回 50 分兜底（而非 0 分）
        return self._get_fallback_result("")

    def _parse_subjective_feedback_response(self, response: str):
        """
        解析主观题文字反馈响应。
        """
        result = self._extract_json_from_response(response)
        if result:
            required_fields = ["answer_evaluation", "explanation", "error_analysis", "learning_suggestion"]
            for field in required_fields:
                if field not in result:
                    result[field] = ""
            return result

        return {
            "answer_evaluation": "AI反馈生成中...",
            "explanation": "",
            "error_analysis": "",
            "learning_suggestion": "",
        }

    def _parse_explanation_response(self, response: str, question=None):
        result = self._extract_json_from_response(response)

        if result:
            required_fields = ["correct_answer_explanation", "distractor_analysis", "key_points", "listening_tips"]
            for field in required_fields:
                if field not in result:
                    if field in ["distractor_analysis", "key_points"]:
                        result[field] = []
                    elif field == "listening_tips":
                        result[field] = "请仔细听听力材料，注意关键词。"
                    else:
                        result[field] = "AI生成解释中..."

            if "related_knowledge" not in result:
                result["related_knowledge"] = ""

            return result

        return self._get_fallback_explanation(question) if question else {
            "correct_answer_explanation": "AI生成解释中...",
            "distractor_analysis": [],
            "key_points": [],
            "listening_tips": "请仔细听听力材料，注意关键词。",
            "related_knowledge": "",
        }

    def _extract_json_from_response(self, response: str):
        if not response:
            return None

        def clean_json_string(text: str) -> str:
            # 移除 markdown 代码块标记
            text = re.sub(r"```json\s*", "", text)
            text = re.sub(r"```\s*", "", text)

            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                text = json_match.group()

            cleaned = ""
            in_string = False
            escape_next = False

            for i, char in enumerate(text):
                if escape_next:
                    cleaned += char
                    escape_next = False
                    continue

                if char == "\\":
                    cleaned += char
                    escape_next = True
                    continue

                if char == '"' and (i == 0 or text[i - 1] != "\\"):
                    in_string = not in_string
                    cleaned += char
                    continue

                if in_string:
                    if ord(char) < 32 and char not in ["\n", "\r", "\t"]:
                        continue
                    elif char == "\n":
                        cleaned += "\\n"
                    elif char == "\r":
                        cleaned += "\\r"
                    elif char == "\t":
                        cleaned += "\\t"
                    else:
                        cleaned += char
                else:
                    if ord(char) >= 32 or char in [" ", "\n", "\r", "\t"]:
                        cleaned += char

            return cleaned

        try:
            cleaned_response = clean_json_string(response)
            print(f"清理后的JSON: {cleaned_response[:300]}...")
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"失败位置: line {e.lineno} column {e.colno}")
            if hasattr(e, "pos"):
                print(f"错误附近内容: {response[max(0, e.pos - 50):e.pos + 50]}")
            return None

    def _get_empty_answer_result(self):
        # 保持字段名称与前端一致，但使用字符串字段形式，兼容同事版
        return {
            "content_accuracy": 0,
            "language_expression": 0,
            "completeness": 0,
            "logical_coherence": 0,
            "total_score": 0,
            "feedback": "请先填写答案后再进行评分。",
            "suggestions": "请仔细阅读题目要求，根据听力内容回答问题，确保答案完整且准确。",
            "grammar_errors": "None",
            "vocabulary_suggestions": "None",
        }

    def _get_fallback_result(self, student_answer: str):
        # 统一回退为 50 分，并保持 JSON 结构
        return {
            "content_accuracy": 50,
            "language_expression": 50,
            "completeness": 50,
            "logical_coherence": 50,
            "total_score": 50,
            "feedback": "AI评分服务暂时不可用，请等待教师评分。",
            "suggestions": "请等待教师评分。",
            "grammar_errors": "None",
            "vocabulary_suggestions": "None",
        }

    def _get_fallback_explanation(self, question):
        return {
            "correct_answer_explanation": f"正确答案是{question.answer}。",
            "distractor_analysis": [],
            "key_points": [],
            "listening_tips": "请仔细听听力材料，注意关键词。",
            "related_knowledge": "",
        }
