from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from .models import EventRequest


class EventRequestWorkflowTestCase(APITestCase):
    """事件请求工作流测试"""
    
    def setUp(self):
        now = timezone.now()
        # 创建不同角色的用户
        self.cs_user = User.objects.create_user(
            username='cs_user',
            password='testpass123',
            role='cs'
        )
        self.scs_user = User.objects.create_user(
            username='scs_user',
            password='testpass123',
            role='scs'
        )
        self.fm_user = User.objects.create_user(
            username='fm_user',
            password='testpass123',
            role='fm'
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='testpass123',
            role='admin'
        )

        self.submitted_event = EventRequest.objects.create(
                title = 'Tech Conference 2024 - ABC Corp',
                description = 'Event request for ABC Corp',
                record_number = 'ER-2024-001',
                client_name = 'ABC Corp',
                event_type = 'Conference',
                expected_number = 150,
                expected_budget = 75000.00,
                from_date = now.date() + timedelta(days=30),
                to_date = now.date() + timedelta(days=32),
                has_decorations = True,
                has_meals = True,
                has_parties = False,
                has_drinks = True,
                has_filming = True,
                created_by = self.cs_user,
                status = 'submitted',
                created_at = now - timedelta(hours=2),
                updated_at = now - timedelta(hours=2)
        )
        self.scs_handled_event = EventRequest.objects.create(
                title = 'Product Launch - XYZ Tech',
                description = 'Event request for XYZ Tech',
                record_number = 'ER-2024-003',
                client_name = 'XYZ Tech',
                event_type = 'Product Launch',
                expected_number = 300,
                expected_budget = 150000.00,
                from_date = now.date() + timedelta(days=45),
                to_date = now.date() + timedelta(days=46),
                has_decorations = True,
                has_meals = True,
                has_parties = True,
                has_drinks = True,
                has_filming = True,
                created_by = self.cs_user,
                status = 'scs_reviewed',
                created_at = now - timedelta(days=2),
                updated_at = now - timedelta(hours=6),
                scs_handler = self.scs_user,
                scs_comment = 'Event details look comprehensive. Client is a valued customer with good payment history. Ready for financial review.',
                scs_handled_at = now - timedelta(hours=6),
        )
        self.fm_handled_event = EventRequest.objects.create(
            title = 'Charity Gala - Hope Foundation',
            description = 'Event request for Hope Foundation',
            record_number = 'ER-2024-005',
            client_name = 'Hope Foundation',
            event_type = 'Charity Gala',
            expected_number = 250,
            expected_budget = 180000.00,
            from_date = now.date() + timedelta(days=50),
            to_date = now.date() + timedelta(days=50),
            has_decorations = True,
            has_meals = True,
            has_parties = True,
            has_drinks = True,
            has_filming = True,
            created_by = self.cs_user,
            status = 'fm_reviewed',
            created_at = now - timedelta(days=3),
            updated_at = now - timedelta(hours=4),
            scs_handler = self.scs_user,
            scs_comment = 'High-profile charity event. Excellent opportunity for company PR. Recommend approval.',
            scs_handled_at = now - timedelta(days=2, hours=18),
            fm_handler = self.fm_user,
            fm_feedback = 'Budget reviewed and approved. Expected ROI is positive. Payment terms: 50% deposit, 50% on completion.',
            fm_handled_at = now - timedelta(hours=4)
        )
        self.approved_event = EventRequest.objects.create(
            title = 'Summer Festival - City Council',
            description = 'Event request for City Council',
            record_number = 'ER-2024-007',
            client_name = 'City Council',
            event_type = 'Festival',
            expected_number = 500,
            expected_budget = 250000.00,
            from_date = now.date() + timedelta(days=90),
            to_date = now.date() + timedelta(days=92),
            has_decorations = True,
            has_meals = True,
            has_parties = True,
            has_drinks = True,
            has_filming = True,
            created_by = self.cs_user,
            status = 'approved',
            created_at = now - timedelta(days=5),
            updated_at = now - timedelta(hours=1),
            scs_handler = self.scs_user,
            scs_comment = 'Major city event with high visibility. Strategic importance for company portfolio.',
            scs_handled_at = now - timedelta(days=4, hours=12),
            fm_handler = self.fm_user,
            fm_feedback = 'Large budget approved with staged payments. Government client - secure payment. Profit margin is healthy.',
            fm_handled_at = now - timedelta(days=3, hours=8),
            admin_handler = self.admin_user,
            admin_decision = 'APPROVED. High-profile event aligns with company growth strategy. Allocate senior team members.',
            admin_handled_at = now - timedelta(hours=1)
        )
        self.rejected_event = EventRequest.objects.create(
            title = 'Private Party - Johnson Estate',
            description = 'Event request for Johnson Estate',
            record_number = 'ER-2024-009',
            client_name = 'Johnson Estate',
            event_type = 'Private Party',
            expected_number = 50,
            expected_budget = 85000.00,
            from_date = now.date() + timedelta(days=15),
            to_date = now.date() + timedelta(days=15),
            has_decorations = True,
            has_meals = True,
            has_parties = True,
            has_drinks = True,
            has_filming = False,
            created_by = self.cs_user,
            status = 'rejected',
            created_at = now - timedelta(days=6),
            updated_at = now - timedelta(days=4),
            scs_handler = self.scs_user,
            scs_comment = 'Small event with very high budget per person. Client is new with no references. Timeline is very tight.',
            scs_handled_at = now - timedelta(days=5, hours=16),
            fm_handler = self.fm_user,
            fm_feedback = 'Budget seems inflated. No payment history. High financial risk. Recommend rejection unless 100% prepayment.',
            fm_handled_at = now - timedelta(days=5, hours=2),
            admin_handler = self.admin_user,
            admin_decision = 'REJECTED. Timeline too short for preparation. Financial risk too high for unknown client.',
            admin_handled_at = now - timedelta(days=4),
        )
        self.open_event = EventRequest.objects.create(
            title = 'Awards Ceremony - MediaGroup',
            description = 'Event request for MediaGroup',
            record_number = 'ER-2024-011',
            client_name = 'MediaGroup',
            event_type = 'Awards Ceremony',
            expected_number = 300,
            expected_budget = 200000.00,
            from_date = now.date() + timedelta(days=70),
            to_date = now.date() + timedelta(days=70),
            has_decorations = True,
            has_meals = True,
            has_parties = True,
            has_drinks = True,
            has_filming = True,
            created_by = self.cs_user,
            status = 'open',
            created_at = now - timedelta(days=10),
            updated_at = now - timedelta(days=2),
            scs_handler = self.scs_user,
            scs_comment = 'Prestigious awards ceremony. Media client with excellent reputation. High visibility event.',
            scs_handled_at = now - timedelta(days=9, hours=10),
            fm_handler = self.fm_user,
            fm_feedback = 'Budget approved. Client has strong financials. Expected profit margin 25%. Payment terms: 40% deposit, 40% mid-project, 20% completion.',
            fm_handled_at = now - timedelta(days=8, hours=14),
            admin_handler = self.admin_user,
            admin_decision = 'APPROVED. Excellent showcase opportunity. Assign top-tier team. Ensure media coverage for company PR.',
            admin_handled_at = now - timedelta(days=7, hours=20),
            description_of_decorations = 'Red carpet entrance with gold and black theme. Crystal chandeliers, elegant draping, floral centerpieces.',
            description_of_meals = 'Five-course gourmet dinner: Smoked salmon canapés, French onion soup, filet mignon or sea bass, chocolate fondant.',
            description_of_music = 'Live jazz quartet during cocktail hour. DJ for after-ceremony celebration. Professional sound system.',
            description_of_poster = 'Large format posters at entrance featuring award categories and nominees. Digital displays throughout venue.',
            description_of_filming = 'Three professional cameras for live streaming. Drone footage. Photo booth. Professional photographer for red carpet.',
            description_of_drinks = 'Premium open bar: champagne, wine selection, craft cocktails, mocktails. Signature cocktail for the event.',
            other_needs = 'VIP green room. Security. Valet parking. Event coordinator on-site. Award trophies and certificates.',
        )

        self.close_event = EventRequest.objects.create(
            title= 'New Year Gala - Luxury Hotels Group',
            description= 'Event request for Luxury Hotels Group',
            record_number= 'ER-2024-015',
            client_name= 'Luxury Hotels Group',
            event_type= 'Gala',
            expected_number= 400,
            expected_budget= 280000.00,
            from_date= now.date() - timedelta(days=30),
            to_date= now.date() - timedelta(days=30),
            has_decorations= True,
            has_meals= True,
            has_parties= True,
            has_drinks= True,
            has_filming= True,
            created_by= self.cs_user,
            status= 'closed',
            created_at= now - timedelta(days=90),
            updated_at= now - timedelta(days=25),
            scs_handler= self.scs_user,
            scs_comment= 'Premium New Year celebration. VIP client. Luxury tier service required.',
            scs_handled_at= now - timedelta(days=89),
            fm_handler= self.fm_user,
            fm_feedback= 'High-value event. Premium pricing approved. All payments completed successfully.',
            fm_handled_at= now - timedelta(days=88),
            admin_handler= self.admin_user,
            admin_decision= 'APPROVED. Showcase event. Deploy best resources. Opportunity for portfolio photos.',
            admin_handled_at= now - timedelta(days=87),
            description_of_decorations= 'Luxury New Year theme. Gold and silver decor. Balloon drop at midnight. Ice sculptures.',
            description_of_meals= 'Gourmet seven-course dinner. Michelin-star chef. Caviar station. Premium ingredients throughout.',
            description_of_music= 'Live orchestra. International DJ. Entertainment acts. Countdown coordination.',
            description_of_poster= 'Elegant event branding. Welcome displays. Sponsor recognition.',
            description_of_filming= 'Multi-camera setup. Highlight reel production. Social media content. Guest photography service.',
            description_of_drinks= 'Premium champagne. Top-shelf spirits. Specialty cocktails. Wine pairing with dinner.',
            other_needs= 'Valet service. Coat check. Security team. Event hostesses. Fireworks display. Photo booth. Party favors.',
        )

        self.client = APIClient()
    
    def test_full_workflow(self):
        """测试完整工作流"""
        
        # 1. CS 创建事件请求
        self.client.force_authenticate(user=self.cs_user)
        create_data = {
            'record_number': 'REQ001',
            'client_name': 'Test Client',
            'event_type': 'Conference',
            'from_date': '2024-03-01',
            'to_date': '2024-03-03',
            'expected_number': 100,
            'has_decorations': True,
            'has_meals': True,
            'has_parties': False,
            'has_drinks': True,
            'has_filming': True,
            'expected_budget': 50000.00,
        }
        url = reverse('event-request-list')
        response = self.client.post(url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'submitted')
        event_id = response.data['id']
        
        # 2. SCS 添加评论
        self.client.force_authenticate(user=self.scs_user)
        url = reverse('event-request-scs-review', kwargs={'pk': event_id})
        response = self.client.post(url, {
            'scs_comment': 'Looks good, approved for FM review'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'scs_reviewed')
        
        # 3. FM 添加反馈
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('event-request-fm-review', kwargs={'pk': event_id})
        response = self.client.post(url, {
            'fm_feedback': 'Budget approved'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'fm_reviewed')
        
        # 4. Admin 批准
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('event-request-admin-review', kwargs={'pk': event_id})
        response = self.client.post(url, {
            'admin_decision': 'Event approved',
            'decision': 'approved'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        
        # 5. SCS 添加详细信息
        self.client.force_authenticate(user=self.scs_user)
        url = reverse('event-request-add-details', kwargs={'pk': event_id})
        response = self.client.post(url, {
            'description_of_decorations': 'Modern theme',
            'description_of_meals': 'International buffet',
            'other_needs': 'PA system required'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'open')
    
    def test_cs_create_event_request_success(self):
        """测试 CS 成功创建事件请求"""
        self.client.force_authenticate(user=self.cs_user)
        now = timezone.now()
        create_data = {
            'title': 'Tech Conference 2024 - CCC Corp',
            'description': 'Event request for CCC Corp',
            'record_number': 'ER-2024-002',
            'client_name': 'CCC Corp',
            'event_type': 'Conference',
            'expected_number': 150,
            'expected_budget': 75000.00,
            'from_date': now.date() + timedelta(days=30),
            'to_date': now.date() + timedelta(days=32),
            'has_decorations': True,
            'has_meals': True,
            'has_parties': False,
            'has_drinks': True,
            'has_filming': True,
        }
        url = reverse('event-request-list')
        response = self.client.post(url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'submitted')
        self.assertEqual(response.data['created_by'], self.cs_user.id)
    
    def test_admin_create_event_request_forbidden(self):
        """测试 Admin 创建事件请求被禁止"""
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        create_data = {
            'title': 'Tech Conference 2024 - XYZ Inc',
            'description': 'Event request for XYZ Inc',
            'record_number': 'ER-2024-002',
            'client_name': 'XYZ Inc',
            'event_type': 'Conference',
            'expected_number': 200,
            'expected_budget': 100000.00,
            'from_date': now.date() + timedelta(days=45),
            'to_date': now.date() + timedelta(days=47),
            'has_decorations': True,
            'has_meals': True,
            'has_parties': True,
            'has_drinks': True,
            'has_filming': True,
        }
        url = reverse('event-request-list')
        response = self.client.post(url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_scs_review_success(self):
        """测试 SCS 成功审核事件请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.submitted_event content
        event_request_id = self.submitted_event.id
        
        # Now have SCS review it
        self.client.force_authenticate(user=self.scs_user)
        url = reverse('event-request-scs-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {'scs_comment': 'Looks good, approved for FM review'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'scs_reviewed')

    def test_scs_review_invalid_status(self):
        """测试 SCS 审核无效状态的请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.scs_reviewed_event content
        event_request_id = self.scs_handled_event.id
        
        # Try to have SCS review a request not in 'submitted' status
        self.client.force_authenticate(user=self.scs_user)
        url = reverse('event-request-scs-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {'scs_comment': 'Test Content'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fm_review_success(self):
        """测试 FM 成功审核事件请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.scs_reviewed_event content
        event_request_id = self.scs_handled_event.id
        
        # Now have FM review it
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('event-request-fm-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {'fm_feedback': 'Budget approved'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'fm_reviewed')
        self.assertEqual(response.data['fm_handler'], self.fm_user.id)

    def test_fm_review_invalid_status(self):
        """测试 FM 审核无效状态的请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.submitted_event content
        event_request_id = self.submitted_event.id
        
        # Try to have FM review a request not in 'scs_reviewed' status
        self.client.force_authenticate(user=self.fm_user)
        url = reverse('event-request-fm-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {'fm_feedback': 'Test Content'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_admin_review_success(self):
        """测试 Admin 成功审核事件请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.fm_reviewed_event content
        event_request_id = self.fm_handled_event.id
        
        # Now have Admin review it
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('event-request-admin-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {
            'admin_decision': 'Event approved',
            'decision': 'approved'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'approved')
        self.assertEqual(response.data['admin_handler'], self.admin_user.id)

    def test_admin_review_reject(self):
        """测试 Admin 拒绝事件请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.fm_reviewed_event content
        event_request_id = self.fm_handled_event.id
        
        # Now have Admin review it and reject
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('event-request-admin-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {
            'admin_decision': 'Event rejected due to budget concerns',
            'decision': 'rejected'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'rejected')
        self.assertEqual(response.data['admin_handler'], self.admin_user.id)
    
    def test_admin_review_invalid_status(self):
        """测试 Admin 审核无效状态的请求"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.submitted_event content
        event_request_id = self.submitted_event.id
        
        # Try to have Admin review a request not in 'fm_reviewed' status
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('event-request-admin-review', kwargs={'pk': event_request_id})

        response = self.client.post(url, {
            'admin_decision': 'Test Content',
            'decision': 'approved'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_scs_add_details_success(self):
        """测试 SCS 成功添加详细信息"""
        self.client.force_authenticate(user=self.cs_user)
        # first get self.approved_event content
        event_request_id = self.approved_event.id
        
        # Now have SCS add details
        self.client.force_authenticate(user=self.scs_user)
        url = reverse('event-request-add-details', kwargs={'pk': event_request_id})

        response = self.client.post(url, {
            'description_of_decorations': 'Modern theme with LED lighting',
            'description_of_meals': 'Vegan and gluten-free options included',
            'other_needs': 'High-speed WiFi required'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'open')