import {
  Create,
  SimpleForm,
  TextInput,
  NumberInput,
  SelectInput,
  ReferenceInput,
  required,
  minValue,
} from "react-admin";

// Budget Request Create Form
// Only accessible to users with SM (Service Manager) or PM (Product Manager) roles
// API Payload Fields:
//   "title": "string",
//   "description": "string",
//   "related_event": 0,
//   "requested_amount": "decimal",
//   "status": "submitted",
//   "fm_decision": "string"

export const BudgetRequestCreate = () => {
  return (
    <Create redirect="list">
      <SimpleForm>
        <TextInput
          source="title"
          label="Budget Request Title"
          validate={required()}
          fullWidth
        />

        <TextInput
          source="description"
          label="Description"
          multiline
          rows={4}
          validate={required()}
          fullWidth
        />
        <ReferenceInput
          source="related_event"
          reference="event_requests"
          label="Related Event"
        >
          <SelectInput optionText="client_name" />
        </ReferenceInput>

        <NumberInput
          source="requested_amount"
          label="Requested Amount"
          step={0.01}
          parse={(value) => (value ? parseFloat(value) : 0)}
          validate={[required(), minValue(0.01)]}
        />
      </SimpleForm>
    </Create>
  );
};
