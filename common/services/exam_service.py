"""
Exam service interface.

This interface provides unified access to exam/practice functionality.
This will help merge duplicate code between stu_practice and accessment modules.
"""
from typing import Optional, List, Dict
from abc import ABC, abstractmethod


class ExamService(ABC):
    """考试服务接口"""
    
    @staticmethod
    @abstractmethod
    def create_exam_record(student_id: int, unit_id: int) -> 'StudentExamRecord':
        """
        创建考试记录
        
        Args:
            student_id: 学生ID
            unit_id: 单元ID
            
        Returns:
            StudentExamRecord 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_exam_record(student_id: int, unit_id: int) -> Optional['StudentExamRecord']:
        """
        获取考试记录
        
        Args:
            student_id: 学生ID
            unit_id: 单元ID
            
        Returns:
            StudentExamRecord 对象或 None（如果不存在）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_or_create_page_record(
        exam_record_id: int,
        page_id: int
    ) -> 'StudentPageRecord':
        """
        获取或创建页面记录
        
        Args:
            exam_record_id: 考试记录ID
            page_id: 试卷页面ID
            
        Returns:
            StudentPageRecord 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def save_answer(
        student_page_record_id: int,
        sub_question_id: int,
        answer_text: str,
        is_correct: Optional[bool] = None
    ) -> 'StudentAnswer':
        """
        保存学生答案
        
        Args:
            student_page_record_id: 学生页面记录ID
            sub_question_id: 小题ID
            answer_text: 答案文本
            is_correct: 是否正确（可选，用于自动批改）
            
        Returns:
            StudentAnswer 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_answers_by_page_record(page_record_id: int) -> List['StudentAnswer']:
        """
        获取页面记录的所有答案
        
        Args:
            page_record_id: 页面记录ID
            
        Returns:
            StudentAnswer 对象列表（可能为空）
        """
        pass
    
    @staticmethod
    @abstractmethod
    def update_media_play_record(
        exam_record_id: int,
        main_question_id: int,
        play_count: int,
        last_pause_time: float
    ) -> 'StudentMediaPlayRecord':
        """
        更新媒体播放记录
        
        Args:
            exam_record_id: 考试记录ID
            main_question_id: 大题ID
            play_count: 播放次数
            last_pause_time: 最后暂停时间
            
        Returns:
            StudentMediaPlayRecord 对象
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_media_play_record(
        exam_record_id: int,
        main_question_id: int
    ) -> Optional['StudentMediaPlayRecord']:
        """
        获取媒体播放记录
        
        Args:
            exam_record_id: 考试记录ID
            main_question_id: 大题ID
            
        Returns:
            StudentMediaPlayRecord 对象或 None
        """
        pass
    
    @staticmethod
    @abstractmethod
    def submit_exam(exam_record_id: int) -> bool:
        """
        提交考试
        
        Args:
            exam_record_id: 考试记录ID
            
        Returns:
            是否提交成功
        """
        pass

