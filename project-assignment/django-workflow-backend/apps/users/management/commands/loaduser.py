from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = '创建测试用户数据'

    def handle(self, *args, **kwargs):
        users_data = [
            {
                "username": "Mike",
                "email": "mike@sep.com",
                "password": "123456",
                "role": "admin"
            },
            {
                "username": "Simon",
                "email": "simon@sep.com",
                "password": "123456",
                "role": "hrm"
            },
            {
                "username": "Janet",
                "email": "janet@sep.com",
                "password": "123456",
                "role": "scs"
            },
            {
                "username": "Sarah",
                "email": "sarah@sep.com",
                "password": "123456",
                "role": "cs"
            },
            {
                "username": "Alice",
                "email": "alice@sep.com",
                "password": "123456",
                "role": "fm"
            },
            {
                "username": "Jack",
                "email": "jack@sep.com",
                "password": "123456",
                "role": "pm"
            },
            {
                "username": "Natalie",
                "email": "natalie@sep.com",
                "password": "123456",
                "role": "sm"
            },
            {
                "username": "Antony",
                "email": "antony@sep.com",
                "password": "123456",
                "role": "employee",
                "department": "Product"
            },
            {
                "username": "Helen",
                "email": "helen@sep.com",
                "password": "123456",
                "role": "employee",
                "department": "Service"
            },
        ]

        created_count = 0
        for user_data in users_data:
            username = user_data['username']
            
            # 检查用户是否已存在
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'用户 {username} 已存在，跳过')
                )
                continue
            
            # 创建用户
            password = user_data.pop('password')
            user = User.objects.create_user(**user_data)
            user.set_password(password)
            user.save()
            
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ 成功创建用户: {username} ({user.get_role_display()})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n总计创建 {created_count} 个用户')
        )