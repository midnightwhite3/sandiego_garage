from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from .forms import PasswordChangeCustomForm, PasswordResetCustomForm, UserEditForm, UserRegistrationForm, PasswordResetConfirmCustomForm, ProfileEditForm
from .models import Profile
# Create your views here.

    
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            return redirect('register_complete')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


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

