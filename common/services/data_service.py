"""
Data service interface.

This interface provides unified data query and statistics functionality.
"""
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from datetime import datetime


class DataService(ABC):
    """数据查询服务接口"""
    
    @staticmethod
    @abstractmethod
    def get_student_learning_stats(
        student_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """获取学生学习统计"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_class_learning_stats(
        class_id: int,
        week: Optional[int] = None
    ) -> Dict:
        """获取班级学习统计"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_question_analysis(question_id: int) -> Dict:
        """获取题目分析数据"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_attendance_stats(
        class_id: int,
        week: Optional[int] = None
    ) -> Dict:
        """获取考勤统计"""
        pass
    
    @staticmethod
    @abstractmethod
    def generate_formative_assessment_report(
        student_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """生成形成性评估报告"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_media_play_analysis(
        student_id: int,
        material_id: Optional[int] = None
    ) -> Dict:
        """获取媒体播放分析"""
        pass

