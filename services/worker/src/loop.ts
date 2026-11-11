import { classifyAttempt, handleMessage, settleExhausted, type JobEffects } from "./handler.ts";
import { log } from "./log.ts";
import type { QueueAdapter, ReceiptStore } from "./queue/types.ts";

export async function processBatch(input: {
  queue: QueueAdapter;
  receipts: ReceiptStore;
  maxAttempts: number;
  batchSize: number;
  jobs?: JobEffects;
}): Promise<{ archived: number; retried: number }> {
  const messages = await input.queue.read(input.batchSize);
  let archived = 0;
  let retried = 0;

  for (const message of messages) {
    if (classifyAttempt(message.readCount, input.maxAttempts) === "exhaust") {
      if (input.jobs) {
        try {
          await settleExhausted(message, input.jobs);
        } catch (error) {
          log({
            event: "exhaust_failed",
            messageId: message.id,
            category: error instanceof Error ? error.name : "error",
          });
        }
      }
      await input.queue.archive(message.id);
      log({ event: "job_exhausted", messageId: message.id, attempts: message.readCount });
      archived += 1;
      continue;
    }

    try {
      const result = await handleMessage(message, input.receipts, input.jobs);
      if (result === "ack") {
        await input.queue.archive(message.id);
        archived += 1;
      } else {
        retried += 1;
      }
    } catch (error) {
      retried += 1;
      log({
        event: "job_retry",
        messageId: message.id,
        attempts: message.readCount,
        category: error instanceof Error ? error.name : "error",
      });
    }
  }

  return { archived, retried };
}
