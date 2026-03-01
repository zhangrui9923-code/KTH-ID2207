from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskAssignmentViewSet

app_name = 'task_assignments_api'

# 创建DRF路由器
router = DefaultRouter()
router.register(r'task-assignments', TaskAssignmentViewSet, basename='taskassignment')

urlpatterns = [
    path('', include(router.urls)),
]