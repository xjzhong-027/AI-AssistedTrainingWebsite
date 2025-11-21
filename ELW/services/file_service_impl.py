"""
FileService implementation for ELW module.

This module implements the FileService interface, providing unified file upload,
storage, and access functionality.
"""
from typing import Optional, List, Tuple
from common.services.file_service import FileService
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os
import uuid


class FileServiceImpl(FileService):
    """文件服务实现"""
    
    @staticmethod
    def upload_media_file(
        file: UploadedFile,
        file_type: str = 'media'  # 'media', 'image', 'document'
    ) -> Tuple[str, str]:
        """上传媒体文件，返回 (file_path, file_url)"""
        # Generate unique filename
        file_uuid = uuid.uuid4().hex
        original_filename = file.name
        file_extension = os.path.splitext(original_filename)[1]
        
        # Determine storage directory based on file_type
        if file_type == 'image':
            storage_dir = os.path.join(settings.MEDIA_ROOT, 'image')
            url_prefix = 'media_material/image'
        elif file_type == 'document':
            storage_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
            url_prefix = 'media_material/documents'
        else:  # 'media' or default
            storage_dir = os.path.join(settings.MEDIA_ROOT, 'media')
            url_prefix = 'media_material/media'
        
        # Create directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Build file path
        if file_extension:
            file_path = os.path.join(storage_dir, file_uuid + file_extension)
        else:
            file_path = os.path.join(storage_dir, file_uuid)
        
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Build file URL
        file_url = os.path.join(url_prefix, os.path.basename(file_path)).replace('\\', '/')
        
        return file_path, file_url
    
    @staticmethod
    def upload_image_files(files: List[UploadedFile]) -> List[str]:
        """上传多个图片文件，返回图片URL列表"""
        image_urls = []
        
        if not files:
            return image_urls
        
        # Generate a common UUID for this batch of images
        batch_uuid = uuid.uuid4().hex
        image_dir = os.path.join(settings.MEDIA_ROOT, 'image', batch_uuid)
        os.makedirs(image_dir, exist_ok=True)
        
        for image_file in files:
            image_file_path = os.path.join(image_dir, image_file.name)
            image_url = os.path.join('media_material', 'image', batch_uuid, image_file.name).replace('\\', '/')
            
            # Save image file
            with open(image_file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            image_urls.append(image_url)
        
        return image_urls
    
    @staticmethod
    def get_file_url(file_path: str) -> str:
        """获取文件的访问URL"""
        # Convert absolute path to relative URL
        if not file_path:
            return ''
        
        # Get relative path from MEDIA_ROOT
        try:
            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            # Convert to URL format (use forward slashes)
            file_url = os.path.join('media_material', relative_path).replace('\\', '/')
            return file_url
        except ValueError:
            # If file_path is not under MEDIA_ROOT, return as is
            return file_path.replace('\\', '/')
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        if not file_path or not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False
    
    @staticmethod
    def delete_files_by_material(material_id: int) -> bool:
        """删除与媒体素材关联的所有文件"""
        try:
            from ELW.models import MediaMaterial
            material = MediaMaterial.objects.get(id=material_id)
            
            deleted_count = 0
            
            # Delete media file
            if material.media_url:
                media_path = os.path.join(settings.MEDIA_ROOT, material.media_url)
                if os.path.exists(media_path):
                    os.remove(media_path)
                    deleted_count += 1
            
            # Delete image file
            if material.image_url:
                image_path = os.path.join(settings.MEDIA_ROOT, material.image_url)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    deleted_count += 1
            
            # Delete image directory if it exists (for batch uploads)
            if material.image_url:
                image_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, material.image_url))
                if os.path.exists(image_dir) and os.path.isdir(image_dir):
                    try:
                        os.rmdir(image_dir)  # Only remove if empty
                    except OSError:
                        pass  # Directory not empty, skip
            
            return deleted_count > 0
        except Exception:
            return False
    
    @staticmethod
    def validate_file_type(
        file: UploadedFile,
        allowed_types: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """验证文件类型，返回 (是否有效, 错误信息)"""
        if not file or not file.name:
            return False, "文件名为空"
        
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if not file_extension:
            return False, "文件没有扩展名"
        
        # Normalize allowed_types (ensure they start with .)
        normalized_allowed = []
        for allowed_type in allowed_types:
            if not allowed_type.startswith('.'):
                normalized_allowed.append('.' + allowed_type.lower())
            else:
                normalized_allowed.append(allowed_type.lower())
        
        if file_extension not in normalized_allowed:
            return False, f"不支持的文件类型: {file_extension}。允许的类型: {', '.join(normalized_allowed)}"
        
        return True, None
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        if not file_path or not os.path.exists(file_path):
            return 0
        
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0

