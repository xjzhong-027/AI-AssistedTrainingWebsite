# -*- coding: utf-8 -*-
"""
AI 提示服务：分级提示生成，复用火山引擎 Get_from_AI（与 scoring 一致）。
"""
from AI_module.Get_from_AI import Get_from_AI


# 提示级别：1=轻提示 2=方向提示 3=详细解释
LEVEL_LIGHT = 1
LEVEL_DIRECTION = 2
LEVEL_DETAIL = 3


class HintService:
    """分级提示生成，高级别使用火山引擎 API，与评分模块一致。"""

    def __init__(self, model='VolcEngine'):
        self.ai_client = Get_from_AI(model=model)

    def get_hint(self, question, level, student_answer='', transcript='', context=None):
        """
        根据级别返回提示内容。不泄露答案。
        Level 1/2/3 均走 AI 引擎，通过不同提示词区分轻重。
        """
        if level == LEVEL_LIGHT:
            content = self._level1_content(question, transcript=transcript)
        elif level == LEVEL_DIRECTION:
            content = self._level2_content(question, transcript=transcript)
        else:
            content = self._level3_content(question, transcript=transcript, student_answer=student_answer)
        return {'content': content or '暂无提示', 'level': level}

    def _call_ai_hint(self, prompt, question, fallback):
        """调用火山引擎生成提示，失败时返回 fallback。"""
        try:
            response = self.ai_client.get_answer(prompt)
            if response and response.strip():
                return response.strip()[:2000]
        except Exception as e:
            print(f"HintService 火山引擎调用失败: {e}")
        return fallback

    def _level1_content(self, question, transcript=''):
        """轻提示：AI 用一句话给最轻的思考方向，不涉及答案。"""
        question_type = getattr(question.main_question, 'question_type', 'choice') if hasattr(question, 'main_question') else 'choice'
        prompt = self._build_hint_prompt_light(
            question_text=question.question_text,
            question_type=question_type,
            transcript=transcript or '未提供',
        )
        fallback = '请再听一遍材料，注意题干问的是哪方面（时间/人物/原因等）。'
        return self._call_ai_hint(prompt, question, fallback)

    def _level2_content(self, question, transcript=''):
        """方向提示：AI 用 2～3 句话给方向性提示，不涉及答案。"""
        question_type = getattr(question.main_question, 'question_type', 'choice') if hasattr(question, 'main_question') else 'choice'
        prompt = self._build_hint_prompt_direction(
            question_text=question.question_text,
            question_type=question_type,
            transcript=transcript or '未提供',
        )
        fallback = '结合听力内容，从选项或填空处反推材料中对应的信息。'
        return self._call_ai_hint(prompt, question, fallback)

    def _level3_content(self, question, transcript='', student_answer=''):
        """详细解释：AI 给出更详细的理解引导，禁止包含正确答案。"""
        question_type = getattr(question.main_question, 'question_type', 'choice') if hasattr(question, 'main_question') else 'choice'
        prompt = self._build_hint_prompt_detail(
            question_text=question.question_text,
            question_type=question_type,
            transcript=transcript or '未提供',
            student_answer=student_answer,
        )
        fallback = (question.analysis or '').strip() or '请结合听力材料与题干关键词，再思考一次。'
        return self._call_ai_hint(prompt, question, fallback)

    def _build_hint_prompt_light(self, question_text, question_type, transcript):
        """Level 1：轻提示，一句话，只点明思考方向。禁止给答案。"""
        return f"""你是一位英语听力辅导老师。学生正在做听力题，需要你给「最轻」的一句话说提示，只点明思考方向，绝对不能透露正确答案或任何选项内容。

【题目】
{question_text}

【题型】
{question_type}

【听力原文（节选）】
{transcript[:2000] if transcript and transcript != '未提供' else '未提供'}

【要求】
1. 只输出一句话，例如：注意题干问的是时间/人物/原因/态度中的哪一类；或：关注材料开头/结尾的结论。
2. 不要说出正确答案、不要提到具体选项内容。
3. 中文回复，不要输出 JSON。"""

    def _build_hint_prompt_direction(self, question_text, question_type, transcript):
        """Level 2：方向提示，结合材料指出具体词汇或逻辑关系。禁止给答案。"""
        return f"""你是一位英语听力辅导老师。学生正在做听力题，需要你给「方向性」提示：必须结合下面这段听力原文，指出其中与题目相关的具体词汇、短语或逻辑关系，不能只给笼统建议。

【题目】
{question_text}

【题型】
{question_type}

【听力原文】
{transcript[:4000] if transcript and transcript != '未提供' else '未提供'}

【要求】
1. 必须结合原文：指出原文里需要重点关注的 1～3 个具体词汇或短语（可引用原文用引号标出），或指出原文中的逻辑关系（如转折、因果、举例、总结等）出现在哪类表述附近。
2. 用 2～4 句话，让学生能按你的提示回到材料里找到对应位置，仍不透露正确答案或选项内容。
3. 若原文未提供或过短，可说明应关注哪类信息，但一旦有原文就必须引用具体表述。
4. 中文回复，不要输出 JSON。"""

    def _build_hint_prompt_detail(self, question_text, question_type, transcript, student_answer):
        """Level 3：详细解释，紧密结合材料中的关键词、逻辑与位置。禁止给答案。"""
        return f"""你是一位英语听力辅导老师。学生正在做听力题，需要你给出「结合材料」的详细提示：根据听力原文具体指出与题目相关的关键词、逻辑关系、以及大致对应原文的哪一部分，不能给泛泛而谈的建议。

【题目】
{question_text}

【题型】
{question_type}

【听力原文】
{transcript[:5000] if transcript else '未提供'}

【要求】
1. 必须紧扣原文：列出原文中与答题相关的具体词汇或短语（用引号引用原文），并说明这些词/句在逻辑上的作用（如引出观点、转折、总结、举例等）。
2. 可指出答案相关信息在原文中的大致位置（如开头、中间某处、结尾）或与某类信号词（如 but, so, because, first, in conclusion）的关系。
3. 用 3～5 句话，让学生能带着你的提示重听并定位到具体内容，绝对不要说出正确答案或选项内容。
4. 若原文未提供或过短，再退而求其次给一般性理解建议；有原文时必须以引用原文为主。
5. 中文回复，不要输出 JSON。"""

    def get_max_allowed_level(self, student, sub_question_id):
        """
        消退机制：根据该生在该题上的历史提示请求次数，逐步减少可用级别。
        请求次数越多，最高可用级别越低，鼓励独立作答。
        """
        from AI_module.models import HintRequestLog
        count = HintRequestLog.objects.filter(
            student=student,
            sub_question_id=sub_question_id
        ).count()
        if count >= 6:
            return LEVEL_LIGHT
        if count >= 3:
            return LEVEL_DIRECTION
        return LEVEL_DETAIL