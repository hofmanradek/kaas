from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    """
    User login form
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    """
    New user registration form
    """
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class KnapsakTextArea(forms.Form):
    """
    Text area where user can copy paste JSON with knapsack task definition
    """
    knapsack_json = forms.CharField(widget=forms.Textarea, label='')
