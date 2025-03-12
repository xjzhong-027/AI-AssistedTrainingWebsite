from django import forms
from .models import Class

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['class_name', 'course', 'teacher', 'start_date', 'week', 'start_time', 'end_time']

    # 给class_name字段添加placeholder的效果
    class_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '例如：2101, 2102'
        })
    )