from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    扩展的用户模型，支持不同角色
    """
    ROLE_CHOICES = [
        ('admin', 'Admin Manager'),
        ('cs', 'Customer Service'),
        ('scs', 'Senior Customer Service'),
        ('fm', 'Financial Manager'),
        ('sm', 'Service Manager'),
        ('pm', 'Product Manager'),
        ('hrm', 'HR Manager'),
        ('employee', 'Employee'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

