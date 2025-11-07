# applications/models.py

from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from core.models import AuditModel, City, SoftDeleteModel

# Справочник состояний здоровья
class HealthStatusChoice(AuditModel, SoftDeleteModel):
    code = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Уникальный код статуса здоровья"
    )
    name = models.CharField(
        max_length=100,
        help_text="Читаемое название статуса (годен, негоден, годен с ограничениями и т.п.)"
    )

    def __str__(self):
        return self.name



class ServiceType(AuditModel, SoftDeleteModel):
    code = models.SlugField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Advantage(AuditModel, SoftDeleteModel):
    code = models.SlugField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ServiceTypeAdvantage(models.Model):
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, related_name="advantages"
    )
    advantage = models.ForeignKey(
        Advantage, on_delete=models.CASCADE, related_name="service_types"
    )

    class Meta:
        unique_together = ("service_type", "advantage")


class ApplicationStatus(AuditModel, SoftDeleteModel):
    code = models.SlugField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EducationLevel(AuditModel, SoftDeleteModel):
    code = models.SlugField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Specialization(AuditModel, SoftDeleteModel):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class MilitaryBranch(AuditModel, SoftDeleteModel):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Rank(AuditModel, SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Application(AuditModel, SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="applications", db_index=True
    )
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.PROTECT,
        related_name="applications", db_index=True
    )
    status = models.ForeignKey(
        ApplicationStatus, on_delete=models.PROTECT,
        related_name="applications", default=1, db_index=True
    )

    # Основные поля
    full_name = models.CharField(max_length=255, db_index=True)
    date_of_birth = models.DateField(db_index=True)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=12, db_index=True)
    birth_city = models.ForeignKey(
        City, on_delete=models.SET_NULL,
        null=True, related_name="birth_applications"
    )
    address = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    # Образование
    education_level = models.ForeignKey(
        EducationLevel, on_delete=models.PROTECT,
        related_name="applications",
        null=True,
        blank=True,
        help_text="Уровень образования (может быть пустым перед заполнением)"
    )
    specialization = models.ForeignKey(
        Specialization, on_delete=models.SET_NULL,
        null=True, related_name="applications"
    )
    graduation_place = models.CharField(max_length=255, blank=True)

    # Физические параметры и достижения
    sports_achievements = models.TextField(blank=True)
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    # Поля по типам службы
    # Для срочной службы — наличие приписного свидетельства
    has_conscript_certificate = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Наличие приписного свидетельства (для срочной службы)"
    )
    # Для контрактной службы — наличие военного билета
    has_military_ticket = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Наличие военного билета (для контрактной службы)"
    )
    # Для контрактной службы — прохождение военной кафедры
    has_military_faculty = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Наличие прохождения военной кафедры (для контрактной службы)"
    )

    # Текущее звание (при наличии)
    current_rank = models.ForeignKey(
        Rank, on_delete=models.SET_NULL,
        null=True, related_name="applications"
    )
    # Предпочтительный род войск
    preferred_branch = models.ForeignKey(
        MilitaryBranch, on_delete=models.SET_NULL,
        null=True, related_name="applications"
    )

    # Состояние здоровья и комментарий
    health_status = models.ForeignKey(
        HealthStatusChoice, on_delete=models.PROTECT,
        related_name="applications",
        null=True,
        help_text="Состояние здоровья"
    )
    health_comment = models.TextField(
        blank=True,
        help_text="Комментрарии по состоянию здоровья (описание болезней и т.п.)"
    )

    # Комментарий администратора при review
    admin_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

        # ИИН: 12 цифр
    iin = models.CharField(
        max_length=12,
        unique=True,
        validators=[RegexValidator(r'^\d{12}$', 'ИИН должен быть из 12 цифр.')],
        help_text="Индивидуальный идентификационный номер (12 цифр)"
    )

    has_deferment = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Наличие отсрочки"
    )
    deferment_reason = models.TextField(
        blank=True,
        help_text="Причина отсрочки (если есть)"
    )

    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GPA (например, 3.75)"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.service_type.name})"


class ApplicationCity(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE,
        related_name="desired_cities"
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE,
        related_name="applications"
    )

    class Meta:
        unique_together = ("application", "city")


class Attachment(AuditModel, SoftDeleteModel):
    ATTACHMENT_TYPE_CHOICES = [
        ("resume", "Резюме"),
        ("photo", "Фото"),
        ("diploma", "Диплом"),
        ("attestat", "Аттестат"),
        ("id_document", "Удостоверение личности"),
        ("conscript_ticket", "Приписной билет"),
    ]
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="applications/%Y/%m/")
    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Тип вложения"
    )

    def __str__(self):
        return f"{self.attachment_type} for {self.application_id}"
