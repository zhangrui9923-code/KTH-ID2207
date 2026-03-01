# apps/recruitments/views.py
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Recruitment
from .serializers import RecruitmentSerializer


def _role_upper(user) -> str:
    return (getattr(user, "role", "") or "").upper()


def is_pm(user) -> bool:
    # 允许 PM / SM / Admin（也兼容 superuser）
    role = _role_upper(user)
    return role in {"PM", "SM", "PRODUCT_MANAGER", "SERVICE_MANAGER", "ADMIN"} or user.is_superuser


def is_hr(user) -> bool:
    # 允许 HR / Admin；兼容 is_staff/superuser 作为 HR 权限
    role = _role_upper(user)
    return role in {"HR", "ADMIN"} or user.is_staff or user.is_superuser


class RecruitmentViewSet(viewsets.ModelViewSet):
    """
    /api/recruitments/ 资源：
      - list / retrieve / create / partial_update
      - 动作：submit / accept / add_hires / complete / reject
    """
    queryset = Recruitment.objects.all().order_by("-created_at")
    serializer_class = RecruitmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 后端强制注入 requester
        serializer.save(requester=self.request.user)

    # ---------- Actions ----------

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        rec = self.get_object()
        # 只有申请人（PM/SM）或管理员可以 submit；并且必须 pending
        if not is_pm(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if rec.status != "pending":
            return Response({"detail": "Only pending can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
        rec.status = "submitted"
        rec.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(rec).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        rec = self.get_object()
        if not is_hr(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if rec.status != "submitted":
            return Response({"detail": "Only submitted can be accepted."}, status=status.HTTP_400_BAD_REQUEST)
        rec.status = "in_progress"
        rec.hr_handler = request.user
        rec.started_at = timezone.now()
        rec.save(update_fields=["status", "hr_handler", "started_at", "updated_at"])
        return Response(self.get_serializer(rec).data)

    @action(detail=True, methods=["post"])
    def add_hires(self, request, pk=None):
        rec = self.get_object()
        if not is_hr(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if rec.status != "in_progress":
            return Response({"detail": "Only in_progress can add hires."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            count = int(request.data.get("count", 0))
        except (TypeError, ValueError):
            return Response({"detail": "count must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        if count <= 0:
            return Response({"detail": "count must be > 0."}, status=status.HTTP_400_BAD_REQUEST)

        if rec.positions_filled + count > rec.number_of_positions:
            return Response({"detail": "Exceeds number_of_positions."}, status=status.HTTP_400_BAD_REQUEST)

        rec.positions_filled += count
        rec.candidates_interviewed = max(rec.candidates_interviewed, rec.positions_filled)
        rec.save(update_fields=["positions_filled", "candidates_interviewed", "updated_at"])
        return Response(self.get_serializer(rec).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        rec = self.get_object()
        if not is_hr(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if rec.status != "in_progress":
            return Response({"detail": "Only in_progress can be completed."}, status=status.HTTP_400_BAD_REQUEST)
        if rec.positions_filled <= 0:
            return Response({"detail": "Cannot complete with zero hires."}, status=status.HTTP_400_BAD_REQUEST)

        rec.status = "completed"
        rec.completed_at = timezone.now()
        rec.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(self.get_serializer(rec).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        rec = self.get_object()
        if not is_hr(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if rec.status in {"completed", "rejected"}:
            return Response({"detail": "Already completed or rejected."}, status=status.HTTP_400_BAD_REQUEST)

        reason = (request.data.get("reason") or "").strip()
        if reason:
            # 追加到 hr_notes（保留历史）
            rec.hr_notes = (rec.hr_notes or "") + (("\n" if rec.hr_notes else "") + f"Reject: {reason}")
        rec.status = "rejected"
        rec.save(update_fields=["status", "hr_notes", "updated_at"])
        return Response(self.get_serializer(rec).data)
