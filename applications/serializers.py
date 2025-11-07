# applications/serializers.py

from rest_framework import serializers
from .models import (
    City, ServiceType, Advantage, ServiceTypeAdvantage,
    ApplicationStatus, EducationLevel, Specialization,
    MilitaryBranch, Rank, HealthStatusChoice,
    Application, ApplicationCity, Attachment
)

# 1. Справочники — простые ModelSerializer’ы
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'code', 'name', 'description']


class AdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantage
        fields = ['id', 'code', 'name', 'description']


class ServiceTypeAdvantageSerializer(serializers.ModelSerializer):
    advantage = AdvantageSerializer(read_only=True)
    advantage_id = serializers.PrimaryKeyRelatedField(
        source='advantage', queryset=Advantage.objects.all(), write_only=True
    )

    class Meta:
        model = ServiceTypeAdvantage
        fields = ['service_type', 'advantage', 'advantage_id']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = ['id', 'code', 'name']


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = ['id', 'code', 'name']


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name']


class MilitaryBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilitaryBranch
        fields = ['id', 'name']


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ['id', 'name']


class HealthStatusChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthStatusChoice
        fields = ['id', 'code', 'name']


# 2. Вложенные объекты заявки
class ApplicationCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationCity
        fields = ['city']


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'attachment_type']


# 3. Главный сериализатор заявки
class ApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    service_type = serializers.SlugRelatedField(
        slug_field='code', queryset=ServiceType.objects.all()
    )
    status = serializers.SlugRelatedField(
        slug_field='code', queryset=ApplicationStatus.objects.all(), required=False
    )
    birth_city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), allow_null=True, required=False
    )
    education_level = serializers.PrimaryKeyRelatedField(
        queryset=EducationLevel.objects.all(), allow_null=True, required=False
    )
    specialization = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), allow_null=True, required=False
    )
    current_rank = serializers.PrimaryKeyRelatedField(
        queryset=Rank.objects.all(), allow_null=True, required=False
    )
    preferred_branch = serializers.PrimaryKeyRelatedField(
        queryset=MilitaryBranch.objects.all(), allow_null=True, required=False
    )
    health_status = serializers.PrimaryKeyRelatedField(
        queryset=HealthStatusChoice.objects.all(), allow_null=True, required=False
    )

    desired_cities = ApplicationCitySerializer(many=True, read_only=True)
    new_cities = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False,
        help_text="IDs городов (желаемые)"
    )

    attachments = AttachmentSerializer(many=True, read_only=True)
    new_files = serializers.ListField(
        child=serializers.FileField(), write_only=True,
        required=False, help_text="Файлы для загрузки"
    )

    class Meta:
        model = Application
        fields = [
            'id','user','service_type','status',
            'full_name','date_of_birth','email','phone','birth_city','address','comment',
            'education_level','specialization','graduation_place',
            'sports_achievements','height_cm','weight_kg',
            'has_conscript_certificate','has_military_ticket','has_military_faculty',
            'current_rank','preferred_branch',
            'health_status','health_comment','admin_comment',
            'desired_cities','new_cities',
            'attachments','new_files',
            'created_at','created_by','modified_at','modified_by',
            'iin', 'has_deferment', 'deferment_reason', 'gpa',
        ]
        read_only_fields = ['id','created_at','created_by','modified_at','modified_by','admin_comment','status']

    def _save_cities(self, application, city_ids):
        # чистим старые и создаём новые связи
        ApplicationCity.objects.filter(application=application).delete()
        for cid in city_ids:
            ApplicationCity.objects.create(application=application, city_id=cid)

    def _save_files(self, application, files):
        for f in files:
            Attachment.objects.create(
                application=application,
                file=f,
                created_by=self.context['request'].user,
                modified_by=self.context['request'].user
            )

    def create(self, validated_data):
        city_ids = validated_data.pop('new_cities', [])
        files = validated_data.pop('new_files', [])
        app = super().create(validated_data)
        if city_ids:
            self._save_cities(app, city_ids)
        if files:
            self._save_files(app, files)
        return app

    def update(self, instance, validated_data):
        city_ids = validated_data.pop('new_cities', [])
        files = validated_data.pop('new_files', [])
        app = super().update(instance, validated_data)
        if city_ids is not None:
            self._save_cities(app, city_ids)
        if files:
            self._save_files(app, files)
        return app
