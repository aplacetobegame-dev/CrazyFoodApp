import postgres from "postgres";
import type { ReceiptRecord, ReceiptStore } from "./queue/types.ts";

type Sql = ReturnType<typeof postgres>;

export function createPostgresReceiptStore(sql: Sql): ReceiptStore {
  return {
    async record(input: ReceiptRecord): Promise<"inserted" | "duplicate"> {
      const rows = await sql<{ message_id: string }[]>`
        insert into infra.job_receipts (message_id, idempotency_key, job_type)
        values (${input.messageId}::bigint, ${input.idempotencyKey}, ${input.jobType})
        on conflict (message_id) do nothing
        returning message_id
      `;
      return rows.length === 0 ? "duplicate" : "inserted";
    },
  };
}

export class MemoryReceiptStore implements ReceiptStore {
  readonly rows = new Map<string, ReceiptRecord>();

  async record(input: ReceiptRecord): Promise<"inserted" | "duplicate"> {
    if (this.rows.has(input.messageId)) {
      return "duplicate";
    }
    this.rows.set(input.messageId, input);
    return "inserted";
  }
}
