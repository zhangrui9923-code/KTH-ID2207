import { Admin, Resource, ShowGuesser } from "react-admin";
import { dataProvider } from "./dataProvider";
import { authProvider } from "./authProvider";
import { Dashboard } from "./Dashboard";
import { Layout } from "./Layout";
import { UserList, UserEdit, UserCreate } from "./users";
import { BudgetRequestList } from "./BudgetRequestList";
import { BudgetRequestEdit } from "./BudgetRequestEdit";
import { BudgetRequestCreate } from "./BudgetRequestCreate";
import {
  EventRequestCreate,
  EventRequestList,
  EventRequestPendingList,
  EventRequestPendingEdit,
} from "./event";
import {
  RecruitmentCreate,
  RecruitmentList,
  RecruitmentEdit,
} from "./recruitement";
import {
  TaskAssignmentCreate,
  TaskAssignmentList,
  TaskAssignmentManagerEdit,
  TaskAssignmentEmployeeList,
  TaskAssignmentEmployeeEdit,
} from "./task";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import PeopleIcon from "@mui/icons-material/People";
import EventIcon from "@mui/icons-material/Event";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import WorkIcon from "@mui/icons-material/Work";
import AssignmentIcon from "@mui/icons-material/Assignment";

// 根据权限动态渲染资源
const AppWithPermissions = () => {
  return (
    <Admin
      dataProvider={dataProvider}
      authProvider={authProvider}
      dashboard={Dashboard}
      layout={Layout}
    >
      {(permissions) => (
        <>
          {/* Users 资源 - 只有 admin 和 hr 可以看到 */}
          {(permissions === "admin" || permissions === "hrm") && (
            <Resource
              name="users"
              list={UserList}
              edit={UserEdit}
              create={UserCreate}
              icon={PeopleIcon}
              options={{ label: "User Management" }}
            />
          )}

          {/* event_requests 资源 - 所有角色都可以看到 */}
          <Resource
            name="event-requests"
            create={EventRequestCreate}
            list={EventRequestList}
            show={ShowGuesser}
            icon={EventIcon}
            options={{ label: "Event Requests" }}
          />

          {/* event-requests-pending 资源 - 待处理的事件请求 */}
          {(permissions === "scs" ||
            permissions === "fm" ||
            permissions === "admin") && (
            <Resource
              name="event-requests-pending"
              list={EventRequestPendingList}
              edit={EventRequestPendingEdit}
              icon={PendingActionsIcon}
              options={{ label: "Pending Events" }}
            />
          )}

          {/* Budget请求，只有fm看到完整，sm和pm看到自己创建的，其余不可见，不过access control已被后端实现，前端只需要保证页面可见 */}
          {(permissions === "sm" ||
            permissions === "pm" ||
            permissions === "fm") && (
            <Resource
              name="budget-approvals"
              list={BudgetRequestList}
              create={permissions !== "fm" ? BudgetRequestCreate : undefined}
              edit={permissions === "fm" ? BudgetRequestEdit : undefined}
              show={ShowGuesser}
              icon={AttachMoneyIcon}
              options={{ label: "Budget" }}
            />
          )}

          {/* Recruitment - PM/SM 可以创建，HR 可以处理 */}
          {(permissions === "pm" ||
            permissions === "sm" ||
            permissions === "hrm" ||
            permissions === "admin") && (
            <Resource
              name="recruitments"
              list={RecruitmentList}
              create={
                permissions === "pm" || permissions === "sm"
                  ? RecruitmentCreate
                  : undefined
              }
              edit={RecruitmentEdit}
              show={ShowGuesser}
              icon={WorkIcon}
              options={{ label: "Recruitments" }}
            />
          )}

          {/* Task Assignments - Manager (SM/PM) 可以创建和管理任务 */}
          {(permissions === "sm" || permissions === "pm") && (
            <Resource
              name="task-assignments"
              list={TaskAssignmentList}
              create={TaskAssignmentCreate}
              edit={TaskAssignmentManagerEdit}
              show={ShowGuesser}
              icon={AssignmentIcon}
              options={{ label: "Task Assignments" }}
            />
          )}

          {/* Task Assignments - Employee 查看和提交任务 */}
          {permissions === "employee" && (
            <Resource
              name="task-assignments"
              list={TaskAssignmentEmployeeList}
              edit={TaskAssignmentEmployeeEdit}
              icon={AssignmentIcon}
              options={{ label: "My Tasks" }}
            />
          )}
        </>
      )}
    </Admin>
  );
};

export const App = () => <AppWithPermissions />;
