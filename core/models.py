# core/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone

class AuditModel(models.Model):
    """
    Абстрактная модель для аудита: кто/когда создал и редактировал запись.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, editable=False,
        related_name="%(class)s_created"
    )
    created_at = models.DateTimeField(
        default=timezone.now, editable=False
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, editable=False,
        related_name="%(class)s_modified"
    )
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(exist=True)


class SoftDeleteModel(models.Model):
    """
    Абстрактная модель для soft-delete: вместо физического удаления
    выставляем exist=False.
    """
    exist = models.BooleanField(default=True, db_index=True)

    objects = SoftDeleteManager()   # «живые» записи
    all_objects = models.Manager()  # все, включая «удалённые»

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        # soft-delete
        self.exist = False
        self.save(update_fields=["exist"])

class City(AuditModel, SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name