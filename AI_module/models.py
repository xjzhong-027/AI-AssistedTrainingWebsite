from django.db import models
from Account.models import Students
from ELW.models import SubQuestion


class AIScoreRecord(models.Model):
    AI_MODEL_CHOICES = [
        ('VolcEngine', '火山引擎'),
        ('ZhipuAI', '智谱清言'),
        ('Local', '本地模型'),
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        related_name='ai_score_records',
        verbose_name='学生'
    )
    sub_question = models.ForeignKey(
        SubQuestion,
        on_delete=models.CASCADE,
        related_name='ai_scores',
        verbose_name='题目'
    )

    content_accuracy = models.IntegerField(
        default=0,
        verbose_name='内容准确性',
        help_text='是否正确回答了问题核心要点 (0-100分)'
    )
    language_expression = models.IntegerField(
        default=0,
        verbose_name='语言表达',
        help_text='语法正确性、词汇使用 (0-100分)'
    )
    completeness = models.IntegerField(
        default=0,
        verbose_name='完整性',
        help_text='是否完整回答了问题 (0-100分)'
    )
    logical_coherence = models.IntegerField(
        default=0,
        verbose_name='逻辑连贯性',
        help_text='表达是否清晰、有条理 (0-100分)'
    )
    total_score = models.FloatField(
        default=0.0,
        verbose_name='总分',
        help_text='加权计算的总分 (0-100分)'
    )

    feedback = models.TextField(
        verbose_name='整体反馈',
        help_text='AI生成的整体反馈 (2-3句话)'
    )
    suggestions = models.JSONField(
        default=list,
        verbose_name='改进建议',
        help_text='具体的改进建议列表'
    )
    grammar_errors = models.JSONField(
        default=list,
        verbose_name='语法错误',
        help_text='语法错误列表 [{"error": "错误类型", "correction": "修改建议", "location": "位置"}]'
    )
    vocabulary_suggestions = models.JSONField(
        default=list,
        verbose_name='词汇建议',
        help_text='词汇提升建议列表 [{"word": "原词", "better": "更好的词", "reason": "原因"}]'
    )

    student_answer = models.TextField(
        verbose_name='学生答案',
        help_text='学生的原始答案'
    )
    score_time = models.DateTimeField(
        auto_now=True,
        verbose_name='评分时间'
    )
    ai_model = models.CharField(
        max_length=50,
        default='VolcEngine',
        choices=AI_MODEL_CHOICES,
        verbose_name='AI模型'
    )

    class Meta:
        db_table = 'ai_score_record'
        verbose_name = 'AI评分记录'
        verbose_name_plural = 'AI评分记录'
        ordering = ['-score_time']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['sub_question']),
            models.Index(fields=['score_time']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.sub_question.id} - {self.total_score}分"

    def get_weighted_score(self):
        """
        计算加权总分
        总分 = 内容准确性×0.4 + 语言表达×0.3 + 完整性×0.2 + 逻辑连贯性×0.1
        """
        return (
            self.content_accuracy * 0.4 +
            self.language_expression * 0.3 +
            self.completeness * 0.2 +
            self.logical_coherence * 0.1
        )


class AIExplanationRecord(models.Model):
    AI_MODEL_CHOICES = [
        ('VolcEngine', '火山引擎'),
        ('ZhipuAI', '智谱清言'),
        ('Local', '本地模型'),
    ]

    id = models.AutoField(primary_key=True)
    sub_question = models.ForeignKey(
        SubQuestion,
        on_delete=models.CASCADE,
        related_name='ai_explanations',
        verbose_name='题目'
    )

    correct_answer_explanation = models.TextField(
        verbose_name='正确答案解释',
        help_text='详细解释为什么这个答案是正确的，引用听力原文'
    )
    distractor_analysis = models.JSONField(
        default=list,
        verbose_name='干扰项分析',
        help_text='干扰项错误原因列表 [{"option": "A", "reason": "为什么这个选项是错误的"}]'
    )
    key_points = models.JSONField(
        default=list,
        verbose_name='关键点',
        help_text='听力材料中的关键点列表'
    )
    listening_tips = models.TextField(
        verbose_name='听力技巧',
        help_text='针对这类题目的听力技巧建议'
    )
    related_knowledge = models.TextField(
        verbose_name='相关知识',
        help_text='相关的语言知识点（语法/词汇）',
        blank=True,
        null=True
    )

    generate_time = models.DateTimeField(
        auto_now=True,
        verbose_name='生成时间'
    )
    ai_model = models.CharField(
        max_length=50,
        default='VolcEngine',
        choices=AI_MODEL_CHOICES,
        verbose_name='AI模型'
    )

    class Meta:
        db_table = 'ai_explanation_record'
        verbose_name = 'AI解释记录'
        verbose_name_plural = 'AI解释记录'
        ordering = ['-generate_time']
        indexes = [
            models.Index(fields=['sub_question']),
            models.Index(fields=['generate_time']),
        ]

    def __str__(self):
        return f"{self.sub_question.id} - {self.ai_model}"


class AIConversationHistory(models.Model):
    AI_MODEL_CHOICES = [
        ('VolcEngine', '火山引擎'),
        ('ZhipuAI', '智谱清言'),
        ('Local', '本地模型'),
    ]

    MESSAGE_ROLES = [
        ('user', '用户'),
        ('assistant', 'AI助手'),
        ('system', '系统'),
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        verbose_name='学生'
    )

    role = models.CharField(
        max_length=20,
        choices=MESSAGE_ROLES,
        default='user',
        verbose_name='角色'
    )
    content = models.TextField(
        verbose_name='消息内容'
    )
    context = models.JSONField(
        default=dict,
        verbose_name='上下文',
        help_text='对话上下文信息 {"practice_id": 1, "page_id": 2, "sub_question_id": 3}'
    )

    message_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='消息时间'
    )
    ai_model = models.CharField(
        max_length=50,
        default='VolcEngine',
        choices=AI_MODEL_CHOICES,
        verbose_name='AI模型'
    )

    class Meta:
        db_table = 'ai_conversation_history'
        verbose_name = 'AI对话历史'
        verbose_name_plural = 'AI对话历史'
        ordering = ['message_time']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['message_time']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        content_preview = self.content[:30] + '...' if len(self.content) > 30 else self.content
        return f"{self.student.username} - {self.role} - {content_preview}"


# 提示级别：1=轻提示 2=方向提示 3=详细解释
HINT_LEVEL_CHOICES = [(1, '轻提示'), (2, '方向提示'), (3, '详细解释')]


class HintRequestLog(models.Model):
    """学生请求提示的记录，用于消退策略与形成性评估"""
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Students,
        on_delete=models.CASCADE,
        related_name='hint_request_logs',
        verbose_name='学生'
    )
    sub_question = models.ForeignKey(
        SubQuestion,
        on_delete=models.CASCADE,
        related_name='hint_request_logs',
        verbose_name='题目'
    )
    level = models.PositiveSmallIntegerField(
        choices=HINT_LEVEL_CHOICES,
        verbose_name='提示级别'
    )
    hint_content = models.TextField(
        verbose_name='返回的提示内容',
        blank=True,
        default=''
    )
    request_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='请求时间'
    )
    context = models.JSONField(
        default=dict,
        verbose_name='上下文',
        help_text='练习/页面等 {"practice_id": 1, "page_id": 2}'
    )

    class Meta:
        db_table = 'ai_hint_request_log'
        verbose_name = '提示请求记录'
        verbose_name_plural = '提示请求记录'
        ordering = ['-request_time']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['sub_question']),
            models.Index(fields=['request_time']),
        ]

    def __str__(self):
        return f"{self.student.username} - 题目{self.sub_question_id} - 级别{self.level}"
