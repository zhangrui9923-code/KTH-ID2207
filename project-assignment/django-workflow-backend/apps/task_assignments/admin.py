from django.contrib import admin
from django.utils.html import format_html
from .models import TaskAssignment


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    """任务分配管理后台"""

    list_display = [
        'title',
        'manager',
        'employee',
        'status_badge',
        'start_date',
        'end_date',
        'estimated_budget',
        'created_at'
    ]

    list_filter = [
        'status',
        'start_date',
        'end_date',
        'created_at'
    ]

    search_fields = [
        'title',
        'description',
        'manager__username',
        'manager__email',
        'employee__username',
        'employee__email',
        'employee_plan'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'employee_submitted_at'
    ]

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'status')
        }),
        ('人员分配', {
            'fields': ('manager', 'employee')
        }),
        ('时间安排', {
            'fields': ('start_date', 'end_date')
        }),
        ('员工反馈', {
            'fields': ('employee_plan', 'estimated_budget', 'employee_submitted_at'),
            'classes': ('collapse',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    date_hierarchy = 'created_at'

    ordering = ['-created_at']

    list_per_page = 20

    def status_badge(self, obj):
        """显示带颜色的状态标签"""
        colors = {
            'pending': '#6c757d',
            'sent_to_employee': '#0dcaf0',
            'plan_submitted': '#ffc107',
            'completed': '#198754'
        }
        status_names = {
            'pending': '待处理',
            'sent_to_employee': '已发送',
            'plan_submitted': '已提交计划',
            'completed': '已完成'
        }
        color = colors.get(obj.status, '#6c757d')
        name = status_names.get(obj.status, obj.get_status_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color, name
        )

    status_badge.short_description = '状态'

    def get_queryset(self, request):
        """优化查询性能"""
        qs = super().get_queryset(request)
        return qs.select_related('manager', 'employee')

    actions = ['mark_as_sent', 'mark_as_completed']

    def mark_as_sent(self, request, queryset):
        """批量标记为已发送"""
        updated = queryset.filter(status='pending').update(status='sent_to_employee')
        self.message_user(request, f'成功将 {updated} 个任务标记为已发送')

    mark_as_sent.short_description = '标记选中任务为已发送'

    def mark_as_completed(self, request, queryset):
        """批量标记为已完成"""
        updated = queryset.filter(status='plan_submitted').update(status='completed')
        self.message_user(request, f'成功将 {updated} 个任务标记为已完成')

    mark_as_completed.short_description = '标记选中任务为已完成'