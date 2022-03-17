from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import EmailInput, PasswordInput, TextInput
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import Profile
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=20, min_length=8, label=_('Password'), widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': _('From 8 to 20 characters')}))
    password2 = forms.CharField(label=_('Repeat password'), widget=PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=15, label=_('Username'), widget=TextInput(attrs={'class': 'form-control', 'placeholder': _('Maximum 15 characters')}))
    email = forms.EmailField(label='Email', widget=EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter a valid e-mail')}))

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
            raise forms.ValidationError(_("Passwords don't match."))
        return cd['password2']


class PasswordChangeCustomForm(PasswordChangeForm):
    old_password = forms.CharField(label=_('Old_password'),min_length=8, max_length=20, widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label=_('New Password'),min_length=8, max_length=20, widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': _('From 8 to 20 characters')}))
    new_password2 = forms.CharField(label=_('Confirm new password'),min_length=8, max_length=20, widget=PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def clean(self): # clean + field name, displays ValidationError as field error, standalone clean - non.field_error
        if self.cleaned_data.get('new_password1') == self.cleaned_data.get('old_password'):
           raise forms.ValidationError(_("New password can't be the same as the old one."))
        return self.cleaned_data
    

class PasswordResetCustomForm(PasswordResetForm):
    email = forms.CharField(label='E-mail', widget=EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email',)


class PasswordResetConfirmCustomForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("New password"), widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label=_('Confirm new password'), widget=PasswordInput(attrs={'class': 'form-control'}))

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
            'post_code_city': _('Post code and City'),
            'phone_number': _('Phone number'),
        }
