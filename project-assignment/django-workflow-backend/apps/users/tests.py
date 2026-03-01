from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import User


class UserModelTestCase(TestCase):
    """用户模型测试"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'employee',
            'department': 'IT'
        }
    
    def test_create_user(self):
        """测试创建用户"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password='testpass123',
            role=self.user_data['role'],
            department=self.user_data['department']
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'employee')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username='john',
            role='admin'
        )
        self.assertIn('john', str(user))
        self.assertIn('Admin Manager', str(user))


class UserAPITestCase(APITestCase):
    """用户 API 测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'apipass123',
            'role': 'cs',
            'department': 'Customer Service',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890'
        }
    
    def test_user_login_success(self):
        """测试用户登录成功"""
        User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password='loginpass123'
        )
        url = reverse('user-login')
        response = self.client.post(url, {
            'username': 'loginuser',
            'password': 'loginpass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)

    def test_create_user_via_api(self):
        """测试通过 API 创建用户"""
        url = reverse('user-list')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'apiuser')
        # 密码不应该在响应中返回
        self.assertNotIn('password', response.data)
    
    def test_list_users(self):
        """测试获取用户列表"""
        # 创建测试用户
        User.objects.create_user(username='user1', email='user1@test.com', role='employee')
        User.objects.create_user(username='user2', email='user2@test.com', role='admin')
        
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_user(self):
        """测试获取单个用户详情"""
        user = User.objects.create_user(
            username='detailuser',
            email='detail@test.com',
            role='fm',
            department='Finance'
        )
        
        url = reverse('user-detail', kwargs={'pk': user.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'detailuser')
        self.assertEqual(response.data['department'], 'Finance')
    
    def test_update_user(self):
        """测试更新用户"""
        user = User.objects.create_user(
            username='updateuser',
            email='update@test.com',
            role='employee'
        )
        
        url = reverse('user-detail', kwargs={'pk': user.pk})
        update_data = {
            'username': 'updateuser',
            'email': 'newemail@test.com',
            'role': 'sm',
            'department': 'Service'
        }
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.email, 'newemail@test.com')
        self.assertEqual(user.role, 'sm')
    
    def test_partial_update_user(self):
        """测试部分更新用户"""
        user = User.objects.create_user(
            username='patchuser',
            email='patch@test.com',
            role='employee'
        )
        
        url = reverse('user-detail', kwargs={'pk': user.pk})
        patch_data = {'department': 'HR'}
        response = self.client.patch(url, patch_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.department, 'HR')
        self.assertEqual(user.username, 'patchuser')  # 其他字段不变
    
    def test_delete_user(self):
        """测试删除用户"""
        user = User.objects.create_user(
            username='deleteuser',
            email='delete@test.com'
        )
        
        url = reverse('user-detail', kwargs={'pk': user.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)
    
    def test_filter_users_by_role(self):
        """测试按角色过滤用户"""
        User.objects.create_user(username='admin1', role='admin')
        User.objects.create_user(username='admin2', role='admin')
        User.objects.create_user(username='employee1', role='employee')
        
        url = reverse('user-list')
        response = self.client.get(url, {'role': 'admin'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_search_users(self):
        """测试搜索用户"""
        User.objects.create_user(
            username='john_doe',
            email='john@test.com',
            first_name='John',
            last_name='Doe'
        )
        User.objects.create_user(
            username='jane_smith',
            email='jane@test.com',
            first_name='Jane',
            last_name='Smith'
        )
        
        url = reverse('user-list')
        response = self.client.get(url, {'search': 'john'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'john_doe')
    
    def test_password_is_hashed(self):
        """测试密码被正确加密"""
        url = reverse('user-list')
        response = self.client.post(url, self.user_data, format='json')
        
        user = User.objects.get(username='apiuser')
        # 密码不应该是明文
        self.assertNotEqual(user.password, 'apipass123')
        # 应该可以验证密码
        self.assertTrue(user.check_password('apipass123'))

