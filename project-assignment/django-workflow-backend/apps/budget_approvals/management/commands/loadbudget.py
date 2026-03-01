from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from apps.users.models import User
from apps.budget_approvals.models import BudgetApproval
from apps.event_requests.models import EventRequest


class Command(BaseCommand):
    help = '创建预算审批的模拟数据'

    def handle(self, *args, **kwargs):
        # 获取现有用户
        try:
            pm_user = User.objects.get(username='Jack')
            sm_user = User.objects.get(username='Natalie')
            fm_user = User.objects.get(username='Alice')
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('错误: 请先运行 loaduser 命令创建用户')
            )
            return

        # 获取一些事件请求用于关联
        event_requests = list(EventRequest.objects.all()[:4])
        
        now = timezone.now()

        budget_data = [
            # 1. SM 提交的 - Submitted 状态
            {
                'title': 'Additional Decoration Budget for Tech Conference',
                'description': 'Client ABC Corp requested premium stage decorations including LED walls and custom lighting setup. Original budget does not cover these premium additions.',
                'requester': sm_user,
                'related_event': event_requests[0] if len(event_requests) > 0 else None,
                'requested_amount': Decimal('25000.00'),
                'status': 'submitted',
                'created_at': now - timedelta(days=2),
                'updated_at': now - timedelta(days=2),
            },
            # 2. PM 提交的 - Submitted 状态
            {
                'title': 'AV Equipment Upgrade for Product Launch',
                'description': 'Need to rent professional 4K camera equipment and live streaming setup for XYZ Tech product launch. High-profile event requires broadcast-quality production.',
                'requester': pm_user,
                'related_event': event_requests[1] if len(event_requests) > 1 else None,
                'requested_amount': Decimal('18500.00'),
                'status': 'submitted',
                'created_at': now - timedelta(days=1, hours=12),
                'updated_at': now - timedelta(days=1, hours=12),
            },
            # 3. SM 提交的 - Approved 状态
            {
                'title': 'Emergency Catering Budget Increase',
                'description': 'Guest count increased from 250 to 350 for Charity Gala. Need additional catering budget to accommodate the extra 100 guests with same premium menu.',
                'requester': sm_user,
                'related_event': event_requests[2] if len(event_requests) > 2 else None,
                'requested_amount': Decimal('15000.00'),
                'status': 'approved',
                'fm_handler': fm_user,
                'fm_decision': 'Budget approved. The increased guest count justifies the additional catering costs. ROI remains positive with more attendees. Funds allocated from contingency budget.',
                'created_at': now - timedelta(days=5),
                'updated_at': now - timedelta(days=3),
            },
            # 4. PM 提交的 - Approved 状态
            {
                'title': 'Premium Sound System Rental',
                'description': 'Client requested upgrade to premium sound system for Summer Festival. Original quote was for standard system. Premium system includes wireless mics, monitors, and professional mixing console.',
                'requester': pm_user,
                'related_event': event_requests[3] if len(event_requests) > 3 else None,
                'requested_amount': Decimal('32000.00'),
                'status': 'approved',
                'fm_handler': fm_user,
                'fm_decision': 'Approved. Premium audio is essential for outdoor festival. Client agreed to 60% cost share. Expected profit margin maintained. Payment received in advance.',
                'created_at': now - timedelta(days=7),
                'updated_at': now - timedelta(days=4),
            },
            # 5. SM 提交的 - Rejected 状态
            {
                'title': 'Luxury Transportation Budget',
                'description': 'Request for luxury car service and helicopter transfer for VIP guests. Would enhance event prestige and client satisfaction.',
                'requester': sm_user,
                'related_event': None,
                'requested_amount': Decimal('45000.00'),
                'status': 'rejected',
                'fm_handler': fm_user,
                'fm_decision': 'Rejected. Budget too high for transportation alone. No commitment from client to cover additional costs. Standard limo service is sufficient. Recommend discussing upgrade options with client first.',
                'created_at': now - timedelta(days=8),
                'updated_at': now - timedelta(days=6),
            },
            # 6. PM 提交的 - Rejected 状态
            {
                'title': 'Custom Stage Design and Construction',
                'description': 'Request for custom-built stage with hydraulic platforms and special effects integration. Would create unique experience but requires significant investment.',
                'requester': pm_user,
                'related_event': None,
                'requested_amount': Decimal('75000.00'),
                'status': 'rejected',
                'fm_handler': fm_user,
                'fm_decision': 'Rejected. Cost-benefit analysis shows poor ROI. Custom stage cannot be reused for other events. Timeline too short for safe construction. Recommend using modular staging system instead.',
                'created_at': now - timedelta(days=10),
                'updated_at': now - timedelta(days=7),
            },
        ]

        created_count = 0
        for idx, budget_info in enumerate(budget_data, 1):
            title = budget_info['title']
            
            # 检查是否已存在（通过标题检查）
            if BudgetApproval.objects.filter(title=title).exists():
                self.stdout.write(
                    self.style.WARNING(f'预算审批 "{title}" 已存在，跳过')
                )
                continue

            # 创建预算审批
            budget = BudgetApproval.objects.create(**budget_info)
            
            created_count += 1
            requester_name = budget_info['requester'].username
            status_display = budget_info['status'].upper()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ 成功创建预算审批 #{idx}: {title[:50]}... '
                    f'(申请人: {requester_name}, 状态: {status_display}, '
                    f'金额: ${budget_info["requested_amount"]})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n总计创建 {created_count} 条预算审批记录')
        )