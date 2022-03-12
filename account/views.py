from base64 import urlsafe_b64encode
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from .forms import PasswordChangeCustomForm, PasswordResetCustomForm, UserEditForm, UserRegistrationForm, PasswordResetConfirmCustomForm, ProfileEditForm
from .models import Profile
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
# Create your views here.

    
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            current_site = get_current_site(request)
            mail_subject = 'GarageApp, confirm your e-mail.'
            message = render_to_string('registration/confirm_mail.html',{
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_b64encode(force_bytes(new_user.pk)).decode(),
                'token': account_activation_token.make_token(new_user)
            })
            email_to = user_form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[email_to]
            )
            email.send()
            return redirect('confirm_mail_message')
            # return redirect('register_complete')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})

def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Cogratulations! You activated your account and can log in now.')
        return redirect('login')
    else:
        messages.error(request, 'Token invalid or expired.')
        return redirect('login')

def register_complete(request, *args, **kwargs):
    template = 'registration/register_complete.html'
    context = {}
    return render(request, template, context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


@method_decorator(login_required, name='dispatch')
class PasswordChangeCustomView(PasswordChangeView):
    form_class = PasswordChangeCustomForm
    fields = '__all__'


class PasswordResetCustomView(PasswordResetView):
    form_class = PasswordResetCustomForm
    fields = '__all__'


class PasswordResetConfirmCustomView(PasswordResetConfirmView):
    form_class = PasswordResetConfirmCustomForm
    fields = '__all__'


def confirm_mail_message(request, *args, **kwargs):
    template = 'registration/confirm_mail_message.html'
    context = {}
    return render(request, template, context)