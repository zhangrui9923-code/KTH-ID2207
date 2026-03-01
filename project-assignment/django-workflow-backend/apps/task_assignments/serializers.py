from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TaskAssignment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TaskAssignmentListSerializer(serializers.ModelSerializer):
    """任务列表序列化器（简化版）"""
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'title', 'status', 'status_display',
            'manager', 'manager_name',
            'employee', 'employee_name',
            'start_date', 'end_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskAssignmentDetailSerializer(serializers.ModelSerializer):
    """任务详情序列化器（完整版）"""
    manager = UserSerializer(read_only=True)
    employee = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'title', 'description',
            'manager', 'employee',
            'start_date', 'end_date',
            'status', 'status_display',
            'employee_plan', 'estimated_budget',
            'employee_submitted_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_submitted_at']


class TaskAssignmentCreateSerializer(serializers.ModelSerializer):
    """创建任务序列化器"""

    class Meta:
        model = TaskAssignment
        fields = [
            'title', 'description',
            'employee',
            'start_date', 'end_date'
        ]

    def validate(self, data):
        """验证日期"""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError({
                'end_date': '结束日期必须晚于开始日期'
            })
        return data

    def create(self, validated_data):
        """创建任务，自动设置manager和初始状态"""
        validated_data['manager'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class TaskAssignmentUpdateSerializer(serializers.ModelSerializer):
    """更新任务序列化器（Manager使用）"""

    class Meta:
        model = TaskAssignment
        fields = [
            'title', 'description',
            'employee',
            'start_date', 'end_date',
            'status'
        ]

    def validate_status(self, value):
        """验证状态转换"""
        instance = self.instance
        if instance:
            # 只有manager可以将状态改为sent_to_employee或completed
            if value in ['sent_to_employee', 'completed']:
                return value
            # 其他状态转换不允许manager直接修改
            if value != instance.status:
                raise serializers.ValidationError('不允许的状态转换')
        return value


class EmployeePlanSubmitSerializer(serializers.ModelSerializer):
    """员工提交计划序列化器"""

    class Meta:
        model = TaskAssignment
        fields = ['employee_plan', 'estimated_budget']

    def validate(self, data):
        """验证员工提交"""
        instance = self.instance
        if instance and instance.status not in ['sent_to_employee', 'plan_submitted']:
            raise serializers.ValidationError('当前状态不允许提交计划')
        return data

    def update(self, instance, validated_data):
        """更新并设置提交时间和状态"""
        from django.utils import timezone

        validated_data['employee_submitted_at'] = timezone.now()
        validated_data['status'] = 'plan_submitted'
        return super().update(instance, validated_data)