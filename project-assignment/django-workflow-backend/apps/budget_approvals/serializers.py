from rest_framework import serializers
from .models import BudgetApproval
from apps.users.models import User


class BudgetApprovalSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.username', read_only=True)
    requester_department = serializers.CharField(source='requester.department', read_only=True)
    fm_handler_name = serializers.CharField(source='fm_handler.username', read_only=True)
    related_event_title = serializers.CharField(source='related_event.client_name', read_only=True)
    
    class Meta:
        model = BudgetApproval
        fields = [
            'id',
            'title',
            'description',
            'requester',
            'requester_name',
            'requester_department',
            'related_event',
            'related_event_title',
            'requested_amount',
            'status',
            'fm_handler',
            'fm_handler_name',
            'fm_decision',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['requester', 'fm_handler', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # 自动设置申请人为当前用户
        request = self.context.get('request')
        validated_data['requester'] = request.user
        validated_data['status'] = 'submitted'
        return super().create(validated_data)
    
    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        
        # 创建时检查用户角色
        if self.instance is None:  # 创建操作
            if user.role not in ['sm', 'pm']:
                raise serializers.ValidationError(
                    "只有 Service Manager 或 Product Manager 可以创建预算申请"
                )
        
        return data


class BudgetApprovalDecisionSerializer(serializers.ModelSerializer):
    """FM 处理预算申请的序列化器"""
    
    class Meta:
        model = BudgetApproval
        fields = ['fm_decision', 'status']
    
    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError(
                "状态只能设置为 'approved' 或 'rejected'"
            )
        return value
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.fm_handler = request.user
        return super().update(instance, validated_data)