from django import forms
from django.core.validators import FileExtensionValidator
from django.forms.widgets import ClearableFileInput
import os

from django.template.context_processors import request
import requests
from docx import Document as DocxDocument
from io import BytesIO




from django import forms
from django.forms import inlineformset_factory
from .models import MainQuestion, SubQuestion, ChoiceOption, MatchingOption, Correction, Document


class WordUploadForm(forms.Form):
    word_file = forms.FileField(label='文件导入')

# 大题表单
class MainQuestionForm(forms.ModelForm):
    class Meta:
        model = MainQuestion
        fields = ['question_text']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4}),
        }

# 小题表单
class SubQuestionForm(forms.ModelForm):
    class Meta:
        model = SubQuestion
        fields = ['question_text', 'image_url', 'tips', 'answer', 'analysis', 'score']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 2}),
            'tips': forms.Textarea(attrs={'rows': 2}),
            'answer': forms.Textarea(attrs={'rows': 2}),
            'analysis': forms.Textarea(attrs={'rows': 2}),
            'score': forms.NumberInput(),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document_url',)

# 选择题-选项表单
class ChoiceOptionForm(forms.ModelForm):
    class Meta:
        model = ChoiceOption
        fields = ['option_label', 'option_content', 'is_answer']

# 连线题右项表单
class MatchingOptionForm(forms.ModelForm):
    class Meta:
        model = MatchingOption
        fields = ['option_label', 'option_content', 'image_url']

    def clean(self):
        cleaned_data = super().clean()
        sub_question = cleaned_data.get('sub_question')
        if not sub_question:
            raise forms.ValidationError("Sub-question field is required.")
        return cleaned_data

# 改错题表单
class CorrectionForm(forms.ModelForm):
    class Meta:
        model = Correction
        fields = ['type', 'index']

# 创建大题与小题的表单集合
SubQuestionFormSet = inlineformset_factory(
    MainQuestion,
    SubQuestion,  # 父模型和子模型
    form=SubQuestionForm,
    extra=1,  # 默认提供一个空表单
    can_delete=True  # 允许用户删除小题
)

# 创建小题与选项的表单集合
ChoiceOptionFormSet = inlineformset_factory(
    SubQuestion,
    ChoiceOption,
    form=ChoiceOptionForm,
    extra=2,
    can_delete=True
)

# 创建小题与连线右项的表单集合
MatchingOptionFormset = inlineformset_factory(
    SubQuestion,
    MatchingOption,
    form=MatchingOptionForm,
    extra=1,  # 默认多一个表单
    can_delete=True
)

# 创建小题与改错题的表单集合
CorrectionFormSet = inlineformset_factory(
    SubQuestion,
    Correction,
    form=CorrectionForm,
    extra=1,
    can_delete=True
)










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
    # audio_file = forms.FileField(
    #     # 只允许上传音频
    #     validators=[FileExtensionValidator(allowed_extensions=['mp3', 'mp4'])],
    #     widget=ClearableFileInput(attrs={'accept': 'audio/*'}),
    #     required=False,
    # )
    # video_file = forms.FileField(
    #     # 只允许上传视频
    #     validators=[FileExtensionValidator(allowed_extensions=['avi', 'wav', 'mov', 'ogg', 'webm'])],
    #     widget=ClearableFileInput(attrs={'accept': 'video/*'}),
    #     required=False,
    # )
    media_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'mp4', 'avi', 'wav', 'mov', 'ogg', 'webm'])],
        widget=ClearableFileInput(attrs={'accept': '.mp3,.mp4,.avi,.wav,.mov,.ogg,.webm,audio/*'}),
        # 至少要上传一个媒体文件
        required=True,
    )
    # image_file = forms.FileField(
    #     # 只允许上传图片
    #     validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
    #     widget=ClearableFileInput(attrs={'accept': 'image/*'}),
    #     # 可以不上传图片
    #     required=False,
    # )
    image_file = forms.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        widget=ClearableFileInput(attrs={'accept': 'image/*', 'multiple': True}),
        required=False,
    )


