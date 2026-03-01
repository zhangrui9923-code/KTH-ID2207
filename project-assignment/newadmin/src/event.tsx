import {
  Create,
  SimpleForm,
  TextInput,
  DateInput,
  NumberInput,
  SelectInput,
  ReferenceField,
  TextField,
  required,
  BooleanInput,
  minValue,
  DataTable,
  List,
  DateField,
  Edit,
  usePermissions,
  useRecordContext,
} from "react-admin";

// Example API Payload:
// "record_number": "string",
//  "client_name": "string",
//  "event_type": "string",
//  "from_date": "2025-10-29",
//  "to_date": "2025-10-29",
//  "expected_number": 9223372036854776000,
//  "has_decorations": true,
//  "has_meals": true,
//  "has_parties": true,
//  "has_drinks": true,
//  "has_filming": true,
//  "expected_budget": "-"

export const EventRequestCreate = () => {
  return (
    <Create redirect="list">
      <SimpleForm>
        <TextInput
          source="record_number"
          label="Record Number"
          validate={required()}
        />
        <TextInput
          source="client_name"
          label="Client Name"
          validate={required()}
        />
        <SelectInput
          source="event_type"
          label="Event Type"
          choices={[
            { id: "wedding", name: "Wedding" },
            { id: "conference", name: "Conference" },
            { id: "party", name: "Party" },
            { id: "other", name: "Other" },
          ]}
          validate={required()}
        />
        <DateInput source="from_date" label="From Date" validate={required()} />
        <DateInput source="to_date" label="To Date" validate={required()} />
        <NumberInput
          source="expected_number"
          label="Expected Attendees"
          min={0}
        />
        {/* boolean 勾选框 */}
        <BooleanInput source="has_decorations" label="Has Decorations?" />
        <BooleanInput source="has_meals" label="Has Meals?" />
        <BooleanInput source="has_parties" label="Has Parties?" />
        <BooleanInput source="has_drinks" label="Has Drinks?" />
        <BooleanInput source="has_filming" label="Has Filming?" />
        <TextInput
          source="venue_preference"
          label="Venue Preference"
          multiline
          rows={3}
        />
        {/* restrict budget with numerical input, preferably 2 decimal and bigger than 0*/}
        <NumberInput
          source="expected_budget"
          label="Expected Budget"
          step={0.01}
          parse={(value) => (value ? parseFloat(value) : 0)}
          validate={[required(), minValue(0)]}
        />
      </SimpleForm>
    </Create>
  );
};

// Event request list
export const EventRequestList = () => (
  <List>
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="created_by" label="Created By">
        <ReferenceField source="created_by" reference="users" link={false}>
          <TextField source="username" />
        </ReferenceField>
      </DataTable.Col>
      <DataTable.Col source="status_display" />
      <DataTable.Col source="title" />
      {/* <DataTable.Col source="description" /> */}
      <DataTable.Col source="record_number" />
      <DataTable.Col source="client_name" />
      <DataTable.Col source="event_type" />
      {/* <DataTable.NumberCol source="expected_number" />
      <DataTable.Col source="expected_budget" />
      <DataTable.Col source="from_date">
        <DateField source="from_date" />
      </DataTable.Col>
      <DataTable.Col source="to_date">
        <DateField source="to_date" />
      </DataTable.Col>
      <DataTable.Col source="has_decorations">
        <BooleanField source="has_decorations" />
      </DataTable.Col>
      <DataTable.Col source="has_meals">
        <BooleanField source="has_meals" />
      </DataTable.Col>
      <DataTable.Col source="has_parties">
        <BooleanField source="has_parties" />
      </DataTable.Col>
      <DataTable.Col source="has_drinks">
        <BooleanField source="has_drinks" />
      </DataTable.Col>
      <DataTable.Col source="has_filming">
        <BooleanField source="has_filming" />
      </DataTable.Col>
      <DataTable.Col source="description_of_decorations" />
      <DataTable.Col source="description_of_meals" />
      <DataTable.Col source="description_of_music" />
      <DataTable.Col source="description_of_poster" />
      <DataTable.Col source="description_of_filming" />
      <DataTable.Col source="description_of_drinks" />
      <DataTable.Col source="other_needs" />
      <DataTable.Col source="status" />
      <DataTable.Col source="scs_comment" />
      <DataTable.Col source="scs_handled_at">
        <DateField source="scs_handled_at" />
      </DataTable.Col>
      <DataTable.Col source="fm_feedback" />
      <DataTable.Col source="fm_handled_at">
        <DateField source="fm_handled_at" />
      </DataTable.Col>
      <DataTable.Col source="admin_decision" />
      <DataTable.Col source="admin_handled_at">
        <DateField source="admin_handled_at" />
      </DataTable.Col>
      <DataTable.Col source="created_at">
        <DateField source="created_at" />
      </DataTable.Col>
      <DataTable.Col source="updated_at">
        <DateField source="updated_at" />
      </DataTable.Col>
      <DataTable.NumberCol source="created_by" />
      <DataTable.Col source="current_handler" />
      <DataTable.NumberCol source="scs_handler" />
      <DataTable.NumberCol source="fm_handler" />
      <DataTable.NumberCol source="admin_handler" />
      <DataTable.Col source="scs_handler_name" />
      <DataTable.Col source="fm_handler_name" />
      <DataTable.Col source="admin_handler_name" /> */}
    </DataTable>
  </List>
);

// Event Request pending list - 获取当前用户需要处理的请求
export const EventRequestPendingList = () => (
  <List filter={{ pending: true }} title="Pending Event Requests">
    <DataTable>
      <DataTable.Col source="id" />
      <DataTable.Col source="created_by" label="Created By">
        <ReferenceField source="created_by" reference="users" link={false}>
          <TextField source="username" />
        </ReferenceField>
      </DataTable.Col>
      <DataTable.Col source="status_display" label="Status" />
      <DataTable.Col source="title" />
      <DataTable.Col source="record_number" label="Record #" />
      <DataTable.Col source="client_name" label="Client" />
      <DataTable.Col source="event_type" label="Event Type" />
      <DataTable.Col source="from_date" label="From">
        <DateField source="from_date" locales="en-US" />
      </DataTable.Col>
      <DataTable.Col source="to_date" label="To">
        <DateField source="to_date" locales="en-US" />
      </DataTable.Col>
    </DataTable>
  </List>
);

export const EventSCSEdit = () => {
  return (
    <Edit>
      <SimpleForm>
        {/* <SelectInput
          source="status"
          label="Status"
          choices={[
            { id: "approved_by_scs", name: "Approved" },
            { id: "rejected_by_scs", name: "Rejected" },
          ]}
          validate={required()}
        /> */}
        <TextInput
          source="scs_comment"
          label="SCS Comment"
          multiline
          rows={4}
        />
      </SimpleForm>
    </Edit>
  );
};

export const EventFMEdit = () => {
  return (
    <Edit>
      <SimpleForm>
        <TextInput
          source="fm_feedback"
          label="FM Feedback"
          multiline
          rows={4}
        />
      </SimpleForm>
    </Edit>
  );
};

export const EventAdminEdit = () => {
  return (
    <Edit>
      <SimpleForm>
        <SelectInput
          source="status"
          label="Status"
          choices={[
            { id: "approved_by_admin", name: "Approve" },
            { id: "rejected_by_admin", name: "Reject" },
          ]}
          validate={required()}
        />
        <TextInput
          source="admin_decision"
          label="Admin Decision"
          multiline
          rows={4}
        />
      </SimpleForm>
    </Edit>
  );
};

export const EventSCSAddDetails = () => {
  return (
    <Edit>
      <SimpleForm>
        <TextInput
          source="description_of_decorations"
          label="Description of Decorations"
          multiline
          rows={3}
        />
        <TextInput
          source="description_of_meals"
          label="Description of Meals"
          multiline
          rows={3}
        />
        <TextInput
          source="description_of_music"
          label="Description of Music"
          multiline
          rows={3}
        />
        <TextInput
          source="description_of_poster"
          label="Description of Poster"
          multiline
          rows={3}
        />
        <TextInput
          source="description_of_filming"
          label="Description of Filming"
          multiline
          rows={3}
        />
        <TextInput
          source="description_of_drinks"
          label="Description of Drinks"
          multiline
          rows={3}
        />
        <TextInput
          source="other_needs"
          label="Other Needs"
          multiline
          rows={3}
        />
      </SimpleForm>
    </Edit>
  );
};

// 智能编辑组件 - 根据用户角色和记录状态显示不同的表单
export const EventRequestPendingEdit = () => {
  const { permissions } = usePermissions();
  const EventFormContent = () => {
    const record = useRecordContext();

    if (!record) return null;

    // 根据角色和状态决定显示哪些字段
    const showSCSForm =
      permissions === "scs" &&
      (record.status === "submitted" || record.status === "approved");
    const showFMForm = permissions === "fm" && record.status === "scs_reviewed";
    const showAdminForm =
      permissions === "admin" && record.status === "fm_reviewed";

    return (
      <>
        {/* 显示基本信息（只读） */}
        <TextInput source="record_number" label="Record Number" disabled />
        <TextInput source="client_name" label="Client Name" disabled />
        <TextInput source="event_type" label="Event Type" disabled />
        <DateInput source="from_date" label="From Date" disabled />
        <DateInput source="to_date" label="To Date" disabled />
        <NumberInput
          source="expected_number"
          label="Expected Attendees"
          disabled
        />
        <NumberInput
          source="expected_budget"
          label="Expected Budget"
          disabled
        />
        <BooleanInput
          source="has_decorations"
          label="Has Decorations?"
          disabled
        />
        <BooleanInput source="has_meals" label="Has Meals?" disabled />
        <BooleanInput source="has_parties" label="Has Parties?" disabled />
        <BooleanInput source="has_drinks" label="Has Drinks?" disabled />
        <BooleanInput source="has_filming" label="Has Filming?" disabled />

        {/* 显示已有的评论/反馈（只读） */}
        {record.scs_comment && (
          <TextInput
            source="scs_comment"
            label="SCS Comment (Read Only)"
            multiline
            rows={4}
            disabled
          />
        )}
        {record.fm_feedback && (
          <TextInput
            source="fm_feedback"
            label="FM Feedback (Read Only)"
            multiline
            rows={4}
            disabled
          />
        )}
        {record.admin_decision && (
          <TextInput
            source="admin_decision"
            label="Admin Decision (Read Only)"
            multiline
            rows={4}
            disabled
          />
        )}

        {/* SCS 处理表单 */}
        {showSCSForm && record.status === "submitted" && (
          <>
            <hr style={{ margin: "20px 0", border: "1px solid #e0e0e0" }} />
            <h3 style={{ marginBottom: "10px" }}>SCS Review</h3>
            <TextInput
              source="scs_comment"
              label="SCS Comment"
              multiline
              rows={4}
            />
          </>
        )}

        {/* SCS 添加详细信息表单 */}
        {showSCSForm && record.status === "approved" && (
          <>
            <hr style={{ margin: "20px 0", border: "1px solid #e0e0e0" }} />
            <h3 style={{ marginBottom: "10px" }}>Add Event Details</h3>
            <TextInput
              source="description_of_decorations"
              label="Description of Decorations"
              multiline
              rows={3}
            />
            <TextInput
              source="description_of_meals"
              label="Description of Meals"
              multiline
              rows={3}
            />
            <TextInput
              source="description_of_music"
              label="Description of Music"
              multiline
              rows={3}
            />
            <TextInput
              source="description_of_poster"
              label="Description of Poster"
              multiline
              rows={3}
            />
            <TextInput
              source="description_of_filming"
              label="Description of Filming"
              multiline
              rows={3}
            />
            <TextInput
              source="description_of_drinks"
              label="Description of Drinks"
              multiline
              rows={3}
            />
            <TextInput
              source="other_needs"
              label="Other Needs"
              multiline
              rows={3}
            />
          </>
        )}

        {/* FM 处理表单 */}
        {showFMForm && (
          <>
            <hr style={{ margin: "20px 0", border: "1px solid #e0e0e0" }} />
            <h3 style={{ marginBottom: "10px" }}>FM Review</h3>
            <TextInput
              source="fm_feedback"
              label="FM Feedback"
              multiline
              rows={4}
            />
          </>
        )}

        {/* Admin 处理表单 */}
        {showAdminForm && (
          <>
            <hr style={{ margin: "20px 0", border: "1px solid #e0e0e0" }} />
            <h3 style={{ marginBottom: "10px" }}>Admin Decision</h3>
            <SelectInput
              source="status"
              label="Status"
              choices={[
                { id: "approved", name: "Approve" },
                { id: "rejected", name: "Reject" },
              ]}
              validate={required()}
            />
            <TextInput
              source="admin_decision"
              label="Admin Decision"
              multiline
              rows={4}
            />
          </>
        )}
      </>
    );
  };

  return (
    <Edit>
      <SimpleForm>
        <EventFormContent />
      </SimpleForm>
    </Edit>
  );
};
