"""
AI service interface.

This interface provides unified access to AI functionality.
"""
from typing import Optional, Dict, List
from abc import ABC, abstractmethod


class AIService(ABC):
    """AI服务接口"""
    
    @staticmethod
    @abstractmethod
    def generate_question(
        media_transcript: str,
        question_type: str,
        difficulty: Optional[str] = None
    ) -> Dict:
        """生成题目"""
        pass
    
    @staticmethod
    @abstractmethod
    def grade_answer(
        question_text: str,
        correct_answer: str,
        student_answer: str,
        question_type: str
    ) -> Dict:
        """批改答案"""
        pass
    
    @staticmethod
    @abstractmethod
    def generate_feedback(
        question_text: str,
        student_answer: str,
        is_correct: bool
    ) -> str:
        """生成反馈内容"""
        pass
    
    @staticmethod
    @abstractmethod
    def format_document(text: str) -> Dict:
        """格式化文档（用于Word导入）"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_ai_status() -> Dict:
        """获取AI服务状态"""
        pass

