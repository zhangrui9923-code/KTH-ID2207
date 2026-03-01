from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetApprovalViewSet

router = DefaultRouter()
router.register(r'budget-approvals', BudgetApprovalViewSet, basename='budget-approval')

urlpatterns = [
    path('', include(router.urls)),
]