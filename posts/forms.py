# posts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Post, Comment

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        # password1 & password2 are added automatically by UserCreationForm
        fields = ['username', 'email', 'role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Write your post content here...'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'}),
        }