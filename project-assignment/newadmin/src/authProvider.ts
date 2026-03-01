import { AuthProvider } from "react-admin";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const getCsrfToken = (): string | null => {
  const name = "csrftoken";
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.trim().split("=");
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return null;
};

export const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    try {
      await fetch(`${apiUrl}/users/login/`, {
        method: "GET",
        credentials: "include",
      }).catch(() => {});

      const csrfToken = getCsrfToken();

      const response = await fetch(`${apiUrl}/users/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken && { "X-CSRFToken": csrfToken }),
        },
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "登录失败");
      }

      const data = await response.json();

      localStorage.setItem("user", JSON.stringify(data.user));
      localStorage.setItem("username", username);
      localStorage.setItem("role", data.user.role); // 存储角色

      return Promise.resolve();
    } catch (error) {
      return Promise.reject(error);
    }
  },

  logout: async () => {
    try {
      const csrfToken = getCsrfToken();
      await fetch(`${apiUrl}/users/logout/`, {
        method: "POST",
        headers: {
          ...(csrfToken && { "X-CSRFToken": csrfToken }),
        },
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    }

    localStorage.removeItem("user");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    return Promise.resolve();
  },

  checkAuth: () => {
    return localStorage.getItem("user") ? Promise.resolve() : Promise.reject();
  },

  checkError: (error) => {
    const status = error.status;
    if (status === 401 || status === 403) {
      localStorage.removeItem("user");
      localStorage.removeItem("username");
      localStorage.removeItem("role");
      return Promise.reject();
    }
    return Promise.resolve();
  },

  getIdentity: () => {
    try {
      const userStr = localStorage.getItem("user");
      if (userStr) {
        const user = JSON.parse(userStr);
        return Promise.resolve({
          id: user.id,
          fullName: user.username,
          avatar: user.avatar,
        });
      }
      return Promise.reject();
    } catch {
      return Promise.reject();
    }
  },

  getPermissions: () => {
    // 返回用户角色作为权限
    const role = localStorage.getItem("role");
    console.log("当前用户角色:", role);
    return role ? Promise.resolve(role) : Promise.reject();
  },
};
