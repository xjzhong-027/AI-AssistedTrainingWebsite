from django import forms
from .models import ClassroomLayout
from Account.models import ClassScheduleAdjustment, ClassScheduleAddition, Class



class AttendanceQueryForm(forms.Form):
    """ 考勤查询表单 """
    week = forms.IntegerField(min_value=1, label='周次', required=False)
    class_field = forms.ChoiceField(label='班级', required=True, choices=[])

    def __init__(self, *args, **kwargs):
        class_choices = kwargs.pop('class_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['class_field'].choices = class_choices


class ClassScheduleAdjustmentForm(forms.ModelForm):
    """ 调课表单 """
    class_instance = forms.ModelChoiceField(queryset=Class.objects.none(), label="班级", required=True)
    week = forms.IntegerField(min_value=1, label="周次", required=True)
    new_week_day = forms.ChoiceField(choices=ClassScheduleAdjustment._meta.get_field('new_week_day').choices, label="调整后的上课星期", required=True)
    new_class_begin_time = forms.TimeField(label="调整后的上课时间", required=True)
    new_class_end_time = forms.TimeField(label="调整后的下课时间", required=True)

    class Meta:
        model = ClassScheduleAdjustment
        fields = ['class_instance', 'week', 'new_week_day', 'new_class_begin_time', 'new_class_end_time']

    def __init__(self, *args, **kwargs):
        class_choices = kwargs.pop('class_choices', None)
        super().__init__(*args, **kwargs)
        if class_choices:
            self.fields['class_instance'].queryset = class_choices


class ClassScheduleAdditionForm(forms.ModelForm):
    """ 补课表单 """
    class_instance = forms.ModelChoiceField(queryset=Class.objects.none(), label="班级", required=True)
    week = forms.IntegerField(min_value=1, label="周次", required=True)
    weekday = forms.ChoiceField(choices=ClassScheduleAddition._meta.get_field('weekday').choices, label="上课星期", required=True)
    class_begin_time = forms.TimeField(label="上课时间", required=True)
    class_end_time = forms.TimeField(label="下课时间", required=True)

    class Meta:
        model = ClassScheduleAddition
        fields = ['class_instance', 'week', 'weekday', 'class_begin_time', 'class_end_time']

    def __init__(self, *args, **kwargs):
        class_choices = kwargs.pop('class_choices', None)
        super().__init__(*args, **kwargs)
        if class_choices:
            self.fields['class_instance'].queryset = class_choices


class ClassroomLayoutForm(forms.ModelForm):
    """ 课室设置表单 """
    class_instance = forms.ModelChoiceField(queryset=Class.objects.all(), widget=forms.HiddenInput, required=True)
    seat_rows = forms.IntegerField(min_value=1, label="行数", required=True)
    seat_cols = forms.IntegerField(min_value=1, label="列数", required=True)

    class Meta:
        model = ClassroomLayout
        fields = ['class_instance', 'seat_rows', 'seat_cols']

    def __init__(self, *args, **kwargs):
        class_obj = kwargs.pop('class_obj')  # 从视图传递过来的 class_obj
        super().__init__(*args, **kwargs)
        self.fields['class_instance'].initial = class_obj
        self.fields['class_instance'].disabled = True


# class ReevaluationForm(forms.Form):
#     """ 重新评分表单 """
#     class_name = forms.CharField(max_length=200, required=True, label="班级名称")
#     unit_name = forms.CharField(max_length=100, required=True, label="单元名称")
#     category = forms.ChoiceField(choices=Unit.TYPES, required=True, label="单元类别")

