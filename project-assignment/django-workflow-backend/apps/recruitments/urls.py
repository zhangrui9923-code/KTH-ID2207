from rest_framework.routers import DefaultRouter
from .views import RecruitmentViewSet

router = DefaultRouter()
router.register(r"recruitments", RecruitmentViewSet, basename="recruitment")

urlpatterns = router.urls
