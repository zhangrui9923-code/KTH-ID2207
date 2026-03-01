from django.db import models
from django.conf import settings


class Recruitment(models.Model):
    """
    招聘申请工作流模型
    流程: Service/Product Manager 提交申请 -> HR Manager 处理招聘
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted to HR'),
        ('in_progress', 'Recruiting'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    position_title = models.CharField(max_length=200, help_text="招聘职位")
    description = models.TextField(help_text="职位描述和要求")
    
    # 申请人 (Service Manager 或 Product Manager)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruitment_requests'
    )
    
    department = models.CharField(max_length=100)
    number_of_positions = models.PositiveIntegerField(default=1, help_text="招聘人数")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # HR Manager 的处理
    hr_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_recruitments'
    )
    hr_notes = models.TextField(blank=True, help_text="HR 备注")
    
    # 招聘结果
    candidates_interviewed = models.PositiveIntegerField(default=0)
    positions_filled = models.PositiveIntegerField(default=0)
    
    started_at = models.DateTimeField(null=True, blank=True, help_text="开始招聘时间")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="完成招聘时间")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.position_title} - {self.department}"

