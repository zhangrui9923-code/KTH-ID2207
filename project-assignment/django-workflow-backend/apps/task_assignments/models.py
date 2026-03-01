from django.db import models
from django.conf import settings


class TaskAssignment(models.Model):
    """
    任务分配工作流模型
    流程: Service/Product Manager 分配任务 -> Employee 填写计划和预算返回
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent_to_employee', 'Sent to Employee'),
        ('plan_submitted', 'Plan Submitted'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Manager (Service Manager 或 Product Manager)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    
    # 被分配的员工
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_tasks'
    )
    
    # 时间段
    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 员工的反馈
    employee_plan = models.TextField(blank=True, help_text="员工填写的工作计划")
    estimated_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="预估预算"
    )
    employee_submitted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.employee.username}"

