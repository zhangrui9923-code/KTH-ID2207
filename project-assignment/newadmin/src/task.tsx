import {
  Create,
  SimpleForm,
  TextInput,
  DateInput,
  NumberInput,
  SelectInput,
  ReferenceInput,
  ReferenceField,
  required,
  DataTable,
  List,
  DateField,
  Edit,
  usePermissions,
  useRecordContext,
  TextField,
  useGetList,
  FilterButton,
  CreateButton,
  TopToolbar,
  Button,
  useDataProvider,
  useNotify,
  useRefresh,
} from "react-admin";
import { Typography, Box, Chip, Card, CardContent } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

// 类型定义
interface User {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  role?: string;
  department?: string;
}

// 辅助函数：格式化用户显示名称
const formatUserName = (user: User) => {
  if (user.first_name && user.last_name) {
    return `${user.username} - ${user.first_name} ${user.last_name}`;
  }
  return user.username;
};

// ==================== Manager (SM/PM) 创建任务 ====================
export const TaskAssignmentCreate = () => {
  const { permissions } = usePermissions();
  const { data: events } = useGetList("event-requests", {
    filter: { status: ["open", "in_progress"] },
  });

  // 根据角色确定部门过滤
  const getDepartmentFilter = () => {
    if (permissions === "sm") {
      return { role: "employee", department: "Service" };
    } else if (permissions === "pm") {
      return { role: "employee", department: "Product" };
    }
    return { role: "employee" };
  };

  return (
    <Create redirect="list">
      <SimpleForm>
        <Typography variant="h6" gutterBottom>
          Create New Task Assignment
        </Typography>

        <TextInput
          source="title"
          label="Task Title"
          validate={required()}
          fullWidth
        />

        <TextInput
          source="description"
          label="Task Description"
          multiline
          rows={4}
          validate={required()}
          fullWidth
        />

        <ReferenceInput
          source="employee"
          reference="users"
          label="Assign To Employee"
          filter={getDepartmentFilter()}
        >
          <SelectInput
            optionText={formatUserName}
            validate={required()}
            fullWidth
          />
        </ReferenceInput>

        <SelectInput
          source="related_event"
          label="Related Event Request (Optional)"
          choices={
            events?.map((event) => ({
              id: event.id,
              name: `${event.record_number} - ${event.client_name} (${event.status_display})`,
            })) || []
          }
          fullWidth
        />

        <DateInput
          source="start_date"
          label="Start Date"
          validate={required()}
        />

        <DateInput source="end_date" label="End Date" validate={required()} />
      </SimpleForm>
    </Create>
  );
};

// ==================== Manager 查看已分配的任务列表 ====================
export const TaskAssignmentList = () => {
  const { permissions } = usePermissions();
  const isManager = permissions === "sm" || permissions === "pm";

  // 根据角色确定部门过滤
  const getEmployeeFilter = () => {
    if (permissions === "sm") {
      return { role: "employee", department: "Service" };
    } else if (permissions === "pm") {
      return { role: "employee", department: "Product" };
    }
    return { role: "employee" };
  };

  const taskFilters = [
    <TextInput key="title" source="title" label="Search Title" alwaysOn />,
    <SelectInput
      key="status"
      source="status"
      label="Status"
      choices={[
        { id: "pending", name: "Pending" },
        { id: "sent_to_employee", name: "Sent to Employee" },
        { id: "plan_submitted", name: "Plan Submitted" },
        { id: "completed", name: "Completed" },
      ]}
    />,
    <ReferenceInput
      key="employee"
      source="employee"
      reference="users"
      label="Employee"
      filter={getEmployeeFilter()}
    >
      <SelectInput optionText={formatUserName} />
    </ReferenceInput>,
  ];

  const ListActions = () => (
    <TopToolbar>
      <FilterButton />
      {isManager && <CreateButton />}
    </TopToolbar>
  );

  return (
    <List
      title="Task Assignments"
      actions={<ListActions />}
      filters={taskFilters}
      sort={{ field: "created_at", order: "DESC" }}
    >
      <DataTable>
        <DataTable.Col source="id" label="ID" />
        <DataTable.Col source="title" label="Title" />
        <DataTable.Col source="status_display" label="Status">
          <StatusChipField />
        </DataTable.Col>
        <DataTable.Col source="employee" label="Assigned To">
          <ReferenceField source="employee" reference="users" link={false}>
            <TextField source="username" />
          </ReferenceField>
        </DataTable.Col>
        {isManager && (
          <DataTable.Col source="manager" label="Created By">
            <ReferenceField source="manager" reference="users" link={false}>
              <TextField source="username" />
            </ReferenceField>
          </DataTable.Col>
        )}
        <DataTable.Col source="start_date" label="Start Date">
          <DateField source="start_date" locales="en-US" />
        </DataTable.Col>
        <DataTable.Col source="end_date" label="End Date">
          <DateField source="end_date" locales="en-US" />
        </DataTable.Col>
        <DataTable.Col source="created_at" label="Created">
          <DateField source="created_at" locales="en-US" showTime />
        </DataTable.Col>
      </DataTable>
    </List>
  );
};

// 状态显示芯片组件
const StatusChipField = () => {
  const record = useRecordContext();
  if (!record) return null;

  const statusColors: Record<
    string,
    "default" | "info" | "warning" | "success"
  > = {
    pending: "default",
    sent_to_employee: "info",
    plan_submitted: "warning",
    completed: "success",
  };

  return (
    <Chip
      label={record.status_display}
      color={statusColors[record.status] || "default"}
      size="small"
    />
  );
};

// ==================== Manager 编辑和管理任务 ====================
export const TaskAssignmentManagerEdit = () => {
  const { permissions } = usePermissions();
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  // 根据角色确定部门过滤
  const getEmployeeFilter = () => {
    if (permissions === "sm") {
      return { role: "employee", department: "Service" };
    } else if (permissions === "pm") {
      return { role: "employee", department: "Product" };
    }
    return { role: "employee" };
  };

  const TaskEditContent = () => {
    const record = useRecordContext();

    if (!record) return null;

    const handleSendToEmployee = async () => {
      try {
        await dataProvider.update("task-assignments", {
          id: record.id,
          data: { action: "send_to_employee" },
          previousData: record,
        });
        notify("Task sent to employee successfully", { type: "success" });
        refresh();
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to send task";
        notify(message, { type: "error" });
      }
    };

    const handleComplete = async () => {
      try {
        await dataProvider.update("task-assignments", {
          id: record.id,
          data: { action: "complete" },
          previousData: record,
        });
        notify("Task marked as completed", { type: "success" });
        refresh();
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to complete task";
        notify(message, { type: "error" });
      }
    };

    return (
      <Box>
        {/* 基本信息编辑 */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Task Information
            </Typography>

            <TextInput
              source="title"
              label="Task Title"
              validate={required()}
              fullWidth
              disabled={record.status !== "pending"}
            />

            <TextInput
              source="description"
              label="Task Description"
              multiline
              rows={4}
              validate={required()}
              fullWidth
              disabled={record.status !== "pending"}
            />

            <ReferenceInput
              source="employee"
              reference="users"
              label="Assign To Employee"
              filter={getEmployeeFilter()}
            >
              <SelectInput
                optionText={formatUserName}
                validate={required()}
                fullWidth
                disabled={record.status !== "pending"}
              />
            </ReferenceInput>

            <DateInput
              source="start_date"
              label="Start Date"
              validate={required()}
              disabled={record.status !== "pending"}
            />

            <DateInput
              source="end_date"
              label="End Date"
              validate={required()}
              disabled={record.status !== "pending"}
            />

            <TextField source="status_display" label="Current Status" />
          </CardContent>
        </Card>

        {/* 员工提交的计划和预算（只读） */}
        {record.employee_plan && (
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Employee Submission
              </Typography>

              <TextInput
                source="employee_plan"
                label="Work Plan"
                multiline
                rows={4}
                fullWidth
                disabled
              />

              <NumberInput
                source="estimated_budget"
                label="Estimated Budget"
                disabled
                fullWidth
              />

              <DateField
                source="employee_submitted_at"
                label="Submitted At"
                locales="en-US"
                showTime
              />
            </CardContent>
          </Card>
        )}

        {/* 操作按钮 */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Actions
            </Typography>

            <Box sx={{ display: "flex", gap: 2 }}>
              {record.status === "pending" && (
                <Button
                  label="Send to Employee"
                  onClick={handleSendToEmployee}
                  startIcon={<SendIcon />}
                  variant="contained"
                />
              )}

              {record.status === "plan_submitted" && (
                <Button
                  label="Mark as Completed"
                  onClick={handleComplete}
                  startIcon={<CheckCircleIcon />}
                  variant="contained"
                  color="success"
                />
              )}
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  };

  return (
    <Edit>
      <SimpleForm toolbar={<></>}>
        <TaskEditContent />
      </SimpleForm>
    </Edit>
  );
};

// ==================== Employee 查看收到的任务 ====================
export const TaskAssignmentEmployeeList = () => {
  const employeeFilters = [
    <TextInput key="title" source="title" label="Search Title" alwaysOn />,
    <SelectInput
      key="status"
      source="status"
      label="Status"
      choices={[
        { id: "sent_to_employee", name: "Sent to Employee" },
        { id: "plan_submitted", name: "Plan Submitted" },
        { id: "completed", name: "Completed" },
      ]}
    />,
  ];

  return (
    <List
      title="My Tasks"
      resource="task-assignments"
      filter={{ employee_view: true }}
      filters={employeeFilters}
      sort={{ field: "created_at", order: "DESC" }}
    >
      <DataTable>
        <DataTable.Col source="id" label="ID" />
        <DataTable.Col source="title" label="Task Title" />
        <DataTable.Col source="status_display" label="Status">
          <StatusChipField />
        </DataTable.Col>
        <DataTable.Col source="manager" label="Assigned By">
          <ReferenceField source="manager" reference="users" link={false}>
            <TextField source="username" />
          </ReferenceField>
        </DataTable.Col>
        <DataTable.Col source="start_date" label="Start Date">
          <DateField source="start_date" locales="en-US" />
        </DataTable.Col>
        <DataTable.Col source="end_date" label="Due Date">
          <DateField source="end_date" locales="en-US" />
        </DataTable.Col>
        <DataTable.Col source="created_at" label="Created">
          <DateField source="created_at" locales="en-US" showTime />
        </DataTable.Col>
      </DataTable>
    </List>
  );
};

// ==================== Employee 编辑任务（提交计划） ====================
export const TaskAssignmentEmployeeEdit = () => {
  const dataProvider = useDataProvider();
  const notify = useNotify();
  const refresh = useRefresh();

  const handleSubmitPlan = async (data: Record<string, unknown>) => {
    try {
      await dataProvider.update("task-assignments", {
        id: data.id as number,
        data: {
          action: "submit_plan",
          employee_plan: data.employee_plan,
          estimated_budget: data.estimated_budget,
        },
        previousData: data,
      });
      notify("Plan submitted successfully", { type: "success" });
      refresh();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to submit plan";
      notify(message, { type: "error" });
    }
  };

  const EmployeeEditContent = () => {
    const record = useRecordContext();

    if (!record) return null;

    const canSubmitPlan =
      record.status === "sent_to_employee" ||
      record.status === "plan_submitted";

    // 如果任务状态是 pending，不允许 employee 查看
    if (record.status === "pending") {
      return (
        <Card>
          <CardContent>
            <Typography variant="h6" color="warning.main">
              This task is not yet assigned to you.
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Please wait for the manager to send this task to you.
            </Typography>
          </CardContent>
        </Card>
      );
    }

    return (
      <Box>
        {/* 任务详情（只读） */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Task Details
            </Typography>

            <TextInput source="title" label="Task Title" fullWidth disabled />

            <TextInput
              source="description"
              label="Task Description"
              multiline
              rows={4}
              fullWidth
              disabled
            />

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <strong>Assigned By:</strong>
              </Typography>
              <ReferenceField source="manager" reference="users" link={false}>
                <TextField source="username" />
              </ReferenceField>
            </Box>

            <DateInput source="start_date" label="Start Date" disabled />

            <DateInput source="end_date" label="Due Date" disabled />

            <TextField source="status_display" label="Current Status" />
          </CardContent>
        </Card>

        {/* 提交计划和预算 */}
        {canSubmitPlan && (
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Submit Your Work Plan
              </Typography>

              <TextInput
                source="employee_plan"
                label="Work Plan"
                multiline
                rows={6}
                validate={required()}
                fullWidth
                helperText="Describe your approach, timeline, and deliverables"
              />

              <NumberInput
                source="estimated_budget"
                label="Estimated Budget"
                validate={required()}
                fullWidth
                step={0.01}
                helperText="Enter your estimated budget for this task"
              />

              {record.employee_submitted_at && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="textSecondary">
                    Last submitted:{" "}
                    <DateField
                      source="employee_submitted_at"
                      locales="en-US"
                      showTime
                      record={record}
                    />
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        )}

        {record.status === "completed" && (
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main" gutterBottom>
                ✓ Task Completed
              </Typography>
              <Typography variant="body2" color="textSecondary">
                This task has been marked as completed by your manager.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    );
  };

  return (
    <Edit>
      <SimpleForm onSubmit={handleSubmitPlan}>
        <EmployeeEditContent />
      </SimpleForm>
    </Edit>
  );
};
