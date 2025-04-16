from django import forms
from .models import Subscriber

class SubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        })
    )
    
    class Meta:
        model = Subscriber
        fields = ['email'] 