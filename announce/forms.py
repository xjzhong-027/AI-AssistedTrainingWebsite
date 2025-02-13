# announce/forms.py
from django import forms
from .models import Message,Announcement
from ELW.models import Students,Class
from django.forms.widgets import CheckboxSelectMultiple

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

class AnnouncementForm(forms.ModelForm):
    receivers = forms.ModelMultipleChoiceField(
        queryset=Students.objects.all().order_by('name'),  # 按学生姓名排序
        widget=CheckboxSelectMultiple,
        label='接收者',
        required=False
    )
    a_title = forms.CharField(label='公告标题', max_length=64, widget=forms.TextInput(attrs={'class': 'form-control'}))
    a_content = forms.CharField(label='公告内容', max_length=3000, widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Announcement
        fields = ['a_title', 'a_content', 'receivers']




#     class_field = forms.ModelMultipleChoiceField(
#         queryset=Class.objects.all().order_by('id'),
#         label='班级',
#         required=False
#     )
#     receivers = forms.ModelMultipleChoiceField(
#         queryset=Students.objects.none(),
#         widget=forms.CheckboxSelectMultiple,
#         label='接收者',
#         required=False
#     )
#     select_all = forms.BooleanField(
#         widget=forms.CheckboxInput(attrs={'class': 'select-all'}),
#         label='全选',
#         required=False,
#         initial=False
#     )
#
#     class Meta:
#         model = Announcement
#         fields = ['a_title', 'a_content', 'class_field', 'receivers', 'select_all']
#
#     def __init__(self, *args, **kwargs):
#         super(AnnouncementForm, self).__init__(*args, **kwargs)
#         if 'class_field' in self.data:
#             class_id = self.data.get('class_field')
#             if class_id:
#                 self.fields['receivers'].queryset = Students.objects.filter(
#                     class_instance_id=class_id).order_by('name')