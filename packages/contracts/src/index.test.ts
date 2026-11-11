import assert from "node:assert/strict";
import test from "node:test";
import { isJobMessage, normalizeFunctionPath, parseGenerationRequest } from "./index.ts";

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
  assert.equal(isJobMessage({
    type: "generate_recipe",
    idempotencyKey: "idem-key-1",
    payload: { idempotencyKey: "idem-key-1", requestedBy: "user-1", jobId: "job-1" },
  }), true);
});

test("parseGenerationRequest rejects overlap, bad servings, and accepts a normal request", () => {
  const valid = parseGenerationRequest({
    ingredients: [{ name: "Rice", quantity: "1 cup" }],
    excludedIngredients: ["peanuts"],
    servings: 2,
    weirdness: 10,
    constraints: { equipment: [], dietary: [], maxMinutes: 20 },
  });
  assert.equal(valid?.servings, 2);
  assert.equal(parseGenerationRequest({
    ingredients: [{ name: "Rice" }],
    excludedIngredients: [],
    servings: 13,
    weirdness: 10,
    constraints: { equipment: [], dietary: [] },
  }), null);
  assert.equal(parseGenerationRequest({
    ingredients: [{ name: "Rice" }],
    excludedIngredients: ["rice"],
    servings: 2,
    weirdness: 10,
    constraints: { equipment: [], dietary: [] },
  }), null);
});
