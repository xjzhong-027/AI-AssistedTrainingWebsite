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
    def get_media_play_records_by_exam(
        exam_record_id: int,
        main_question_ids: Optional[List[int]] = None
    ) -> List['StudentMediaPlayRecord']:
        """
        获取考试记录的所有媒体播放记录
        
        Args:
            exam_record_id: 考试记录ID
            main_question_ids: 大题ID列表（可选，如果提供则只查询这些大题）
            
        Returns:
            StudentMediaPlayRecord 对象列表
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
    
    @staticmethod
    @abstractmethod
    def load_answers(page_record_id: int) -> Dict:
        """
        加载页面记录的答案（从缓存或数据库）
        
        Args:
            page_record_id: 页面记录ID
            
        Returns:
            答案字典，key为sub_question_id，value为答案内容
        """
        pass
    
    @staticmethod
    @abstractmethod
    def save_answers_to_cache(
        page_record_id: int,
        answers_data: Dict
    ) -> bool:
        """
        保存答案到缓存
        
        Args:
            page_record_id: 页面记录ID
            answers_data: 答案数据字典
            
        Returns:
            是否保存成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def save_answers_to_database(page_record_id: int) -> bool:
        """
        从缓存读取答案并保存到数据库
        
        Args:
            page_record_id: 页面记录ID
            
        Returns:
            是否保存成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def submit_page(page_record_id: int) -> bool:
        """
        提交页面
        
        Args:
            page_record_id: 页面记录ID
            
        Returns:
            是否提交成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def grade_page(page_record_id: int) -> bool:
        """
        批改页面
        
        Args:
            page_record_id: 页面记录ID
            
        Returns:
            是否批改成功
        """
        pass
    
    @staticmethod
    @abstractmethod
    def grade_comprehension(
        sub_question_id: int,
        student_answer_id: int
    ) -> float:
        """
        批改理解题（使用AI）
        
        Args:
            sub_question_id: 小题ID
            student_answer_id: 学生答案ID
            
        Returns:
            得分
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_exam_record_by_id(record_id: int) -> Optional['StudentExamRecord']:
        """
        根据ID获取考试记录
        
        Args:
            record_id: 考试记录ID
            
        Returns:
            StudentExamRecord 对象或 None
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_page_record_by_id(record_id: int) -> Optional['StudentPageRecord']:
        """
        根据ID获取页面记录
        
        Args:
            record_id: 页面记录ID
            
        Returns:
            StudentPageRecord 对象或 None
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_page_records_by_exam(exam_record_id: int) -> List['StudentPageRecord']:
        """
        获取考试记录的所有页面记录
        
        Args:
            exam_record_id: 考试记录ID
            
        Returns:
            StudentPageRecord 对象列表
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_exam_records_by_user(user_id: int) -> List['StudentExamRecord']:
        """
        获取用户的所有考试记录
        
        Args:
            user_id: 用户ID
            
        Returns:
            StudentExamRecord 对象列表
        """
        pass

