from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from decimal import Decimal
from apps.users.models import User
from apps.event_requests.models import EventRequest
from .models import BudgetApproval


class BudgetApprovalModelTestCase(TestCase):
    """预算审批模型测试"""
    
    def setUp(self):
        self.sm_user = User.objects.create_user(
            username='sm_test',
            password='testpass123',
            role='sm',
            department='Service'
        )
        self.pm_user = User.objects.create_user(
            username='pm_test',
            password='testpass123',
            role='pm',
            department='Production'
        )
        self.fm_user = User.objects.create_user(
            username='fm_test',
            password='testpass123',
            role='fm',
            department='Finance'
        )
        
        now = timezone.now()
        self.event_request = EventRequest.objects.create(
            title='Test Event',
            record_number='ER-2024-001',
            client_name='Test Client',
            event_type='Conference',
            expected_number=100,
            expected_budget=50000.00,
            from_date=now.date() + timedelta(days=30),
            to_date=now.date() + timedelta(days=32),
            has_decorations=True,
            has_meals=True,
            has_parties=False,
            has_drinks=True,
            has_filming=True,
            created_by=self.sm_user,
            status='submitted'
        )
    
    def test_create_budget_approval(self):
        """测试创建预算审批"""
        budget = BudgetApproval.objects.create(
            title='Additional Budget for Decorations',
            description='Need extra budget for premium decorations',
            requester=self.sm_user,
            related_event=self.event_request,
            requested_amount=Decimal('10000.00'),
            status='submitted'
        )
        self.assertEqual(budget.title, 'Additional Budget for Decorations')
        self.assertEqual(budget.requester, self.sm_user)
        self.assertEqual(budget.status, 'submitted')
        self.assertEqual(budget.requested_amount, Decimal('10000.00'))
    
    def test_budget_approval_str_representation(self):
        """测试预算审批字符串表示"""
        budget = BudgetApproval.objects.create(
            title='Extra Catering Budget',
            description='More guests confirmed',
            requester=self.pm_user,
            requested_amount=Decimal('5000.00')
        )
        self.assertIn('Extra Catering Budget', str(budget))
        self.assertIn('5000.00', str(budget))
    
    def test_budget_approval_default_status(self):
        """测试预算审批默认状态"""
        budget = BudgetApproval.objects.create(
            title='Test Budget',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('1000.00')
        )
        self.assertEqual(budget.status, 'submitted')
    
    def test_budget_approval_ordering(self):
        """测试预算审批排序"""
        budget1 = BudgetApproval.objects.create(
            title='Budget 1',
            description='First',
            requester=self.sm_user,
            requested_amount=Decimal('1000.00')
        )
        budget2 = BudgetApproval.objects.create(
            title='Budget 2',
            description='Second',
            requester=self.pm_user,
            requested_amount=Decimal('2000.00')
        )
        budgets = BudgetApproval.objects.all()
        self.assertEqual(budgets[0], budget2)  # 最新的在前
        self.assertEqual(budgets[1], budget1)


class BudgetApprovalAPITestCase(APITestCase):
    """预算审批 API 测试"""
    
    def setUp(self):
        # 创建不同角色的用户
        self.sm_user = User.objects.create_user(
            username='sm_user',
            password='testpass123',
            role='sm',
            department='Service'
        )
        self.pm_user = User.objects.create_user(
            username='pm_user',
            password='testpass123',
            role='pm',
            department='Production'
        )
        self.fm_user = User.objects.create_user(
            username='fm_user',
            password='testpass123',
            role='fm',
            department='Finance'
        )
        self.cs_user = User.objects.create_user(
            username='cs_user',
            password='testpass123',
            role='cs',
            department='Customer Service'
        )
        
        # 创建事件请求
        now = timezone.now()
        self.event_request = EventRequest.objects.create(
            title='Tech Conference 2024',
            record_number='ER-2024-001',
            client_name='ABC Corp',
            event_type='Conference',
            expected_number=150,
            expected_budget=75000.00,
            from_date=now.date() + timedelta(days=30),
            to_date=now.date() + timedelta(days=32),
            has_decorations=True,
            has_meals=True,
            has_parties=False,
            has_drinks=True,
            has_filming=True,
            created_by=self.sm_user,
            status='submitted'
        )
        
        self.client = APIClient()
    
    # ========== SM/PM 创建预算申请测试 ==========
    
    def test_sm_create_budget_request_success(self):
        """测试 SM 成功创建预算申请"""
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Additional Decoration Budget',
            'description': 'Client requested premium decorations',
            'related_event': self.event_request.id,
            'requested_amount': '15000.00'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Additional Decoration Budget')
        self.assertEqual(response.data['status'], 'submitted')
        self.assertEqual(response.data['requester'], self.sm_user.id)
        self.assertEqual(response.data['requester_department'], 'Service')
        self.assertEqual(Decimal(response.data['requested_amount']), Decimal('15000.00'))
    
    def test_pm_create_budget_request_success(self):
        """测试 PM 成功创建预算申请"""
        self.client.force_authenticate(user=self.pm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Equipment Upgrade Budget',
            'description': 'Need new AV equipment for better quality',
            'related_event': self.event_request.id,
            'requested_amount': '25000.00'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['requester'], self.pm_user.id)
        self.assertEqual(response.data['requester_department'], 'Production')
        self.assertEqual(response.data['status'], 'submitted')
    
    def test_fm_cannot_create_budget_request(self):
        """测试 FM 不能创建预算申请"""
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Test Budget',
            'description': 'Should not be allowed',
            'requested_amount': '10000.00'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('只有 Service Manager 或 Product Manager', str(response.data))
    
    def test_cs_cannot_create_budget_request(self):
        """测试 CS 不能创建预算申请"""
        self.client.force_authenticate(user=self.cs_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Test Budget',
            'description': 'Should not be allowed',
            'requested_amount': '10000.00'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_budget_request_without_event(self):
        """测试创建不关联事件的预算申请"""
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'General Budget Request',
            'description': 'Department operational budget',
            'requested_amount': '30000.00'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['related_event'])
    
    # ========== SM/PM 查看预算申请测试 ==========
    
    def test_sm_list_own_budget_requests(self):
        """测试 SM 只能查看自己的预算申请"""
        # SM 创建申请
        budget1 = BudgetApproval.objects.create(
            title='SM Budget 1',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00')
        )
        budget2 = BudgetApproval.objects.create(
            title='SM Budget 2',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('20000.00')
        )
        # PM 创建申请
        budget3 = BudgetApproval.objects.create(
            title='PM Budget',
            description='Test',
            requester=self.pm_user,
            requested_amount=Decimal('15000.00')
        )
        
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        titles = [item['title'] for item in response.data['results']]
        self.assertIn('SM Budget 1', titles)
        self.assertIn('SM Budget 2', titles)
        self.assertNotIn('PM Budget', titles)
    
    def test_pm_list_own_budget_requests(self):
        """测试 PM 只能查看自己的预算申请"""
        BudgetApproval.objects.create(
            title='SM Budget',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00')
        )
        budget_pm = BudgetApproval.objects.create(
            title='PM Budget',
            description='Test',
            requester=self.pm_user,
            requested_amount=Decimal('15000.00')
        )
        
        self.client.force_authenticate(user=self.pm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'PM Budget')
    
    def test_sm_retrieve_own_budget_request(self):
        """测试 SM 查看自己的单个预算申请"""
        budget = BudgetApproval.objects.create(
            title='SM Budget Detail',
            description='Detailed budget request',
            requester=self.sm_user,
            related_event=self.event_request,
            requested_amount=Decimal('12000.00')
        )
        
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-detail', kwargs={'pk': budget.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'SM Budget Detail')
        self.assertEqual(response.data['requester_name'], 'sm_user')
        self.assertEqual(response.data['related_event_title'], 'ABC Corp')
    
    # ========== FM 查看和处理预算申请测试 ==========
    
    def test_fm_list_all_budget_requests(self):
        """测试 FM 可以查看所有预算申请"""
        BudgetApproval.objects.create(
            title='SM Budget',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00')
        )
        BudgetApproval.objects.create(
            title='PM Budget',
            description='Test',
            requester=self.pm_user,
            requested_amount=Decimal('15000.00')
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_fm_approve_budget_request(self):
        """测试 FM 批准预算申请"""
        budget = BudgetApproval.objects.create(
            title='Budget to Approve',
            description='Pending approval',
            requester=self.sm_user,
            requested_amount=Decimal('20000.00'),
            status='submitted'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'fm_decision': 'Budget approved. Funds allocated.',
            'status': 'approved'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        self.assertEqual(response.data['fm_decision'], 'Budget approved. Funds allocated.')
        self.assertEqual(response.data['fm_handler'], self.fm_user.id)
        
        # 验证数据库中的更新
        budget.refresh_from_db()
        self.assertEqual(budget.status, 'approved')
        self.assertEqual(budget.fm_handler, self.fm_user)
    
    def test_fm_reject_budget_request(self):
        """测试 FM 拒绝预算申请"""
        budget = BudgetApproval.objects.create(
            title='Budget to Reject',
            description='Insufficient justification',
            requester=self.pm_user,
            requested_amount=Decimal('50000.00'),
            status='submitted'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'fm_decision': 'Rejected due to insufficient justification and budget constraints.',
            'status': 'rejected'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'rejected')
        self.assertEqual(response.data['fm_handler'], self.fm_user.id)
    
    def test_fm_cannot_decide_already_approved(self):
        """测试 FM 不能处理已批准的申请"""
        budget = BudgetApproval.objects.create(
            title='Already Approved',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00'),
            status='approved',
            fm_handler=self.fm_user,
            fm_decision='Already approved'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'fm_decision': 'Try to change decision',
            'status': 'rejected'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('无法处理状态为', str(response.data))
    
    def test_fm_cannot_decide_already_rejected(self):
        """测试 FM 不能处理已拒绝的申请"""
        budget = BudgetApproval.objects.create(
            title='Already Rejected',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00'),
            status='rejected',
            fm_handler=self.fm_user,
            fm_decision='Already rejected'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'fm_decision': 'Try to approve now',
            'status': 'approved'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_sm_cannot_decide_budget_request(self):
        """测试 SM 不能处理预算申请"""
        budget = BudgetApproval.objects.create(
            title='SM Created Budget',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00'),
            status='submitted'
        )
        
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'fm_decision': 'Try to approve own request',
            'status': 'approved'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('只有 Financial Manager', str(response.data))
    
    def test_pm_cannot_decide_budget_request(self):
        """测试 PM 不能处理预算申请"""
        budget = BudgetApproval.objects.create(
            title='PM Created Budget',
            description='Test',
            requester=self.pm_user,
            requested_amount=Decimal('10000.00'),
            status='submitted'
        )
        
        self.client.force_authenticate(user=self.pm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'fm_decision': 'Try to approve own request',
            'status': 'approved'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    # ========== 状态过滤测试 ==========
    
    def test_filter_by_status_submitted(self):
        """测试按状态过滤 - submitted"""
        BudgetApproval.objects.create(
            title='Submitted 1',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00'),
            status='submitted'
        )
        BudgetApproval.objects.create(
            title='Approved',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('15000.00'),
            status='approved'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url, {'status': 'submitted'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'submitted')
    
    def test_filter_by_status_approved(self):
        """测试按状态过滤 - approved"""
        BudgetApproval.objects.create(
            title='Submitted',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00'),
            status='submitted'
        )
        BudgetApproval.objects.create(
            title='Approved 1',
            description='Test',
            requester=self.pm_user,
            requested_amount=Decimal('15000.00'),
            status='approved'
        )
        BudgetApproval.objects.create(
            title='Approved 2',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('20000.00'),
            status='approved'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url, {'status': 'approved'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_by_related_event(self):
        """测试按关联事件过滤"""
        BudgetApproval.objects.create(
            title='Budget for Event',
            description='Test',
            requester=self.sm_user,
            related_event=self.event_request,
            requested_amount=Decimal('10000.00')
        )
        BudgetApproval.objects.create(
            title='General Budget',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('15000.00')
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url, {'related_event': self.event_request.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Budget for Event')
    
    # ========== 权限测试 ==========
    
    def test_cs_cannot_access_budget_list(self):
        """测试 CS 不能访问预算列表"""
        BudgetApproval.objects.create(
            title='Test Budget',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00')
        )
        
        self.client.force_authenticate(user=self.cs_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)  # CS 看不到任何预算
    
    def test_unauthenticated_cannot_access(self):
        """测试未认证用户不能访问"""
        url = reverse('budget-approval-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # ========== 完整工作流测试 ==========
    
    def test_complete_budget_approval_workflow(self):
        """测试完整的预算审批工作流"""
        # 1. SM 创建预算申请
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Urgent Equipment Budget',
            'description': 'Need new sound system for upcoming event',
            'related_event': self.event_request.id,
            'requested_amount': '35000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        budget_id = response.data['id']
        
        # 2. SM 查看自己的申请
        url = reverse('budget-approval-detail', kwargs={'pk': budget_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'submitted')
        
        # 3. FM 查看所有申请
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        # 4. FM 批准申请
        url = reverse('budget-approval-decide', kwargs={'pk': budget_id})
        data = {
            'fm_decision': 'Approved. Critical for event success. Funds transferred.',
            'status': 'approved'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        self.assertEqual(response.data['fm_handler'], self.fm_user.id)
        
        # 5. SM 查看已批准的申请
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-detail', kwargs={'pk': budget_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        self.assertEqual(response.data['fm_handler_name'], 'fm_user')
    
    def test_complete_budget_rejection_workflow(self):
        """测试完整的预算拒绝工作流"""
        # 1. PM 创建预算申请
        self.client.force_authenticate(user=self.pm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Luxury Upgrade Budget',
            'description': 'Upgrade to premium tier services',
            'requested_amount': '100000.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        budget_id = response.data['id']
        
        # 2. FM 拒绝申请
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget_id})
        data = {
            'fm_decision': 'Rejected. Budget exceeds allocated amount. Need more detailed justification.',
            'status': 'rejected'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'rejected')
        
        # 3. PM 查看被拒绝的申请
        self.client.force_authenticate(user=self.pm_user)
        url = reverse('budget-approval-detail', kwargs={'pk': budget_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'rejected')
        self.assertIn('Budget exceeds', response.data['fm_decision'])
    
    # ========== 边界条件测试 ==========
    
    def test_create_budget_with_zero_amount(self):
        """测试创建金额为零的预算申请"""
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Zero Budget',
            'description': 'Testing edge case',
            'requested_amount': '0.00'
        }
        response = self.client.post(url, data, format='json')
        # 应该能创建，但可能需要业务逻辑验证
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_budget_with_large_amount(self):
        """测试创建大金额的预算申请"""
        self.client.force_authenticate(user=self.sm_user)
        url = reverse('budget-approval-list')
        data = {
            'title': 'Large Budget Request',
            'description': 'Major project funding',
            'requested_amount': '99999999.99'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_fm_decision_without_comment(self):
        """测试 FM 决策时不提供评论"""
        budget = BudgetApproval.objects.create(
            title='Budget Request',
            description='Test',
            requester=self.sm_user,
            requested_amount=Decimal('10000.00'),
            status='submitted'
        )
        
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('budget-approval-decide', kwargs={'pk': budget.pk})
        data = {
            'status': 'approved'
            # 缺少 fm_decision
        }
        response = self.client.post(url, data, format='json')
        # 应该失败，因为缺少必需字段
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
