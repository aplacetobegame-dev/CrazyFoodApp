import { isJobMessage } from "@food-felonies/contracts";
import type { QueueMessage, ReceiptStore } from "./queue/types.ts";

export type ProcessResult = "ack" | "retry";

export function classifyAttempt(readCount: number, maxAttempts: number): "process" | "exhaust" {
  return readCount > maxAttempts ? "exhaust" : "process";
}

export async function handleMessage(
  message: QueueMessage,
  receipts: ReceiptStore,
): Promise<ProcessResult> {
  if (!isJobMessage(message.body)) {
    return "ack";
  }

  await receipts.record({
    messageId: message.id,
    idempotencyKey: message.body.idempotencyKey,
    jobType: message.body.type,
  });
  return "ack";
}
