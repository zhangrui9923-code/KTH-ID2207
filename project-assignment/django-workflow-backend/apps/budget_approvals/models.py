from django.db import models
from django.conf import settings


class BudgetApproval(models.Model):
    """
    预算审批工作流模型
    流程: Service/Product Manager -> Financial Manager 审批
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted to FM'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # 申请人 (Service Manager 或 Product Manager)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budget_requests'
    )

    # 关联的事件（可选）
    related_event = models.ForeignKey(
        'event_requests.EventRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_approvals'
    )
    
    requested_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="申请的预算金额"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    # Financial Manager 的处理
    fm_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_budgets'
    )
    fm_decision = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.requested_amount}"