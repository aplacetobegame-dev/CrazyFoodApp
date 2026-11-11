import assert from "node:assert/strict";
import test from "node:test";
import { prepareCookedPhoto } from "./media.ts";

test("prepareCookedPhoto rejects bytes that are not an image", () => {
  const result = prepareCookedPhoto(new Uint8Array([1, 2, 3, 4]));
  assert.equal("error" in result ? result.error : "", "invalid_image");
});
