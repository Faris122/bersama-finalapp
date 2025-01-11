from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *
from account.models import *

class ResourceCommentForm(forms.ModelForm):
    class Meta:
        model = ResourceComment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Write your comment...'})

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'content', 'link', 'attachment', 'categories']

    categories = forms.ModelMultipleChoiceField(
        queryset=ResourceCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select up to 3 categories"
    )

    def clean_categories(self):
        categories = self.cleaned_data['categories']
        if categories.count() > 3:
            raise forms.ValidationError("You can select a maximum of 3 categories.")
        return categories