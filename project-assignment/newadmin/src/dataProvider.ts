import drfProvider from "ra-data-django-rest-framework";
import { fetchUtils, DataProvider } from "react-admin";

const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

// 资源名称映射：React Admin 资源名 -> Django API 端点
const resourceMap: Record<string, string> = {
  users: "users",
  posts: "posts",
  event_requests: "event-requests", // 下划线转连字符
  "event-requests-pending": "event-requests", // pending list 也使用 event-requests
  budget_approvals: "budget-approvals", // 关键映射：下划线转连字符
  "task-assignments": "task-assignments", // 任务分配
};

// 获取 CSRF token 的辅助函数
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

const httpClient = (url: string, options: fetchUtils.Options = {}) => {
  const csrfToken = getCsrfToken();

  return fetchUtils.fetchJson(url, {
    ...options,
    credentials: "include", // 确保所有请求都包含 session cookie
    headers: new Headers({
      ...options.headers,
      ...(csrfToken && { "X-CSRFToken": csrfToken }), // 添加 CSRF token
    }),
  });
};

const baseDataProvider = drfProvider(apiUrl, httpClient);

// 包装 dataProvider 以处理资源名称映射和自定义端点
const dataProvider: DataProvider = {
  ...baseDataProvider,
  getList: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;

    // 检查是否是 pending list 请求
    if (
      resource === "event-requests-pending" ||
      params?.filter?.pending === true
    ) {
      // 调用 pending_reviews 端点
      return httpClient(`${apiUrl}/${mappedResource}/pending_reviews/`, {
        method: "GET",
      }).then(({ json }) => ({
        data: json,
        total: json.length,
      }));
    }

    return baseDataProvider.getList(mappedResource, params);
  },
  getOne: (resource, params) => {
    // event-requests-pending 使用 event-requests 端点
    const mappedResource =
      resource === "event-requests-pending"
        ? "event-requests"
        : resourceMap[resource] || resource;
    return baseDataProvider.getOne(mappedResource, params);
  },
  getMany: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.getMany(mappedResource, params);
  },
  getManyReference: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.getManyReference(mappedResource, params);
  },
  create: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.create(mappedResource, params);
  },
  update: (resource, params) => {
    // Task Assignment actions
    if (resource === "task-assignments" && params.data.action) {
      const { id, data } = params;
      const action = data.action;
      const mappedResource = resourceMap[resource] || resource;

      const endpoint = `${apiUrl}/${mappedResource}/${id}/${action}/`;
      let payload: Record<string, unknown> = {};

      // 根据不同的 action 构造 payload
      if (action === "send_to_employee") {
        payload = {};
      } else if (action === "complete") {
        payload = {};
      } else if (action === "submit_plan") {
        payload = {
          employee_plan: data.employee_plan,
          estimated_budget: data.estimated_budget,
        };
      }

      return httpClient(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      }).then(({ json }) => ({ data: json }));
    }

    // Recruitment actions
    if (resource === "recruitments" && params.data.action) {
      const { id, data } = params;
      const action = data.action;
      const mappedResource = resourceMap[resource] || resource;

      const endpoint = `${apiUrl}/${mappedResource}/${id}/${action}/`;
      let payload: Record<string, unknown> = {};

      // 根据不同的 action 构造 payload
      if (action === "add_hires" && data.count) {
        payload = { count: data.count };
      } else if (action === "reject" && data.reason) {
        payload = { reason: data.reason };
      }

      return httpClient(endpoint, {
        method: "POST",
        body: JSON.stringify(payload),
      }).then(({ json }) => ({ data: json }));
    }

    // event-requests-pending 需要特殊处理
    if (resource === "event-requests-pending") {
      const mappedResource = "event-requests";
      const { id, data } = params;

      // 根据提交的数据判断调用哪个端点
      let endpoint = "";
      let payload = {};

      if (
        data.scs_comment !== undefined &&
        data.status !== "approved" &&
        data.status !== "rejected"
      ) {
        // SCS review
        endpoint = `${apiUrl}/${mappedResource}/${id}/scs_review/`;
        payload = { scs_comment: data.scs_comment };
      } else if (data.fm_feedback !== undefined) {
        // FM review
        endpoint = `${apiUrl}/${mappedResource}/${id}/fm_review/`;
        payload = { fm_feedback: data.fm_feedback };
      } else if (data.admin_decision !== undefined && data.status) {
        // Admin review
        endpoint = `${apiUrl}/${mappedResource}/${id}/admin_review/`;
        payload = {
          admin_decision: data.admin_decision,
          decision: data.status, // status field maps to decision
        };
      } else if (
        data.description_of_decorations !== undefined ||
        data.description_of_meals !== undefined
      ) {
        // SCS add details
        endpoint = `${apiUrl}/${mappedResource}/${id}/add_details/`;
        payload = {
          description_of_decorations: data.description_of_decorations,
          description_of_meals: data.description_of_meals,
          description_of_music: data.description_of_music,
          description_of_poster: data.description_of_poster,
          description_of_filming: data.description_of_filming,
          description_of_drinks: data.description_of_drinks,
          other_needs: data.other_needs,
        };
      }

      if (endpoint) {
        return httpClient(endpoint, {
          method: "POST",
          body: JSON.stringify(payload),
        }).then(({ json }) => ({ data: json }));
      }
    }

    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.update(mappedResource, params);
  },
  updateMany: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.updateMany(mappedResource, params);
  },
  delete: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.delete(mappedResource, params);
  },
  deleteMany: (resource, params) => {
    const mappedResource = resourceMap[resource] || resource;
    return baseDataProvider.deleteMany(mappedResource, params);
  },
};

export { dataProvider };
