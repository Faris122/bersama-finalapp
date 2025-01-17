from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

class ExtendedUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(required=False, max_length=10, label="Phone Number")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, initial='Public', label="Role")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                role=self.cleaned_data.get('role')
            )
        return user
    
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'is_phone_public', 'bio', 'profile_picture', 'website', 'is_dm_open']