from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    # "media_files" não está no ModelForm, processar manualmente na view
    class Meta:
        model = Post
        fields = ['content_type', 'description']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
