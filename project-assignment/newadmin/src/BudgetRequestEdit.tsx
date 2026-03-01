import {
  Edit,
  SimpleForm,
  TextInput,
  SelectInput,
  required,
  NumberField,
  TextField,
  DateField,
  ReferenceField,
  useRecordContext,
  useNotify,
  useRedirect,
} from "react-admin";

// Budget Request Edit Form for Financial Managers
// API: POST /api/budget-approvals/{id}/decide/
// Payload: { "fm_decision": "批准理由或拒绝理由", "status": "approved" | "rejected" }
// FM can only view budget details and edit fm_decision and status fields
// Status can only be "approved" or "rejected"

const BudgetRequestTitle = () => {
  const record = useRecordContext();
  return <span>Budget Request {record ? `"${record.title}"` : ""}</span>;
};

export const BudgetRequestEdit = () => {
  const notify = useNotify();
  const redirect = useRedirect();

  // Custom save handler for the /decide/ endpoint
  const handleSave = async (data: Record<string, unknown>) => {
    try {
      const apiUrl =
        import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
      const url = `${apiUrl}/budget-approvals/${data.id}/decide/`;

      const response = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken() || "",
        },
        body: JSON.stringify({
          fm_decision: data.fm_decision,
          status: data.status,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update budget request");
      }

      notify("Budget request decision saved successfully", { type: "success" });
      redirect("list", "budget_approvals");
    } catch {
      notify("Error: Failed to save decision", { type: "error" });
    }
  };

  return (
    <Edit title={<BudgetRequestTitle />} mutationMode="pessimistic">
      <SimpleForm onSubmit={handleSave}>
        {/* Read-only fields - Display budget request details */}
        <TextInput source="title" label="Title" disabled fullWidth />

        <TextInput
          source="description"
          label="Description"
          multiline
          rows={3}
          disabled
          fullWidth
        />

        <ReferenceField
          source="related_event"
          reference="event_requests"
          label="Related Event"
          link={false}
        >
          <TextField source="client_name" />
        </ReferenceField>

        <NumberField
          source="requested_amount"
          label="Requested Amount"
          options={{ style: "currency", currency: "SEK" }}
        />

        <ReferenceField
          source="requester"
          reference="users"
          label="Requester"
          link={false}
        >
          <TextField source="username" />
        </ReferenceField>

        <DateField
          source="created_at"
          label="Created At"
          locales="en-US"
          showTime
        />

        {/* Editable fields - FM Decision */}
        <SelectInput
          source="status"
          label="Decision Status"
          choices={[
            { id: "approved", name: "Approved" },
            { id: "rejected", name: "Rejected" },
          ]}
          validate={required()}
          fullWidth
        />

        <TextInput
          source="fm_decision"
          label="FM Decision / Reason"
          multiline
          rows={4}
          validate={required()}
          fullWidth
          helperText="Please provide the reason for approval or rejection"
        />
      </SimpleForm>
    </Edit>
  );
};

// Helper function to get CSRF token
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
