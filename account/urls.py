from django.urls import path
from django.contrib.auth import views as auth_views
from .views import edit_profile, register, register_complete, PasswordChangeCustomView, PasswordResetCustomView, PasswordResetConfirmCustomView, activate_account, confirm_mail_message

urlpatterns = [
    #Login views
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('register_complete', register_complete, name='register_complete'),
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_change/', PasswordChangeCustomView.as_view(), name='password_change'),
    path('password_reset/', PasswordResetCustomView.as_view(), name='password_reset'),
    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmCustomView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('activate_account/<uidb64>/<token>', activate_account, name='activate_account'),
    path('email_confirm_message/', confirm_mail_message, name='confirm_mail_message'),
]
