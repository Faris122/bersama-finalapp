from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class DiscussionForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=DiscussionCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select up to 3 categories.",
        required=True
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'categories']

    def clean_categories(self):
        selected_categories = self.cleaned_data['categories']
        if len(selected_categories) > 3:
            raise forms.ValidationError("You can select a maximum of 3 categories.")
        return selected_categories

class DiscussionCommentForm(forms.ModelForm):
    class Meta:
        model = DiscussionComment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Write your comment...'})