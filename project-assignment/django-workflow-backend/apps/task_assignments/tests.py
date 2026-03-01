from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal

from .models import TaskAssignment

User = get_user_model()


class TaskAssignmentModelTest(TestCase):
    """TaskAssignment模型测试"""

    def setUp(self):
        """设置测试数据"""
        self.manager = User.objects.create_user(
            username='manager1',
            email='manager1@example.com',
            password='testpass123'
        )
        self.employee = User.objects.create_user(
            username='employee1',
            email='employee1@example.com',
            password='testpass123'
        )

        self.task = TaskAssignment.objects.create(
            title='测试任务',
            description='这是一个测试任务',
            manager=self.manager,
            employee=self.employee,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )

    def test_task_creation(self):
        """测试任务创建"""
        self.assertEqual(self.task.title, '测试任务')
        self.assertEqual(self.task.status, 'pending')
        self.assertEqual(self.task.manager, self.manager)
        self.assertEqual(self.task.employee, self.employee)
        self.assertIsNotNone(self.task.created_at)
        self.assertIsNotNone(self.task.updated_at)

    def test_task_str_representation(self):
        """测试字符串表示"""
        expected = f"测试任务 - {self.employee.username}"
        self.assertEqual(str(self.task), expected)

    def test_task_status_choices(self):
        """测试状态选项"""
        valid_statuses = ['pending', 'sent_to_employee', 'plan_submitted', 'completed']
        for status_value in valid_statuses:
            self.task.status = status_value
            self.task.save()
            self.assertEqual(self.task.status, status_value)

    def test_task_ordering(self):
        """测试默认排序（按创建时间降序）"""
        task2 = TaskAssignment.objects.create(
            title='第二个任务',
            description='测试排序',
            manager=self.manager,
            employee=self.employee,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )
        tasks = TaskAssignment.objects.all()
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], self.task)


class TaskAssignmentAPITest(APITestCase):
    """任务分配API测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = APIClient()

        # 创建测试用户
        self.manager = User.objects.create_user(
            username='manager1',
            email='manager1@example.com',
            password='testpass123'
        )
        self.employee = User.objects.create_user(
            username='employee1',
            email='employee1@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123'
        )

        # 创建测试任务
        self.task = TaskAssignment.objects.create(
            title='测试任务',
            description='这是一个测试任务',
            manager=self.manager,
            employee=self.employee,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status='pending'
        )

        self.list_url = '/api/task-assignments/'
        self.detail_url = f'/api/task-assignments/{self.task.id}/'

    def test_authentication_required(self):
        """测试需要认证"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_as_manager(self):
        """测试Manager创建任务"""
        self.client.force_authenticate(user=self.manager)

        data = {
            'title': '新任务',
            'description': '新任务描述',
            'employee': self.employee.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=10))
        }

        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], '新任务')
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['manager']['id'], self.manager.id)

    def test_create_task_invalid_dates(self):
        """测试创建任务时日期验证"""
        self.client.force_authenticate(user=self.manager)

        data = {
            'title': '新任务',
            'description': '新任务描述',
            'employee': self.employee.id,
            'start_date': str(date.today() + timedelta(days=10)),
            'end_date': str(date.today())
        }

        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_tasks_as_manager(self):
        """测试Manager查看任务列表"""
        self.client.force_authenticate(user=self.manager)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_tasks_as_employee(self):
        """测试Employee查看任务列表"""
        self.client.force_authenticate(user=self.employee)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_retrieve_task(self):
        """测试获取任务详情"""
        self.client.force_authenticate(user=self.manager)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task.id)
        self.assertEqual(response.data['title'], self.task.title)

    def test_update_task_as_manager(self):
        """测试Manager更新任务"""
        self.client.force_authenticate(user=self.manager)

        data = {
            'title': '更新的任务标题',
            'description': '更新的描述'
        }

        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '更新的任务标题')

    def test_update_task_as_employee_forbidden(self):
        """测试Employee不能更新任务基本信息"""
        self.client.force_authenticate(user=self.employee)

        data = {
            'title': '尝试更新'
        }

        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_as_manager(self):
        """测试Manager删除任务"""
        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaskAssignment.objects.filter(id=self.task.id).exists())

    def test_delete_task_as_employee_forbidden(self):
        """测试Employee不能删除任务"""
        self.client.force_authenticate(user=self.employee)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_send_to_employee(self):
        """测试发送任务给员工"""
        self.client.force_authenticate(user=self.manager)

        url = f'/api/task-assignments/{self.task.id}/send_to_employee/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'sent_to_employee')

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'sent_to_employee')

    def test_send_to_employee_invalid_status(self):
        """测试在错误状态下发送任务"""
        self.task.status = 'completed'
        self.task.save()

        self.client.force_authenticate(user=self.manager)

        url = f'/api/task-assignments/{self.task.id}/send_to_employee/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_plan_as_employee(self):
        """测试员工提交计划"""
        self.task.status = 'sent_to_employee'
        self.task.save()

        self.client.force_authenticate(user=self.employee)

        url = f'/api/task-assignments/{self.task.id}/submit_plan/'
        data = {
            'employee_plan': '我的工作计划\n1. 第一步\n2. 第二步',
            'estimated_budget': '5000.00'
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'plan_submitted')

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'plan_submitted')
        self.assertEqual(self.task.employee_plan, data['employee_plan'])
        self.assertEqual(self.task.estimated_budget, Decimal('5000.00'))
        self.assertIsNotNone(self.task.employee_submitted_at)

    def test_submit_plan_as_manager_forbidden(self):
        """测试Manager不能提交计划"""
        self.task.status = 'sent_to_employee'
        self.task.save()

        self.client.force_authenticate(user=self.manager)

        url = f'/api/task-assignments/{self.task.id}/submit_plan/'
        data = {
            'employee_plan': '尝试提交',
            'estimated_budget': '1000.00'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_task(self):
        """测试完成任务"""
        self.task.status = 'plan_submitted'
        self.task.save()

        self.client.force_authenticate(user=self.manager)

        url = f'/api/task-assignments/{self.task.id}/complete/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_complete_task_invalid_status(self):
        """测试在错误状态下完成任务"""
        self.task.status = 'pending'
        self.task.save()

        self.client.force_authenticate(user=self.manager)

        url = f'/api/task-assignments/{self.task.id}/complete/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_assigned_tasks(self):
        """测试获取我分配的任务"""
        # 创建另一个任务
        other_task = TaskAssignment.objects.create(
            title='另一个任务',
            description='测试',
            manager=self.other_user,
            employee=self.employee,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.manager)

        url = '/api/task-assignments/my_assigned_tasks/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 应该只看到manager1的任务
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task.id)

    def test_my_received_tasks(self):
        """测试获取我接收的任务"""
        # 创建另一个员工和任务
        other_employee = User.objects.create_user(
            username='employee2',
            password='testpass123'
        )
        other_task = TaskAssignment.objects.create(
            title='另一个任务',
            description='测试',
            manager=self.manager,
            employee=other_employee,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )

        self.client.force_authenticate(user=self.employee)

        url = '/api/task-assignments/my_received_tasks/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 应该只看到employee1的任务
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task.id)

    def test_status_filter(self):
        """测试状态过滤"""
        # 创建不同状态的任务
        TaskAssignment.objects.create(
            title='已完成任务',
            description='测试',
            manager=self.manager,
            employee=self.employee,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            status='completed'
        )

        self.client.force_authenticate(user=self.manager)

        url = '/api/task-assignments/my_assigned_tasks/?status=pending'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'pending')

    def test_other_user_cannot_access_task(self):
        """测试无关用户不能访问任务"""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TaskAssignmentWorkflowTest(APITestCase):
    """任务分配工作流集成测试"""

    def setUp(self):
        """设置测试数据"""
        self.client = APIClient()

        self.manager = User.objects.create_user(
            username='manager1',
            password='testpass123'
        )
        self.employee = User.objects.create_user(
            username='employee1',
            password='testpass123'
        )

    def test_complete_workflow(self):
        """测试完整的任务工作流"""
        # 1. Manager创建任务
        self.client.force_authenticate(user=self.manager)

        create_data = {
            'title': '完整流程测试',
            'description': '测试完整工作流',
            'employee': self.employee.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=14))
        }

        response = self.client.post('/api/task-assignments/', create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task_id = response.data['id']
        self.assertEqual(response.data['status'], 'pending')

        # 2. Manager发送任务给Employee
        send_url = f'/api/task-assignments/{task_id}/send_to_employee/'
        response = self.client.post(send_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'sent_to_employee')

        # 3. Employee查看任务
        self.client.force_authenticate(user=self.employee)

        detail_url = f'/api/task-assignments/{task_id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'sent_to_employee')

        # 4. Employee提交计划和预算
        submit_url = f'/api/task-assignments/{task_id}/submit_plan/'
        plan_data = {
            'employee_plan': '详细工作计划\n阶段一：需求分析\n阶段二：开发实施',
            'estimated_budget': '12000.00'
        }

        response = self.client.post(submit_url, plan_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'plan_submitted')
        self.assertIsNotNone(response.data['employee_submitted_at'])

        # 5. Manager审核并完成任务
        self.client.force_authenticate(user=self.manager)

        complete_url = f'/api/task-assignments/{task_id}/complete/'
        response = self.client.post(complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

        # 6. 验证最终状态
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['employee_plan'], plan_data['employee_plan'])
        self.assertEqual(response.data['estimated_budget'], plan_data['estimated_budget'])