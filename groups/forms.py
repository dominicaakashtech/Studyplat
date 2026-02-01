from django import forms
from .models import StudyGroup, Resource, Message, StudySession

class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'subject', 'description', 'max_members', 'is_private']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mathematics, Physics'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your study group'}),
            'max_members': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 100}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'resource_type', 'description', 'file', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Type your message...'}),
        }

class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['title', 'description', 'scheduled_time', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15}),
        }
