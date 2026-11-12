import postgres from "postgres";
import type { ReceiptRecord, ReceiptStore } from "./queue/types.ts";

type Sql = ReturnType<typeof postgres>;

export function createPostgresReceiptStore(sql: Sql): ReceiptStore {
  return {
    async record(input: ReceiptRecord): Promise<"inserted" | "duplicate"> {
      try {
        const rows = await sql<{ message_id: string }[]>`
          insert into infra.job_receipts (message_id, idempotency_key, job_type, user_id)
          values (${input.messageId}::bigint, ${input.idempotencyKey}, ${input.jobType}, ${input.userId}::uuid)
          on conflict (message_id) do nothing
          returning message_id
        `;
        return rows.length === 0 ? "duplicate" : "inserted";
      } catch (error) {
        if (typeof error === "object" && error !== null && "code" in error && error.code === "23505") {
          return "duplicate";
        }
        throw error;
      }
    },
  };
}

export class MemoryReceiptStore implements ReceiptStore {
  readonly rows = new Map<string, ReceiptRecord>();

  async record(input: ReceiptRecord): Promise<"inserted" | "duplicate"> {
    if (this.rows.has(input.messageId)) {
      return "duplicate";
    }
    for (const row of this.rows.values()) {
      if (row.userId === input.userId && row.idempotencyKey === input.idempotencyKey) {
        return "duplicate";
      }
    }
    this.rows.set(input.messageId, input);
    return "inserted";
  }
}
