from django import forms
from django.core.validators import FileExtensionValidator
from django.forms.widgets import ClearableFileInput
import os

from django.template.context_processors import request


#
# def validate_file_extension(value):
#     valid_extensions = ['.mp3', '.wav', '.mp4', '.avi', '.mov']  # 根据需要添加更多扩展名
#     extension = os.path.splitext(value.name)[1].lower()
#     if extension not in valid_extensions:
#         raise forms.ValidationError("Invalid file extension! Please upload a video or an audio!")
#
# class UploadMediaForm(forms.Form):
#     file = forms.FileField(validators=[
#         # 自定义验证器，确保文件是音频或视频
#         validate_file_extension  # 这个验证器需要你自己实现，下面会展示
#     ])

class UploadMediaForm(forms.Form):
    audio_file = forms.FileField(
        # 只允许上传音频
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'mp4'])],
        widget=ClearableFileInput(attrs={'accept': 'audio/*'}),
        required=False,
    )
    video_file = forms.FileField(
        # 只允许上传视频
        validators=[FileExtensionValidator(allowed_extensions=['avi', 'wav', 'mov', 'ogg', 'webm'])],
        widget=ClearableFileInput(attrs={'accept': 'video/*'}),
        required=False,
    )
    image_file = forms.FileField(
        # 只允许上传图片
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        widget=ClearableFileInput(attrs={'accept': 'image/*'}),
        required=False,
    )


