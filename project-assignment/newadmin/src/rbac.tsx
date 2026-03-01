// 定义角色类型
export type UserRole =
  | "admin"
  | "hr"
  | "employee"
  | "scs"
  | "cs"
  | "fm"
  | "sm"
  | "pm";

// 权限检查函数
export const permissions = {
  // 可以查看用户列表
  canViewUsers: (role: UserRole): boolean => {
    return role === "admin" || role === "hr";
  },

  // 可以编辑用户
  canEditUsers: (role: UserRole): boolean => {
    return role === "admin" || role === "hr";
  },

  // 可以创建用户
  canCreateUsers: (role: UserRole): boolean => {
    return role === "admin" || role === "hr";
  },

  // 可以删除用户
  canDeleteUsers: (role: UserRole): boolean => {
    return role === "admin";
  },

  // 是否是管理员
  isAdmin: (role: UserRole): boolean => {
    return role === "admin";
  },

  // 是否是 HR
  isHR: (role: UserRole): boolean => {
    return role === "hr";
  },
};
