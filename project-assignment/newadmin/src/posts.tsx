import {
  List,
  DataTable,
  ReferenceField,
  EditButton,
  SimpleForm,
  ReferenceInput,
  TextInput,
  Edit,
  Create,
} from "react-admin";

const postFilters = [
  <TextInput key="q" source="q" label="Search" alwaysOn />,
  <ReferenceInput
    key="userId"
    source="userId"
    label="User"
    reference="users"
  />,
];

export const PostList = () => (
  <List filters={postFilters}>
    <DataTable rowClick="false">
      <DataTable.Col source="userId">
        <ReferenceField source="userId" reference="users" link="show" />
      </DataTable.Col>
      <DataTable.Col source="title" />
      <DataTable.Col>
        <EditButton />
      </DataTable.Col>
    </DataTable>
  </List>
);

export const PostEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="id" InputProps={{ disabled: true }} />
      <ReferenceInput source="userId" reference="users" />
      <TextInput source="title" />
      <TextInput source="body" multiline rows={5} />
    </SimpleForm>
  </Edit>
);

export const PostCreate = () => (
  <Create>
    <SimpleForm>
      <ReferenceInput source="userId" reference="users" />
      <TextInput source="title" />
      <TextInput source="body" multiline rows={5} />
    </SimpleForm>
  </Create>
);
