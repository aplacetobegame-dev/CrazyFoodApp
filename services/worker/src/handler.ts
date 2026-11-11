import { isJobMessage, type JobMessage } from "@food-felonies/contracts";
import type { QueueMessage, ReceiptStore } from "./queue/types.ts";

export type ProcessResult = "ack" | "retry";

export class PermanentJobError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PermanentJobError";
  }
}

export type JobEffects = {
  completeGeneration(jobId: string): Promise<void>;
  failGeneration(jobId: string, category: string): Promise<void>;
  reviewPhoto(resultId: string): Promise<void>;
  rejectPhoto(resultId: string): Promise<void>;
  renderClip(clipId: string): Promise<void>;
  failClip(clipId: string): Promise<void>;
};

export function classifyAttempt(readCount: number, maxAttempts: number): "process" | "exhaust" {
  return readCount > maxAttempts ? "exhaust" : "process";
}

export async function settleExhausted(message: QueueMessage, jobs: JobEffects): Promise<void> {
  if (!isJobMessage(message.body)) return;
  if (message.body.type === "generate_recipe") {
    await jobs.failGeneration(message.body.payload.jobId, "exhausted");
  } else if (message.body.type === "moderate_photo") {
    await jobs.rejectPhoto(message.body.payload.resultId);
  } else if (message.body.type === "render_clip") {
    await jobs.failClip(message.body.payload.clipId);
  }
}

async function runJob(message: JobMessage, jobs: JobEffects | undefined): Promise<void> {
  if (message.type === "echo") return;
  if (!jobs) throw new Error("missing job effects");
  if (message.type === "generate_recipe") {
    try {
      await jobs.completeGeneration(message.payload.jobId);
    } catch (error) {
      if (error instanceof PermanentJobError) {
        await jobs.failGeneration(message.payload.jobId, error.message);
        return;
      }
      throw error;
    }
    return;
  }
  if (message.type === "moderate_photo") {
    await jobs.reviewPhoto(message.payload.resultId);
    return;
  }
  await jobs.renderClip(message.payload.clipId);
}

export async function handleMessage(
  message: QueueMessage,
  receipts: ReceiptStore,
  jobs?: JobEffects,
): Promise<ProcessResult> {
  if (!isJobMessage(message.body)) {
    return "ack";
  }

  await runJob(message.body, jobs);
  await receipts.record({
    messageId: message.id,
    idempotencyKey: message.body.idempotencyKey,
    jobType: message.body.type,
    userId: message.body.payload.requestedBy,
  });
  return "ack";
}
