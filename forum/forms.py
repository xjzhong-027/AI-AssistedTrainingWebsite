from django import forms
from .models import Post
from .models import Comment
class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content','is_anonymous','is_public']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content','is_anonymous']