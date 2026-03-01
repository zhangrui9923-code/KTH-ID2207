from rest_framework import serializers
from .models import Recruitment

class RecruitmentSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    hr_handler_username = serializers.CharField(source='hr_handler.username', read_only=True)

    class Meta:
        model = Recruitment
        fields = '__all__'
        # 关键：把 requester / hr_handler 也设为只读，避免创建时被要求提供
        read_only_fields = (
            'requester', 'hr_handler',
            'started_at', 'completed_at',
            'created_at', 'updated_at'
        )
