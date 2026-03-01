from rest_framework import permissions


class IsManagerOrEmployee(permissions.BasePermission):
    """
    自定义权限类：
    - Manager可以创建、更新、删除自己的任务
    - Employee可以查看分配给自己的任务并提交计划
    """

    def has_permission(self, request, view):
        """所有认证用户都可以访问列表和详情"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        对象级权限检查
        - Manager: 只能操作自己创建的任务
        - Employee: 只能查看和更新分配给自己的任务
        """
        # 如果是GET请求，允许manager和employee查看相关任务
        if request.method in permissions.SAFE_METHODS:
            return obj.manager == request.user or obj.employee == request.user

        # 对于非安全方法（PUT, PATCH, DELETE）
        # Manager才能修改任务（除了submit_plan action）
        if hasattr(view, 'action'):
            # submit_plan action由employee执行
            if view.action == 'submit_plan':
                return obj.employee == request.user
            # 其他修改操作由manager执行
            else:
                return obj.manager == request.user

        # 默认只有manager可以修改
        return obj.manager == request.user