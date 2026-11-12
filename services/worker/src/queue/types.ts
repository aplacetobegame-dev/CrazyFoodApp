export type QueueMessage = {
  id: string;
  readCount: number;
  body: unknown;
};

export interface QueueAdapter {
  read(batchSize: number): Promise<QueueMessage[]>;
  archive(id: string): Promise<void>;
  delete(id: string): Promise<void>;
}

export type ReceiptRecord = {
  messageId: string;
  idempotencyKey: string;
  jobType: string;
  userId: string;
};

export interface ReceiptStore {
  record(input: ReceiptRecord): Promise<"inserted" | "duplicate">;
}
