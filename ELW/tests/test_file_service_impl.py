"""
Tests for FileService implementation.

These tests verify that FileServiceImpl correctly implements the FileService interface.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
import uuid
from ELW.services.file_service_impl import FileServiceImpl


class FileServiceImplTestCase(TestCase):
    """Test FileService implementation"""

    def setUp(self):
        """Set up test data"""
        # Create test media directory
        self.media_dir = os.path.join(settings.MEDIA_ROOT, 'media')
        self.image_dir = os.path.join(settings.MEDIA_ROOT, 'image')
        os.makedirs(self.media_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test files"""
        # Clean up test files
        if os.path.exists(self.media_dir):
            for file in os.listdir(self.media_dir):
                file_path = os.path.join(self.media_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        if os.path.exists(self.image_dir):
            for file in os.listdir(self.image_dir):
                file_path = os.path.join(self.image_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def test_upload_media_file_success(self):
        """Test uploading a media file successfully"""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        file_path, file_url = FileServiceImpl.upload_media_file(test_file, file_type='media')
        
        self.assertIsNotNone(file_path)
        self.assertIsNotNone(file_url)
        self.assertTrue(os.path.exists(file_path))
        self.assertIn('media_material', file_url)
        self.assertIn('media', file_url)

    def test_upload_media_file_with_extension(self):
        """Test uploading a media file with extension"""
        test_file = SimpleUploadedFile(
            "test_audio.mp3",
            b"audio_content",
            content_type="audio/mpeg"
        )
        
        file_path, file_url = FileServiceImpl.upload_media_file(test_file, file_type='media')
        
        self.assertIsNotNone(file_path)
        self.assertTrue(file_path.endswith('.mp3'))
        self.assertTrue(os.path.exists(file_path))

    def test_upload_image_files_success(self):
        """Test uploading multiple image files successfully"""
        test_files = [
            SimpleUploadedFile("test1.jpg", b"image1_content", content_type="image/jpeg"),
            SimpleUploadedFile("test2.png", b"image2_content", content_type="image/png")
        ]
        
        image_urls = FileServiceImpl.upload_image_files(test_files)
        
        self.assertEqual(len(image_urls), 2)
        self.assertIsInstance(image_urls[0], str)
        self.assertIsInstance(image_urls[1], str)
        self.assertIn('media_material', image_urls[0])
        self.assertIn('image', image_urls[0])

    def test_upload_image_files_empty_list(self):
        """Test uploading empty list of image files"""
        image_urls = FileServiceImpl.upload_image_files([])
        
        self.assertEqual(len(image_urls), 0)

    def test_get_file_url_success(self):
        """Test getting file URL successfully"""
        # Create a test file first
        test_file = SimpleUploadedFile(
            "test_file.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        file_path, _ = FileServiceImpl.upload_media_file(test_file, file_type='media')
        
        file_url = FileServiceImpl.get_file_url(file_path)
        
        self.assertIsNotNone(file_url)
        self.assertIn('media_material', file_url)

    def test_delete_file_success(self):
        """Test deleting a file successfully"""
        # Create a test file first
        test_file = SimpleUploadedFile(
            "test_file.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        file_path, _ = FileServiceImpl.upload_media_file(test_file, file_type='media')
        self.assertTrue(os.path.exists(file_path))
        
        result = FileServiceImpl.delete_file(file_path)
        
        self.assertTrue(result)
        self.assertFalse(os.path.exists(file_path))

    def test_delete_file_not_found(self):
        """Test deleting a non-existent file"""
        non_existent_path = os.path.join(settings.MEDIA_ROOT, 'media', 'non_existent_file.mp4')
        result = FileServiceImpl.delete_file(non_existent_path)
        
        # Should return False or handle gracefully
        self.assertIsInstance(result, bool)

    def test_validate_file_type_success(self):
        """Test validating file type successfully"""
        test_file = SimpleUploadedFile(
            "test_file.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        is_valid, error_msg = FileServiceImpl.validate_file_type(
            test_file,
            allowed_types=['.mp4', '.mp3', '.avi']
        )
        
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_validate_file_type_invalid(self):
        """Test validating invalid file type"""
        test_file = SimpleUploadedFile(
            "test_file.exe",
            b"file_content",
            content_type="application/x-msdownload"
        )
        
        is_valid, error_msg = FileServiceImpl.validate_file_type(
            test_file,
            allowed_types=['.mp4', '.mp3', '.avi']
        )
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)

    def test_get_file_size_success(self):
        """Test getting file size successfully"""
        # Create a test file with known content
        test_content = b"test file content" * 100  # 1700 bytes
        test_file = SimpleUploadedFile(
            "test_file.txt",
            test_content,
            content_type="text/plain"
        )
        file_path, _ = FileServiceImpl.upload_media_file(test_file, file_type='media')
        
        file_size = FileServiceImpl.get_file_size(file_path)
        
        self.assertIsInstance(file_size, int)
        self.assertGreater(file_size, 0)
        self.assertEqual(file_size, len(test_content))

    def test_get_file_size_not_found(self):
        """Test getting file size for non-existent file"""
        non_existent_path = os.path.join(settings.MEDIA_ROOT, 'media', 'non_existent_file.mp4')
        
        # Should handle gracefully (return 0 or raise exception)
        try:
            file_size = FileServiceImpl.get_file_size(non_existent_path)
            self.assertEqual(file_size, 0)
        except (FileNotFoundError, OSError):
            # Exception is also acceptable
            pass




