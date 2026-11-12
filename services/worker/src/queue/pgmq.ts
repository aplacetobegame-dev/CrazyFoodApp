import postgres from "postgres";
import type { QueueAdapter, QueueMessage } from "./types.ts";

const QUEUE_NAME = "jobs";

type Sql = ReturnType<typeof postgres>;

type PgmqRow = {
  msg_id: string | number;
  read_ct: number;
  message: unknown;
};

export function createPgmqAdapter(sql: Sql, visibilityTimeoutSeconds: number): QueueAdapter {
  return {
    async read(batchSize: number): Promise<QueueMessage[]> {
      const rows = await sql<PgmqRow[]>`
        select msg_id, read_ct, message
        from pgmq.read(${QUEUE_NAME}, ${visibilityTimeoutSeconds}, ${batchSize})
      `;
      return rows.map((row) => ({
        id: String(row.msg_id),
        readCount: row.read_ct,
        body: row.message,
      }));
    },

    async archive(id: string): Promise<void> {
      await sql`select pgmq.archive(${QUEUE_NAME}, ${id}::bigint)`;
    },

    async delete(id: string): Promise<void> {
      await sql`select pgmq.delete(${QUEUE_NAME}, ${id}::bigint)`;
    },
  };
}
