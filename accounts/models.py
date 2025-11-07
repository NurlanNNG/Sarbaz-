from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

class ConfirmationCode(models.Model):
    """
    Хранит разовые коды для подтверждения email/телефона при регистрации
    и для сброса пароля.
    """
    TYPE_CHOICES = [
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="confirmation_codes"
    )
    code = models.CharField(max_length=6)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} – {self.type} – {self.code}"

class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=12,
        unique=True,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^\+7\d{10}$',
                message="Телефон должен быть в формате +7XXXXXXXXXX (11 цифр после +7)."
            )
        ],
        help_text="Телефон в формате +7XXXXXXXXXX"
    )
    birth_city = models.ForeignKey(
        'core.City',        # ссылка на модель City
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='residents',
        help_text="Город рождения"
    )
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username