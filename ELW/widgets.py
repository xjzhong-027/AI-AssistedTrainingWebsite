from django.forms.widgets import Input

class MultipleFileInput(Input):
    input_type = 'file'
    needs_multipart_form = True  # 确保表单支持文件上传

    def __init__(self, attrs=None):
        # 添加 multiple 属性
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        # 获取多文件上传的数据
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return None