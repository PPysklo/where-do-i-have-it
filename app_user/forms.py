from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.forms.widgets import PasswordInput, TextInput


from .models import CustomUser


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
