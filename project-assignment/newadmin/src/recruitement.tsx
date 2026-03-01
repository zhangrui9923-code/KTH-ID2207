import {
  Create,
  SimpleForm,
  TextInput,
  NumberInput,
  required,
  DataTable,
  List,
  Edit,
  usePermissions,
  useRecordContext,
  TextField,
  ReferenceField,
  DateField,
  NumberField,
  minValue,
  FunctionField,
  Button,
  useRefresh,
  useNotify,
  useDataProvider,
  SelectInput,
} from "react-admin";
import { useState } from "react";

// Recruitment Create - PM/SM 创建招聘申请
// 创建后自动提交给 HR
export const RecruitmentCreate = () => {
  const notify = useNotify();
  const dataProvider = useDataProvider();

  return (
    <Create
      redirect="list"
      mutationOptions={{
        onSuccess: async (data) => {
          try {
            // 创建成功后自动提交给 HR
            await dataProvider.update("recruitments", {
              id: data.id,
              data: { action: "submit" },
              previousData: data,
            });
            notify("Recruitment created and submitted to HR successfully", {
              type: "success",
            });
          } catch (error: any) {
            notify("Recruitment created but failed to submit to HR", {
              type: "warning",
            });
          }
        },
      }}
    >
      <SimpleForm>
        <TextInput
          source="position_title"
          label="Position Title"
          validate={required()}
          fullWidth
        />
        <TextInput
          source="description"
          label="Job Description & Requirements"
          multiline
          rows={5}
          validate={required()}
          fullWidth
        />
        <SelectInput
          source="department"
          label="Department"
          choices={[
            { id: "Service", name: "Service" },
            { id: "Production", name: "Production" },
          ]}
          validate={required()}
        />
        <NumberInput
          source="number_of_positions"
          label="Number of Positions"
          min={1}
          validate={[required(), minValue(1)]}
        />
      </SimpleForm>
    </Create>
  );
};

// Recruitment List - 显示所有招聘申请
export const RecruitmentList = () => {
  return (
    <List>
      <DataTable>
        <DataTable.Col source="id" label="ID" />
        <DataTable.Col source="position_title" label="Position" />
        <DataTable.Col source="department" label="Department" />
        <DataTable.Col source="requester" label="Requester">
          <ReferenceField source="requester" reference="users" link={false}>
            <TextField source="username" />
          </ReferenceField>
        </DataTable.Col>
        <DataTable.Col source="status" label="Status">
          <FunctionField
            render={(record: any) => (
              <span
                style={{
                  padding: "4px 8px",
                  borderRadius: "4px",
                  backgroundColor:
                    record.status === "completed"
                      ? "#4caf50"
                      : record.status === "rejected"
                        ? "#f44336"
                        : record.status === "in_progress"
                          ? "#2196f3"
                          : record.status === "submitted"
                            ? "#ff9800"
                            : "#9e9e9e",
                  color: "white",
                  fontSize: "12px",
                }}
              >
                {record.status}
              </span>
            )}
          />
        </DataTable.Col>
        <DataTable.NumberCol source="number_of_positions" label="Positions" />
        <DataTable.NumberCol source="positions_filled" label="Filled" />
        <DataTable.Col source="hr_handler" label="HR Handler">
          <ReferenceField source="hr_handler" reference="users" link={false}>
            <TextField source="username" />
          </ReferenceField>
        </DataTable.Col>
        <DataTable.Col source="created_at" label="Created">
          <DateField source="created_at" locales="en-US" showTime />
        </DataTable.Col>
      </DataTable>
    </List>
  );
};

// PM/SM Edit - 编辑和提交申请
export const RecruitmentPMEdit = () => {
  const ActionButtons = () => {
    const record = useRecordContext();
    const refresh = useRefresh();
    const notify = useNotify();
    const dataProvider = useDataProvider();

    if (!record) return null;

    const handleSubmit = async () => {
      try {
        await dataProvider.update("recruitments", {
          id: record.id,
          data: { action: "submit" },
          previousData: record,
        });
        notify("Recruitment submitted to HR", { type: "success" });
        refresh();
      } catch (error: any) {
        notify(error.message || "Failed to submit", { type: "error" });
      }
    };

    if (record.status === "pending") {
      return (
        <div style={{ marginTop: "20px" }}>
          <Button label="Submit to HR" onClick={handleSubmit} />
        </div>
      );
    }
    return null;
  };

  return (
    <Edit>
      <SimpleForm>
        <TextField source="status" label="Status" />
        <TextInput
          source="position_title"
          label="Position Title"
          validate={required()}
          fullWidth
        />
        <TextInput
          source="description"
          label="Job Description & Requirements"
          multiline
          rows={5}
          validate={required()}
          fullWidth
        />
        <SelectInput
          source="department"
          label="Department"
          choices={[
            { id: "Service", name: "Service" },
            { id: "Production", name: "Production" },
          ]}
          validate={required()}
        />
        <NumberInput
          source="number_of_positions"
          label="Number of Positions"
          min={1}
          validate={[required(), minValue(1)]}
        />
        <ActionButtons />
      </SimpleForm>
    </Edit>
  );
};

// HR Edit - HR 处理招聘申请
export const RecruitmentHREdit = () => {
  const [hiresCount, setHiresCount] = useState(1);
  const [originalStatus, setOriginalStatus] = useState<string>("");
  const notify = useNotify();
  const refresh = useRefresh();
  const dataProvider = useDataProvider();

  const ActionButtons = () => {
    const record = useRecordContext();

    if (!record) return null;

    const handleAddHires = async () => {
      try {
        await dataProvider.update("recruitments", {
          id: record.id,
          data: { action: "add_hires", count: hiresCount },
          previousData: record,
        });
        notify(`Added ${hiresCount} hire(s)`, { type: "success" });
        refresh();
      } catch (error: any) {
        notify(error.message || "Failed to add hires", { type: "error" });
      }
    };

    return (
      <div
        style={{
          marginTop: "20px",
          display: "flex",
          gap: "10px",
          flexWrap: "wrap",
        }}
      >
        {record.status === "in_progress" && (
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <input
              type="number"
              min="1"
              value={hiresCount}
              onChange={(e) => setHiresCount(parseInt(e.target.value) || 1)}
              style={{
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                width: "80px",
              }}
            />
            <Button label="Add Hires" onClick={handleAddHires} />
          </div>
        )}
      </div>
    );
  };

  const getStatusChoices = (currentStatus: string) => {
    // 根据当前状态返回可选的状态
    if (currentStatus === "submitted") {
      return [
        { id: "submitted", name: "Submitted" },
        { id: "in_progress", name: "In Progress (Accept)" },
        { id: "rejected", name: "Rejected" },
      ];
    } else if (currentStatus === "in_progress") {
      return [
        { id: "in_progress", name: "In Progress" },
        { id: "completed", name: "Completed" },
        { id: "rejected", name: "Rejected" },
      ];
    } else {
      // pending, completed, rejected 状态不允许修改
      return [{ id: currentStatus, name: currentStatus }];
    }
  };

  const StatusInput = () => {
    const record = useRecordContext();
    if (!record) return null;

    return (
      <SelectInput
        source="status"
        label="Status"
        choices={getStatusChoices(record.status)}
        validate={required()}
      />
    );
  };

  // 捕获初始状态
  const CaptureOriginalStatus = () => {
    const record = useRecordContext();
    if (record && !originalStatus) {
      setOriginalStatus(record.status);
    }
    return null;
  };

  // 自定义保存处理器
  const handleSave = async (data: any) => {
    const record = data;

    try {
      // 检测状态是否改变
      const statusChanged = data.status !== originalStatus;

      if (!statusChanged) {
        // 状态没有改变，不做任何操作
        notify("No changes made", { type: "info" });
        return record;
      }

      // 状态改变了，调用对应的 action
      let action = "";
      let payload: any = {};

      if (data.status === "in_progress" && originalStatus === "submitted") {
        action = "accept";
      } else if (
        data.status === "completed" &&
        originalStatus === "in_progress"
      ) {
        action = "complete";
      } else if (data.status === "rejected") {
        action = "reject";
        payload = { reason: data.hr_notes || "No reason provided" };
      }

      if (action) {
        await dataProvider.update("recruitments", {
          id: record.id,
          data: { action, ...payload },
          previousData: record,
        });
        notify(`Status updated to ${data.status}`, { type: "success" });
        refresh();
        return record;
      }

      notify("Invalid status change", { type: "error" });
      return record;
    } catch (error: any) {
      notify(error.message || "Failed to update status", { type: "error" });
      throw error;
    }
  };

  return (
    <Edit mutationMode="pessimistic">
      <SimpleForm onSubmit={handleSave} sanitizeEmptyValues={false}>
        <CaptureOriginalStatus />
        {/* Read-only basic info */}
        <TextField source="position_title" label="Position Title" />
        <TextField source="description" label="Description" />
        <TextField source="department" label="Department" />
        <ReferenceField source="requester" reference="users" link={false}>
          <TextField source="username" />
        </ReferenceField>
        <NumberField source="number_of_positions" label="Positions Needed" />

        {/* Progress info */}
        <NumberField
          source="candidates_interviewed"
          label="Candidates Interviewed"
        />
        <NumberField source="positions_filled" label="Positions Filled" />

        {/* Status - HR can change */}
        <StatusInput />

        <ActionButtons />
      </SimpleForm>
    </Edit>
  );
};

// Smart Edit Component - 根据角色选择编辑页面
export const RecruitmentEdit = () => {
  const { permissions } = usePermissions();

  // HR 使用 HR 编辑页面
  if (permissions === "hrm" || permissions === "admin") {
    return <RecruitmentHREdit />;
  }

  // PM/SM 使用 PM 编辑页面
  return <RecruitmentPMEdit />;
};
