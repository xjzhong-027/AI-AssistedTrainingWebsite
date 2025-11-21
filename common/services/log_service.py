"""
Log service interface.

This interface provides unified logging functionality.
"""
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
from django.http import HttpRequest
from datetime import datetime


class LogService(ABC):
    """日志服务接口"""
    
    @staticmethod
    @abstractmethod
    def log_operation(
        user_id: Optional[int],
        username: str,
        operation_type: str,
        module: str,
        message: str,
        request: Optional[HttpRequest] = None
    ) -> 'LogEntry':
        """记录操作日志"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_logs(
        username: Optional[str] = None,
        module: Optional[str] = None,
        operation_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List['LogEntry']:
        """查询日志"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_user_operation_count(
        username: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """获取用户操作统计"""
        pass

