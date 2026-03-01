from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import BudgetApproval
from .serializers import BudgetApprovalSerializer, BudgetApprovalDecisionSerializer


class BudgetApprovalViewSet(viewsets.ModelViewSet):
    """
    预算审批视图集
    
    - SM/PM: 可以创建和查看自己的预算申请
    - FM: 可以查看所有申请并做出决策
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'decide':
            return BudgetApprovalDecisionSerializer
        return BudgetApprovalSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # FM 可以查看所有申请
        if user.role == 'fm':
            return BudgetApproval.objects.all()
        
        # SM/PM 只能查看自己创建的申请
        if user.role in ['sm', 'pm']:
            return BudgetApproval.objects.filter(requester=user)
        
        # 其他角色无权访问
        return BudgetApproval.objects.none()
    
    def perform_create(self, serializer):
        # 序列化器会自动设置 requester 和 status
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        
        # 只有 FM 可以更新
        if user.role != 'fm':
            return Response(
                {"detail": "只有 Financial Manager 可以处理预算申请"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 只能更新 submitted 状态的申请
        if instance.status != 'submitted':
            return Response(
                {"detail": f"无法处理状态为 '{instance.status}' 的申请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def decide(self, request, pk=None):
        """
        FM 对预算申请做出决策
        
        POST /api/budget-approvals/{id}/decide/
        {
            "fm_decision": "批准理由或拒绝理由",
            "status": "approved" 或 "rejected"
        }
        """
        instance = self.get_object()
        user = request.user
        
        # 检查权限
        if user.role != 'fm':
            return Response(
                {"detail": "只有 Financial Manager 可以做出决策"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查状态
        if instance.status != 'submitted':
            return Response(
                {"detail": f"无法处理状态为 '{instance.status}' 的申请"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            BudgetApprovalSerializer(instance).data,
            status=status.HTTP_200_OK
        )
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # 支持状态过滤
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 支持相关事件过滤
        event_id = request.query_params.get('related_event')
        if event_id:
            queryset = queryset.filter(related_event_id=event_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)