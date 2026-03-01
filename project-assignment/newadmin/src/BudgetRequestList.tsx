import {
  List,
  Datagrid,
  TextField,
  ReferenceField,
  DateField,
  NumberField,
  FunctionField,
} from "react-admin";
import { Chip } from "@mui/material";

interface BudgetRecord {
  [key: string]: string;
}

const StatusField = ({ source }: { source: string }) => (
  <FunctionField
    source={source}
    render={(record: BudgetRecord) => {
      const status = record[source];
      let color: "warning" | "success" | "error" | "default" = "default";

      if (status === "submitted") {
        color = "warning"; // 黄色
      } else if (status === "approved") {
        color = "success"; // 绿色
      } else if (status === "rejected") {
        color = "error"; // 红色
      }

      return <Chip label={status} color={color} size="small" />;
    }}
  />
);

export const BudgetRequestList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" label="ID" />
      <TextField source="title" label="Title" />
      <ReferenceField
        source="requester"
        reference="users"
        label="Requester"
        link={false}
      >
        <TextField source="username" />
      </ReferenceField>
      <TextField source="related_event_title" label="Related Event" />
      <NumberField
        source="requested_amount"
        label="Requested Amount"
        options={{ style: "currency", currency: "SEK" }}
      />
      <StatusField source="status" />
      <DateField
        source="created_at"
        label="Created At"
        locales="en-US"
        showTime
      />
    </Datagrid>
  </List>
);
