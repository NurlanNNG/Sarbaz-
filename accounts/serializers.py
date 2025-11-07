from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import ConfirmationCode, CustomUser
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Для вывода профиля в /auth/me/
    """
    class Meta:
        model = CustomUser
        fields = ('id','username','email','first_name','last_name','phone','birth_city')
        read_only_fields = fields


class RegistrationSerializer(serializers.ModelSerializer):
    """
    При регистрации сразу создаёт пользователя с is_active=False
    и передаёт поле phone в create_user, чтобы избежать пустого ''.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.RegexField(
        regex=r'^\+7\d{10}$',
        error_messages={
            'invalid': 'Телефон должен быть в формате +7XXXXXXXXXX.'
        },
        write_only=True
    )  # обязательное поле

    class Meta:
        model = User  # это ваш CustomUser
        fields = ('username', 'email', 'password',
                  'first_name', 'last_name', 'phone')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email уже занят.")
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Этот номер телефона уже зарегистрирован.")
        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        # передаём phone сразу в create_user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=phone,
            is_active=False,   # до подтверждения
        )
        return user


class RegistrationConfirmSerializer(serializers.Serializer):
    """
    Подтверждает регистрацию: принимает код и активирует пользователя.
    """
    code = serializers.CharField(max_length=6)

    def validate_code(self, code):
        try:
            obj = ConfirmationCode.objects.get(
                code=code,
                type='registration',
                is_used=False,
                created_at__gte=timezone.now() - timedelta(minutes=15)
            )
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError("Неверный или просроченный код.")
        return obj

    def save(self):
        obj = self.validated_data['code']
        user = obj.user
        user.is_active = True
        user.save()
        obj.is_used = True
        obj.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    """
    Отправка кода сброса пароля на email.
    """
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Подтверждение сброса пароля: код + новый пароль.
    """
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_code(self, code):
        try:
            obj = ConfirmationCode.objects.get(
                code=code,
                type='password_reset',
                is_used=False,
                created_at__gte=timezone.now() - timedelta(minutes=15)
            )
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError("Неверный или просроченный код.")
        return obj

    def save(self):
        obj = self.validated_data['code']
        user = obj.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        obj.is_used = True
        obj.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Сообщаем сериализатору, что он должен искать пользователя по полю 'email'
    username_field = 'email'