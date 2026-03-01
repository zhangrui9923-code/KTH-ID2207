from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import EventRequest
from .serializers import (
    EventRequestSerializer,
    EventRequestCreateSerializer,
    EventRequestSCSReviewSerializer,
    EventRequestFMReviewSerializer,
    EventRequestAdminReviewSerializer,
    EventRequestDetailsSerializer,
)


class EventRequestViewSet(viewsets.ModelViewSet):
    """
    事件请求视图集
    
    工作流程:
    1. CS 创建简表 (submitted)
    2. SCS 添加评论 (scs_reviewed)
    3. FM 添加反馈 (fm_reviewed)
    4. Admin 做决定 (approved/rejected)
    5. SCS 添加详细信息 (open)
    """
    queryset = EventRequest.objects.all()
    serializer_class = EventRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by', 'current_handler']
    search_fields = ['title', 'record_number', 'client_name']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EventRequestCreateSerializer
        return EventRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """Customer Service 创建事件请求（简表）"""
        # 验证用户角色
        if request.user.role != 'cs':
            return Response(
                {'error': '只有 Customer Service 可以创建事件请求'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # 返回完整信息
        instance = serializer.instance
        response_serializer = EventRequestSerializer(instance)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def scs_review(self, request, pk=None):
        """Senior Customer Service 添加评论"""
        event_request = self.get_object()
        
        # 验证用户角色
        if request.user.role != 'scs':
            return Response(
                {'error': '只有 Senior Customer Service 可以进行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventRequestSCSReviewSerializer(
            event_request,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # 更新状态和处理信息
        serializer.save(
            status='scs_reviewed',
            scs_handler=request.user,
            scs_handled_at=timezone.now()
        )
        
        # 返回完整信息
        response_serializer = EventRequestSerializer(event_request)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def fm_review(self, request, pk=None):
        """Financial Manager 添加反馈"""
        event_request = self.get_object()
        
        # 验证用户角色
        if request.user.role != 'fm':
            return Response(
                {'error': '只有 Financial Manager 可以进行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventRequestFMReviewSerializer(
            event_request,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # 更新状态和处理信息
        serializer.save(
            status='fm_reviewed',
            fm_handler=request.user,
            fm_handled_at=timezone.now()
        )
        
        # 返回完整信息
        response_serializer = EventRequestSerializer(event_request)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def admin_review(self, request, pk=None):
        """Admin Manager 做最终决定"""
        event_request = self.get_object()
        
        # 验证用户角色
        if request.user.role != 'admin':
            return Response(
                {'error': '只有 Admin Manager 可以进行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventRequestAdminReviewSerializer(
            event_request,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # 获取决定
        decision = serializer.validated_data.pop('decision')
        
        # 更新状态和处理信息
        serializer.save(
            status=decision,
            admin_handler=request.user,
            admin_handled_at=timezone.now()
        )
        
        # 返回完整信息
        response_serializer = EventRequestSerializer(event_request)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_details(self, request, pk=None):
        """Senior Customer Service 添加详细信息"""
        event_request = self.get_object()
        
        # 验证用户角色
        if request.user.role != 'scs':
            return Response(
                {'error': '只有 Senior Customer Service 可以添加详细信息'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = EventRequestDetailsSerializer(
            event_request,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # 更新状态
        serializer.save(status='open')
        
        # 返回完整信息
        response_serializer = EventRequestSerializer(event_request)
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """获取当前用户创建的请求"""
        queryset = self.queryset.filter(created_by=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_reviews(self, request):
        """获取待当前用户处理的请求"""
        user_role = request.user.role
        
        if user_role == 'scs':
            queryset = self.queryset.filter(status='submitted') | \
                       self.queryset.filter(status='approved')
        elif user_role == 'fm':
            queryset = self.queryset.filter(status='scs_reviewed')
        elif user_role == 'admin':
            queryset = self.queryset.filter(status='fm_reviewed')
        else:
            queryset = self.queryset.none()
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)