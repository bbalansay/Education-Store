from django import forms

class RegistrationForm(forms.Form):
    """Form for registering new users with username, password email, first/last name"""
    username = forms.CharField(label='Username', max_length=30, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput,
    max_length=30, required=True)
    passwordconf = forms.CharField(label='Password confirmation', widget=forms.PasswordInput,
    max_length=30, required=True)
    email = forms.CharField(label='Email', max_length=30, required=True)
    first_name = forms.CharField(label='First name', max_length=30, required=True)
    last_name = forms.CharField(label='Last name', max_length=30, required=True)

class SigninForm(forms.Form):
    """Form for signing in users based on username and password"""
    username = forms.CharField(label='Username', max_length=30, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput,
    max_length=30, required=True)
