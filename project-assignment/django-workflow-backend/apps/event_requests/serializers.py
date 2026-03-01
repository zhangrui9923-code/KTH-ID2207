from rest_framework import serializers
from .models import EventRequest


class EventRequestCreateSerializer(serializers.ModelSerializer):
    """Customer Service 创建事件请求的序列化器（简表）"""
    
    class Meta:
        model = EventRequest
        fields = [
            'record_number',
            'client_name',
            'event_type',
            'from_date',
            'to_date',
            'expected_number',
            'has_decorations',
            'has_meals',
            'has_parties',
            'has_drinks',
            'has_filming',
            'expected_budget',
        ]
    
    def create(self, validated_data):
        # 自动设置创建者和状态
        validated_data['created_by'] = self.context['request'].user
        validated_data['status'] = 'submitted'
        validated_data['title'] = f"{validated_data['client_name']} - {validated_data['event_type']}"
        validated_data['description'] = f"Event request for {validated_data['client_name']}"
        return super().create(validated_data)


class EventRequestSCSReviewSerializer(serializers.ModelSerializer):
    """Senior Customer Service 审核序列化器"""
    
    class Meta:
        model = EventRequest
        fields = ['scs_comment']
    
    def validate(self, data):
        if self.instance.status != 'submitted':
            raise serializers.ValidationError("只能审核状态为 'submitted' 的请求")
        return data


class EventRequestFMReviewSerializer(serializers.ModelSerializer):
    """Financial Manager 审核序列化器"""
    
    class Meta:
        model = EventRequest
        fields = ['fm_feedback']
    
    def validate(self, data):
        if self.instance.status != 'scs_reviewed':
            raise serializers.ValidationError("只能审核状态为 'scs_reviewed' 的请求")
        return data


class EventRequestAdminReviewSerializer(serializers.ModelSerializer):
    """Admin Manager 审核序列化器"""
    
    decision = serializers.ChoiceField(choices=['approved', 'rejected'])
    
    class Meta:
        model = EventRequest
        fields = ['admin_decision', 'decision']
    
    def validate(self, data):
        if self.instance.status != 'fm_reviewed':
            raise serializers.ValidationError("只能审核状态为 'fm_reviewed' 的请求")
        return data


class EventRequestDetailsSerializer(serializers.ModelSerializer):
    """Senior Customer Service 添加详细信息的序列化器"""
    
    class Meta:
        model = EventRequest
        fields = [
            'description_of_decorations',
            'description_of_meals',
            'description_of_music',
            'description_of_poster',
            'description_of_filming',
            'description_of_drinks',
            'other_needs',
        ]
    
    def validate(self, data):
        if self.instance.status != 'approved':
            raise serializers.ValidationError("只能在状态为 'approved' 时添加详细信息")
        return data


class EventRequestSerializer(serializers.ModelSerializer):
    """完整的事件请求序列化器（用于查看）"""
    
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    scs_handler_name = serializers.CharField(source='scs_handler.username', read_only=True)
    fm_handler_name = serializers.CharField(source='fm_handler.username', read_only=True)
    admin_handler_name = serializers.CharField(source='admin_handler.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EventRequest
        fields = '__all__'
        read_only_fields = [
            'created_by',
            'current_handler',
            'status',
            'scs_handler',
            'scs_handled_at',
            'fm_handler',
            'fm_handled_at',
            'admin_handler',
            'admin_handled_at',
            'created_at',
            'updated_at',
        ]