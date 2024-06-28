from django.urls import path
from core_account.views import (GoogleSocialAuthView, Register, UserLogin)


urlpatterns = [
    path('user/auth/google', GoogleSocialAuthView.as_view()),
    path('user/account/register', Register.as_view()),
    path('user/account/login', UserLogin.as_view()),
]
