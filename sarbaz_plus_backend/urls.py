from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from applications import views as app_views

schema_view = get_schema_view(
    openapi.Info(
        title="Sarbaz+ API",
        default_version='v1',
        description="Документация REST API для портала Sarbaz+",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

# Справочники
router.register(r'cities', app_views.CityViewSet)
router.register(r'service-types', app_views.ServiceTypeViewSet, basename='service-type')
router.register(r'advantages', app_views.AdvantageViewSet)
router.register(r'service-type-advantages', app_views.ServiceTypeAdvantageViewSet)
router.register(r'statuses', app_views.ApplicationStatusViewSet)
router.register(r'education-levels', app_views.EducationLevelViewSet)
router.register(r'specializations', app_views.SpecializationViewSet)
router.register(r'military-branches', app_views.MilitaryBranchViewSet)
router.register(r'ranks', app_views.RankViewSet)
router.register(r'health-statuses', app_views.HealthStatusChoiceViewSet)

# User API
router.register(r'applications', app_views.ApplicationViewSet, basename='application')

# Admin API (под префиксом /admin/applications/)
router.register(r'admin/applications', app_views.AdminApplicationViewSet, basename='admin-applications')


urlpatterns = [
    path('admin/', admin.site.urls),

    # аутентификация
    path('api/auth/', include('accounts.urls')),

    # CRUD-заявки
    path('api/', include(router.urls)),

    # Swagger UI (интерактивно «Try it out»)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Redoc (чистая документация)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
