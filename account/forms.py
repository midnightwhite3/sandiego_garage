from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import EmailInput, PasswordInput, TextInput
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=20, min_length=8, label='Password', widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'From 8 to 20 characters'}))
    password2 = forms.CharField(label='Repeat password', widget=PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=15, label='Username', widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Maximum 15 characters'}))
    email = forms.EmailField(label='Email', widget=EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter a valid e-mail'}))

    class Meta:
        model = User
        fields = ('username', 'email')
    
        # widgets = {
        #     'username': forms.TextInput(attrs={'class': 'form-control'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control'}),
        # }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']


class PasswordChangeCustomForm(PasswordChangeForm):
    old_password = forms.CharField(min_length=8, max_length=20, widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label='New Password',min_length=8, max_length=20, widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'From 8 to 20 characters'}))
    new_password2 = forms.CharField(label='Confirm new password',min_length=8, max_length=20, widget=PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def clean(self): # clean + field name, displays ValidationError as field error, standalone clean - non.field_error
        if self.cleaned_data.get('new_password1') == self.cleaned_data.get('old_password'):
           raise forms.ValidationError("New password can't be the same as the old one.")
        return self.cleaned_data
    

class PasswordResetCustomForm(PasswordResetForm):
    email = forms.CharField(label='E-mail', widget=EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email',)


class PasswordResetConfirmCustomForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New password", widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='Confirm new password', widget=PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)

        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_adress': forms.TextInput(attrs={'class': 'form-control'}),
            'post_code_city': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'nip': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'post_code_city': 'Post code and City'
        }
