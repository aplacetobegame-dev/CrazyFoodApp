import assert from "node:assert/strict";
import test from "node:test";
import { serializeSetCookie } from "./session-cookies.ts";

test("serializeSetCookie writes the attributes Supabase asks to persist", () => {
  const header = serializeSetCookie({
    name: "sb-access-token",
    value: "a b",
    options: {
      path: "/",
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      maxAge: 3600,
      expires: new Date("2026-11-12T00:00:00.000Z"),
    },
  });

  assert.match(header, /^sb-access-token=a%20b;/);
  assert.match(header, /Max-Age=3600/);
  assert.match(header, /Path=\//);
  assert.match(header, /HttpOnly/);
  assert.match(header, /Secure/);
  assert.match(header, /SameSite=Lax/);
  assert.match(header, /Expires=Thu, 12 Nov 2026 00:00:00 GMT/);
});
