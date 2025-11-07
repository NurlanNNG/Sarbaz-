# accounts/views.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.settings import api_settings
from rest_framework.generics import GenericAPIView
from sarbaz_plus_backend.settings import JWT_COOKIE_HTTPONLY, JWT_COOKIE_NAME, JWT_COOKIE_SAMESITE, JWT_COOKIE_SECURE, JWT_REFRESH_COOKIE_NAME
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import EmailTokenObtainPairSerializer, RegistrationSerializer


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Возвращает 200 OK и сразу ставит два кук-файла:
      - access_token (срок из SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
      - refresh_token (срок из SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])
    """
    serializer_class = EmailTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Получаем стандартный ответ с токенами
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            # Очищаем тело ответа (не передаём токены в JSON)
            response.data = {"detail": "Успешный вход"}

            # Устанавливаем access_token
            access_exp = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
            response.set_cookie(
                JWT_COOKIE_NAME,
                data["access"],
                max_age=access_exp,
                httponly=JWT_COOKIE_HTTPONLY,
                secure=JWT_COOKIE_SECURE,
                samesite=JWT_COOKIE_SAMESITE,
                path="/",            # доступно для всех путей API
            )

            # Устанавливаем refresh_token
            refresh_exp = api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()
            response.set_cookie(
                JWT_REFRESH_COOKIE_NAME,
                data["refresh"],
                max_age=refresh_exp,
                httponly=JWT_COOKIE_HTTPONLY,
                secure=JWT_COOKIE_SECURE,
                samesite=JWT_COOKIE_SAMESITE,
                path="/",            # чтобы /api/token/refresh/ его видел
            )
        return response

class CookieTokenBlacklistView(TokenBlacklistView):
    """
    Logout: баним refresh и удаляем все JWT-куки у клиента.
    """
    def post(self, request, *args, **kwargs):
        # 1) баним refresh (стандартный функционал)
        resp = super().post(request, *args, **kwargs)
        # 2) чистим куки
        resp.delete_cookie('access_token', path='/')
        resp.delete_cookie('refresh_token', path='/')
        resp.delete_cookie('sessionid', path='/')
        # (не нужно трогать csrftoken, он может понадобиться дальше)
        resp.data = {'detail': 'Вы успешно вышли'}
        return resp
    
class RegisterView(GenericAPIView):
    """
    POST /api/auth/register/ — регистрация нового пользователя,
    is_active=False + отправка кода на почту (email).
    """
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # 1) создаем пользователя без JWT и без активации
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # пользователь is_active=False

        # 2) генерируем одноразовый код и сохраняем его
        code = f"{random.randint(0, 999999):06d}"
        ConfirmationCode.objects.create(
            user=user,
            code=code,
            type='registration',
            created_at=timezone.now()
        )

        # 3) шлём письмо
        send_mail(
            subject="Код подтверждения регистрации Sarbaz+",
            message=f"Ваш код: {code}\nОн действителен 15 минут.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Пользователь создан, код подтверждения выслан на email."},
            status=status.HTTP_201_CREATED
        )
    
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserSerializer,
    RegistrationConfirmSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from .models import ConfirmationCode

def _send_confirmation_code(user, to_email, code, code_type):
    send_mail(
        subject="Ваш код подтверждения",
        message=f"Ваш код: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False
    )
    ConfirmationCode.objects.create(
        user=user, code=code, type=code_type
    )

class MeView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterConfirmView(GenericAPIView):
    """
    POST /api/auth/register/confirm/ — принимает {"code":"123456"},
    активирует пользователя, выдаёт JWT-куки.
    """
    serializer_class = RegistrationConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # валидируем и активируем
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # внутри активирует user.is_active=True

        # генерируем JWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # собираем ответ с куки
        response = Response({'detail': 'Регистрация подтверждена'}, status=status.HTTP_200_OK)
        cookie_kwargs = {
            'httponly': settings.JWT_COOKIE_HTTPONLY,
            'secure': settings.JWT_COOKIE_SECURE,
            'samesite': settings.JWT_COOKIE_SAMESITE,
            'path': '/',
        }
        response.set_cookie(settings.JWT_COOKIE_NAME, str(access),
                            max_age=refresh.access_token.lifetime.total_seconds(),
                            **cookie_kwargs)
        response.set_cookie(settings.JWT_REFRESH_COOKIE_NAME, str(refresh),
                            max_age=refresh.lifetime.total_seconds(),
                            **cookie_kwargs)
        return response

class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # 1) Получаем сериализатор и валидируем входные данные
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2) Достаем user из validated_data
        #    (validate_email() у вас возвращает объект User)
        user = serializer.validated_data['email']

        # 3) Генерируем код и отправляем
        code = f"{random.randint(0, 999999):06d}"
        _send_confirmation_code(user, user.email, code, 'password_reset')

        return Response(
            {'detail': 'Код для сброса пароля выслан на ваш email'},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Пароль успешно изменён'}, status=status.HTTP_200_OK)
