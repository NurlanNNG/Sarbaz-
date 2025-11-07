# applications/views.py

from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    City, ServiceType, Advantage, ServiceTypeAdvantage,
    ApplicationStatus, EducationLevel, Specialization,
    MilitaryBranch, Rank, HealthStatusChoice,
    Application
)
from .serializers import (
    CitySerializer, ServiceTypeSerializer, AdvantageSerializer,
    ServiceTypeAdvantageSerializer, ApplicationStatusSerializer,
    EducationLevelSerializer, SpecializationSerializer,
    MilitaryBranchSerializer, RankSerializer,
    HealthStatusChoiceSerializer, ApplicationSerializer
)
from .permissions import IsOwnerAndEditable

# 1. Справочники
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAdminUser]


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    permission_classes = [permissions.AllowAny]


class AdvantageViewSet(viewsets.ModelViewSet):
    queryset = Advantage.objects.all()
    serializer_class = AdvantageSerializer
    permission_classes = [permissions.IsAdminUser]


class ServiceTypeAdvantageViewSet(viewsets.ModelViewSet):
    queryset = ServiceTypeAdvantage.objects.all()
    serializer_class = ServiceTypeAdvantageSerializer
    permission_classes = [permissions.IsAdminUser]


class ApplicationStatusViewSet(viewsets.ModelViewSet):
    queryset = ApplicationStatus.objects.all()
    serializer_class = ApplicationStatusSerializer
    permission_classes = [permissions.IsAdminUser]


class EducationLevelViewSet(viewsets.ModelViewSet):
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [permissions.IsAdminUser]


class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [permissions.IsAdminUser]


class MilitaryBranchViewSet(viewsets.ModelViewSet):
    queryset = MilitaryBranch.objects.all()
    serializer_class = MilitaryBranchSerializer
    permission_classes = [permissions.IsAdminUser]


class RankViewSet(viewsets.ModelViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    permission_classes = [permissions.IsAdminUser]


class HealthStatusChoiceViewSet(viewsets.ModelViewSet):
    queryset = HealthStatusChoice.objects.all()
    serializer_class = HealthStatusChoiceSerializer
    permission_classes = [permissions.IsAdminUser]


# 2. Пользовательские заявки
class ApplicationViewSet(viewsets.ModelViewSet):
    """
    CRUD-операции пользователя:
    - list/create/retrieve/update/destroy
    + two custom endpoints:
      POST /applications/communications/
      POST /applications/conscription/
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerAndEditable]

    def get_queryset(self):
        # 1) Если это вызов drf-yasg для генерации схемы (swagger),
        #    у view появится атрибут swagger_fake_view=True
        #    и request.user будет AnonymousUser, фильтр упадёт.
        #    Поэтому для таких «фейковых» вызовов сразу возвращаем пустой QuerySet:
        if getattr(self, 'swagger_fake_view', False):
            return Application.objects.none()

        # 2) Обычная логика: staff видит все, остальные — только свои
        qs = super().get_queryset()
        user = self.request.user
        return qs if user.is_staff else qs.filter(user=user)

    @action(detail=False, methods=['post'], url_path='communications')
    def communications(self, request):
        data = request.data.copy()
        data['service_type'] = 'contract'  # code контрактной службы
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='conscription')
    def conscription(self, request):
        data = request.data.copy()
        data['service_type'] = 'conscription'  # code срочной службы
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()  # soft-delete


# 3. Admin API для заявок
class AdminApplicationViewSet(viewsets.ModelViewSet):
    """
    Только для staff:
      GET    /admin/applications/
      PUT/PATCH /admin/applications/{id}/
      POST   /admin/applications/bulk_update_status/
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'], url_path='bulk_update_status')
    def bulk_update_status(self, request):
        ids = request.data.get('ids', [])
        new_status = request.data.get('status')
        comment = request.data.get('admin_comment', '')
        if not ids or not new_status:
            return Response({'detail': 'ids и status обязательны'}, status=400)
        apps = self.get_queryset().filter(id__in=ids)
        apps.update(
            status_id=ApplicationStatus.objects.get(code=new_status).id,
            admin_comment=comment,
            modified_by=request.user
        )
        return Response({'updated': apps.count()})
