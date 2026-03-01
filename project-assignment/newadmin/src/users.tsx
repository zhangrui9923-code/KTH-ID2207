import {
  BooleanField,
  DataTable,
  EmailField,
  List,
  Edit,
  SimpleForm,
  TextInput,
  BooleanInput,
  SelectInput,
  Create,
  usePermissions,
} from "react-admin";

// 用户列表 - 只有 admin 和 hr 可以查看
export const UserList = () => {
  const { permissions } = usePermissions();

  // 如果是 employee，不显示用户列表
  if (permissions === "employee") {
    return <div>您没有权限访问此页面</div>;
  }

  return (
    <List>
      <DataTable>
        <DataTable.Col source="id" />
        <DataTable.Col source="username" />
        <DataTable.Col source="email">
          <EmailField source="email" />
        </DataTable.Col>
        <DataTable.Col source="role" />
        <DataTable.Col source="department" />
        <DataTable.Col source="is_active">
          <BooleanField source="is_active" />
        </DataTable.Col>
      </DataTable>
    </List>
  );
};

// 用户编辑 - 只有 hr 可以编辑
export const UserEdit = () => {
  const { permissions } = usePermissions();

  // 只有 hr 可以编辑用户
  if (permissions !== "hrm" && permissions !== "admin") {
    return <div>Only HR and Admin can edit user information</div>;
  }

  return (
    <Edit>
      <SimpleForm>
        <TextInput source="username" disabled />
        <TextInput source="email" type="email" />
        <TextInput source="first_name" />
        <TextInput source="last_name" />
        <SelectInput
          source="role"
          choices={[
            { id: "admin", name: "Admin" },
            { id: "hr", name: "HR" },
            { id: "employee", name: "Employee" },
          ]}
        />
        <TextInput source="department" />
        <TextInput source="phone" />
        <BooleanInput source="is_active" />
      </SimpleForm>
    </Edit>
  );
};

// 用户创建 - 只有 hr 和 admin 可以创建
export const UserCreate = () => {
  const { permissions } = usePermissions();

  if (permissions !== "hrm" && permissions !== "admin") {
    return <div>Only HR and Admin can create users</div>;
  }

  return (
    <Create>
      <SimpleForm>
        <TextInput source="username" required />
        <TextInput source="email" type="email" />
        <TextInput source="password" type="password" required />
        <TextInput source="first_name" />
        <TextInput source="last_name" />
        <SelectInput
          source="role"
          choices={[
            { id: "admin", name: "Admin" },
            { id: "hrm", name: "HR" },
            { id: "employee", name: "Employee" },
          ]}
          defaultValue="employee"
        />
        <TextInput source="department" />
        <TextInput source="phone" />
        <BooleanInput source="is_active" defaultValue={true} />
      </SimpleForm>
    </Create>
  );
};
