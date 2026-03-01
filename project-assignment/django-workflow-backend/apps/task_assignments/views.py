from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import TaskAssignment
from .serializers import (
    TaskAssignmentListSerializer,
    TaskAssignmentDetailSerializer,
    TaskAssignmentCreateSerializer,
    TaskAssignmentUpdateSerializer,
    EmployeePlanSubmitSerializer,
)
from .permissions import IsManagerOrEmployee


class TaskAssignmentViewSet(viewsets.ModelViewSet):
    """
    任务分配视图集

    提供以下功能：
    - list: 获取任务列表（根据用户角色过滤）
    - retrieve: 获取任务详情
    - create: 创建任务（仅Manager）
    - update/partial_update: 更新任务（仅Manager）
    - destroy: 删除任务（仅Manager）
    - submit_plan: 员工提交计划和预算
    - send_to_employee: Manager发送任务给员工
    - complete: Manager标记任务完成
    - my_assigned_tasks: 获取我分配的任务（Manager）
    - my_received_tasks: 获取我接收的任务（Employee）
    """
    permission_classes = [IsAuthenticated, IsManagerOrEmployee]

    def get_queryset(self):
        """
        根据用户角色返回不同的查询集
        - Manager: 可以看到自己分配的所有任务
        - Employee: 只能看到已发送给自己的任务（排除pending状态）
        """
        user = self.request.user

        # 如果有特定的action，使用对应的queryset
        if self.action == 'my_assigned_tasks':
            return TaskAssignment.objects.filter(manager=user)
        elif self.action == 'my_received_tasks':
            return TaskAssignment.objects.filter(employee=user)

        # 检查是否是员工视图（从查询参数判断）
        employee_view = self.request.query_params.get('employee_view', '').lower() == 'true'
        
        if employee_view:
            # 员工只能看到已发送给自己的任务（排除 pending 状态）
            return TaskAssignment.objects.filter(
                employee=user
            ).exclude(
                status='pending'
            ).select_related('manager', 'employee')
        
        # 默认返回与用户相关的所有任务
        return TaskAssignment.objects.filter(
            Q(manager=user) | Q(employee=user)
        ).select_related('manager', 'employee')

    def get_serializer_class(self):
        """根据不同的action返回不同的序列化器"""
        if self.action == 'list':
            return TaskAssignmentListSerializer
        elif self.action == 'retrieve':
            return TaskAssignmentDetailSerializer
        elif self.action == 'create':
            return TaskAssignmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskAssignmentUpdateSerializer
        elif self.action == 'submit_plan':
            return EmployeePlanSubmitSerializer
        return TaskAssignmentDetailSerializer

    def create(self, request, *args, **kwargs):
        """创建任务（仅Manager）"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 返回详细信息
        instance = serializer.instance
        detail_serializer = TaskAssignmentDetailSerializer(instance)

        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """更新任务（仅Manager）"""
        instance = self.get_object()

        # 检查是否是manager
        if instance.manager != request.user:
            return Response(
                {'detail': '只有任务创建者可以更新任务'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除任务（仅Manager）"""
        instance = self.get_object()

        # 检查是否是manager
        if instance.manager != request.user:
            return Response(
                {'detail': '只有任务创建者可以删除任务'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def submit_plan(self, request, pk=None):
        """
        员工提交工作计划和预算
        POST /api/task-assignments/{id}/submit_plan/
        """
        instance = self.get_object()

        # 检查是否是被分配的员工
        if instance.employee != request.user:
            return Response(
                {'detail': '只有被分配的员工可以提交计划'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 检查状态
        if instance.status not in ['sent_to_employee', 'plan_submitted']:
            return Response(
                {'detail': f'当前状态（{instance.get_status_display()}）不允许提交计划'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EmployeePlanSubmitSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 返回详细信息
        detail_serializer = TaskAssignmentDetailSerializer(instance)
        return Response(detail_serializer.data)

    @action(detail=True, methods=['post'])
    def send_to_employee(self, request, pk=None):
        """
        Manager发送任务给员工
        POST /api/task-assignments/{id}/send_to_employee/
        """
        instance = self.get_object()

        # 检查是否是manager
        if instance.manager != request.user:
            return Response(
                {'detail': '只有任务创建者可以发送任务'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 检查状态
        if instance.status != 'pending':
            return Response(
                {'detail': f'当前状态（{instance.get_status_display()}）不允许发送'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = 'sent_to_employee'
        instance.save()

        serializer = TaskAssignmentDetailSerializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Manager标记任务完成
        POST /api/task-assignments/{id}/complete/
        """
        instance = self.get_object()

        # 检查是否是manager
        if instance.manager != request.user:
            return Response(
                {'detail': '只有任务创建者可以标记完成'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 检查状态
        if instance.status not in ['plan_submitted']:
            return Response(
                {'detail': f'当前状态（{instance.get_status_display()}）不允许标记完成'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = 'completed'
        instance.save()

        serializer = TaskAssignmentDetailSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_assigned_tasks(self, request):
        """
        获取我分配的任务（Manager视角）
        GET /api/task-assignments/my_assigned_tasks/
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 支持状态过滤
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TaskAssignmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskAssignmentListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_received_tasks(self, request):
        """
        获取我接收的任务（Employee视角）
        GET /api/task-assignments/my_received_tasks/
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 支持状态过滤
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TaskAssignmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskAssignmentListSerializer(queryset, many=True)
        return Response(serializer.data)