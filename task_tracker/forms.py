from django import forms
from .models import UserProfile

# Form for updating phone number
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']  # Include only phone_number in the form
