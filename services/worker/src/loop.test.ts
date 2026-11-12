import assert from "node:assert/strict";
import test from "node:test";
import { PermanentJobError, type JobEffects } from "./handler.ts";
import { MemoryReceiptStore } from "./receipts.ts";
import { processBatch } from "./loop.ts";
import type { QueueAdapter, QueueMessage } from "./queue/types.ts";

function jobs(overrides: Partial<JobEffects> = {}): JobEffects {
  return {
    async completeGeneration() { return undefined; },
    async failGeneration() { return undefined; },
    async reviewPhoto() { return undefined; },
    async rejectPhoto() { return undefined; },
    async renderClip() { return undefined; },
    async failClip() { return undefined; },
    ...overrides,
  };
}

const echoBody = {
  type: "echo",
  idempotencyKey: "idem-key-1",
  payload: {
    idempotencyKey: "idem-key-1",
    requestedBy: "user-1",
  },
};

class MemoryQueue implements QueueAdapter {
  archived: string[] = [];
  deleted: string[] = [];
  private pending: QueueMessage[];

  constructor(pending: QueueMessage[]) {
    this.pending = pending;
  }

  async read(batchSize: number): Promise<QueueMessage[]> {
    return this.pending.splice(0, batchSize);
  }

  async archive(id: string): Promise<void> {
    this.archived.push(id);
  }

  async delete(id: string): Promise<void> {
    this.deleted.push(id);
  }
}

test("an echo job writes one receipt and is archived", async () => {
  const receipts = new MemoryReceiptStore();
  const queue = new MemoryQueue([{ id: "7", readCount: 1, body: echoBody }]);

  const result = await processBatch({ queue, receipts, maxAttempts: 5, batchSize: 1 });

  assert.deepEqual(result, { archived: 1, retried: 0 });
  assert.equal(receipts.rows.size, 1);
  assert.deepEqual(queue.archived, ["7"]);
});

test("redelivery of the same message does not write a second receipt", async () => {
  const receipts = new MemoryReceiptStore();
  const first = new MemoryQueue([{ id: "7", readCount: 1, body: echoBody }]);
  await processBatch({ queue: first, receipts, maxAttempts: 5, batchSize: 1 });

  const second = new MemoryQueue([{ id: "7", readCount: 2, body: echoBody }]);
  const result = await processBatch({ queue: second, receipts, maxAttempts: 5, batchSize: 1 });

  assert.deepEqual(result, { archived: 1, retried: 0 });
  assert.equal(receipts.rows.size, 1);
  assert.deepEqual(second.archived, ["7"]);
});

test("an exhausted message is archived without a receipt", async () => {
  const receipts = new MemoryReceiptStore();
  const queue = new MemoryQueue([{ id: "9", readCount: 6, body: echoBody }]);

  await processBatch({ queue, receipts, maxAttempts: 5, batchSize: 1 });

  assert.equal(receipts.rows.size, 0);
  assert.deepEqual(queue.archived, ["9"]);
});

test("an invalid message is archived and a thrown handler is left for retry", async () => {
  const receipts = new MemoryReceiptStore();
  const invalid = new MemoryQueue([{ id: "3", readCount: 1, body: { type: "other" } }]);
  await processBatch({ queue: invalid, receipts, maxAttempts: 5, batchSize: 1 });
  assert.equal(receipts.rows.size, 0);
  assert.deepEqual(invalid.archived, ["3"]);

  const failing: QueueAdapter = {
    async read() {
      return [{ id: "4", readCount: 1, body: echoBody }];
    },
    async archive() {
      throw new Error("archive should not run");
    },
    async delete() {
      return undefined;
    },
  };
  const failingReceipts: MemoryReceiptStore = new MemoryReceiptStore();
  failingReceipts.record = async () => {
    throw new Error("store down");
  };

  const result = await processBatch({
    queue: failing,
    receipts: failingReceipts,
    maxAttempts: 5,
    batchSize: 1,
  });
  assert.deepEqual(result, { archived: 0, retried: 1 });
});

test("a permanent generation failure is refunded once and acknowledged", async () => {
  const receipts = new MemoryReceiptStore();
  const queue = new MemoryQueue([{
    id: "11",
    readCount: 1,
    body: {
      type: "generate_recipe",
      idempotencyKey: "idem-key-1",
      payload: { idempotencyKey: "idem-key-1", requestedBy: "11111111-1111-4111-8111-111111111111", jobId: "job-1" },
    },
  }]);
  const failed: string[] = [];
  const result = await processBatch({
    queue,
    receipts,
    maxAttempts: 5,
    batchSize: 1,
    jobs: jobs({
      async completeGeneration() {
        throw new PermanentJobError("invalid_request");
      },
      async failGeneration(jobId) {
        failed.push(jobId);
      },
    }),
  });
  assert.deepEqual(result, { archived: 1, retried: 0 });
  assert.deepEqual(failed, ["job-1"]);
});

test("an exhausted generation asks for one refund before it is archived", async () => {
  const receipts = new MemoryReceiptStore();
  const queue = new MemoryQueue([{
    id: "12",
    readCount: 6,
    body: {
      type: "generate_recipe",
      idempotencyKey: "idem-key-2",
      payload: { idempotencyKey: "idem-key-2", requestedBy: "11111111-1111-4111-8111-111111111111", jobId: "job-2" },
    },
  }]);
  const failed: string[] = [];
  await processBatch({
    queue,
    receipts,
    maxAttempts: 5,
    batchSize: 1,
    jobs: jobs({
      async failGeneration(jobId, category) {
        failed.push(`${jobId}:${category}`);
      },
    }),
  });
  assert.deepEqual(failed, ["job-2:exhausted"]);
  assert.deepEqual(queue.archived, ["12"]);
  assert.equal(receipts.rows.size, 0);
});
