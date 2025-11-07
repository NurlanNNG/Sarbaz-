# accounts/urls.py
from django.urls import path
from .views import (
    MeView, RegisterView, RegisterConfirmView,
    PasswordResetView, PasswordResetConfirmView,
    CookieTokenObtainPairView, CookieTokenBlacklistView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('me/', MeView.as_view(), name='auth_me'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('register/confirm/', RegisterConfirmView.as_view(), name='auth_register_confirm'),
    path('password_reset/', PasswordResetView.as_view(), name='auth_password_reset'),
    path('password_reset/confirm/', PasswordResetConfirmView.as_view(), name='auth_password_reset_confirm'),
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/logout/', CookieTokenBlacklistView.as_view(), name='token_blacklist'),
]
