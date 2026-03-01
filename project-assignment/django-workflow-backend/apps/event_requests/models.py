from django.db import models
from django.conf import settings


class EventRequest(models.Model):
    """
    事件请求工作流模型
    流程: Customer Service -> Senior Customer Service -> Financial Manager -> Admin Manager
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted to SCS'),
        ('scs_reviewed', 'SCS Reviewed'),
        ('fm_reviewed', 'FM Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    record_number = models.CharField(max_length=20, unique=True,default='')
    client_name = models.CharField(max_length=100,default='')
    event_type = models.CharField(max_length=100,default='')
    expected_number = models.IntegerField(default=0)
    expected_budget = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    from_date = models.DateField(default=None)
    to_date = models.DateField(default=None)
    has_decorations = models.BooleanField(default=False)
    has_meals = models.BooleanField(default=False)
    has_parties = models.BooleanField(default=False)
    has_drinks = models.BooleanField(default=False)
    has_filming = models.BooleanField(default=False)
    description_of_decorations = models.TextField(blank=True)
    description_of_meals = models.TextField(blank=True)
    description_of_music = models.TextField(blank=True)
    description_of_poster = models.TextField(blank=True)
    description_of_filming = models.TextField(blank=True)
    description_of_drinks = models.TextField(blank=True)    
    other_needs = models.TextField(blank=True)

    # 创建者 (Customer Service)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_event_requests'
    )
    
    # 当前处理人
    current_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handling_event_requests'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Senior Customer Service 的处理
    scs_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scs_event_requests'
    )
    scs_comment = models.TextField(blank=True)
    scs_handled_at = models.DateTimeField(null=True, blank=True)
    
    # Financial Manager 的处理
    fm_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fm_event_requests'
    )
    fm_feedback = models.TextField(blank=True)
    fm_handled_at = models.DateTimeField(null=True, blank=True)
    
    # Admin Manager 的最终决定
    admin_handler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_event_requests'
    )
    admin_decision = models.TextField(blank=True)
    admin_handled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

