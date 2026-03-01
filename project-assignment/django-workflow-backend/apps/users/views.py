from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .serializers import UserSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集，提供完整的 CRUD 功能
    
    list: 获取用户列表
    create: 创建新用户
    retrieve: 获取单个用户详情
    update: 完整更新用户
    partial_update: 部分更新用户
    destroy: 删除用户
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    
    def get_serializer_class(self):
        """列表使用简化序列化器"""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """按角色获取用户"""
        role = request.query_params.get('role')
        if role:
            users = self.queryset.filter(role=role)
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data)
        return Response({'error': 'role parameter is required'}, status=400)


    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录
        
        请求体:
        {
            "username": "Mike",
            "password": "123456"
        }
        
        返回:
        {
            "token": "abc123...",  # 用这个 token 进行后续请求
            "user": {...}
        }
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 认证用户
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # 创建或获取 token
                token, created = Token.objects.get_or_create(user=user)
                
                # 同时也创建 session（可选，为了兼容性）
                login(request, user)
                
                # 返回用户信息和 token
                serializer = UserSerializer(user)
                return Response({
                    'message': '登录成功',
                    'token': token.key,  # 重要：返回 token
                    'user': serializer.data
                })
            else:
                return Response(
                    {'error': '账户已被禁用'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出 - 删除 token"""
        if request.user.is_authenticated:
            # 删除用户的 token
            Token.objects.filter(user=request.user).delete()
            # 同时也清除 session
            logout(request)
            return Response({'message': '登出成功'})
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前登录用户信息"""
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response(
            {'error': '未登录'},
            status=status.HTTP_401_UNAUTHORIZED
        )