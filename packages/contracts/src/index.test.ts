import assert from "node:assert/strict";
import test from "node:test";
import { isJobMessage, normalizeFunctionPath } from "./index.ts";

test("normalizeFunctionPath strips the gateway and function prefix", () => {
  assert.equal(normalizeFunctionPath("/functions/v1/v1/jobs/echo"), "/jobs/echo");
  assert.equal(normalizeFunctionPath("/v1/jobs/echo/"), "/jobs/echo");
  assert.equal(normalizeFunctionPath("/jobs/echo"), "/jobs/echo");
  assert.equal(normalizeFunctionPath("/functions/v1/v1"), "/");
});

test("isJobMessage accepts only a complete echo envelope", () => {
  const message = {
    type: "echo",
    idempotencyKey: "idem-key-1",
    payload: {
      idempotencyKey: "idem-key-1",
      requestedBy: "user-1",
    },
  };
  assert.equal(isJobMessage(message), true);
  assert.equal(isJobMessage({ ...message, payload: { ...message.payload, idempotencyKey: "other" } }), false);
  assert.equal(isJobMessage({ type: "recipe" }), false);
});
