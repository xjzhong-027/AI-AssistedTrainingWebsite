"""
Common exceptions for service layer.

All service-related exceptions should inherit from ServiceException.
"""


class ServiceException(Exception):
    """服务层基础异常"""
    pass


class UserNotFoundError(ServiceException):
    """用户不存在异常"""
    pass


class AuthenticationError(ServiceException):
    """认证失败异常"""
    pass


class PermissionDeniedError(ServiceException):
    """权限不足异常"""
    pass


class ContentNotFoundError(ServiceException):
    """内容不存在异常（题目、媒体素材等）"""
    pass


class FileOperationError(ServiceException):
    """文件操作异常"""
    pass


class AIServiceError(ServiceException):
    """AI服务异常"""
    pass


class NotificationError(ServiceException):
    """通知服务异常"""
    pass

