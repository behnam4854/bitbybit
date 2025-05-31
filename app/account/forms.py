from django.forms import ModelForm, TextInput

from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)


class SignUpForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
