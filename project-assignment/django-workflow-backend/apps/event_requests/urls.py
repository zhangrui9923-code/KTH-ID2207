from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventRequestViewSet

router = DefaultRouter()
router.register(r'event-requests', EventRequestViewSet, basename='event-request')

urlpatterns = [
    path('', include(router.urls)),
]