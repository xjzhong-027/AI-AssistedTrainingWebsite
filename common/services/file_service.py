"""
File service interface.

This interface provides unified file upload, storage, and access functionality.
"""
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from django.core.files.uploadedfile import UploadedFile


class FileService(ABC):
    """文件服务接口"""
    
    @staticmethod
    @abstractmethod
    def upload_media_file(
        file: UploadedFile,
        file_type: str = 'media'  # 'media', 'image', 'document'
    ) -> Tuple[str, str]:
        """上传媒体文件，返回 (file_path, file_url)"""
        pass
    
    @staticmethod
    @abstractmethod
    def upload_image_files(files: List[UploadedFile]) -> List[str]:
        """上传多个图片文件，返回图片URL列表"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_file_url(file_path: str) -> str:
        """获取文件的访问URL"""
        pass
    
    @staticmethod
    @abstractmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        pass
    
    @staticmethod
    @abstractmethod
    def delete_files_by_material(material_id: int) -> bool:
        """删除与媒体素材关联的所有文件"""
        pass
    
    @staticmethod
    @abstractmethod
    def validate_file_type(
        file: UploadedFile,
        allowed_types: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """验证文件类型，返回 (是否有效, 错误信息)"""
        pass
    
    @staticmethod
    @abstractmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        pass

