# applications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceTypeViewSet, ApplicationViewSet

router = DefaultRouter()
router.register(r"services", ServiceTypeViewSet, basename="service")
router.register(r"applications", ApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]
