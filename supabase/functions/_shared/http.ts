import {
  IDEMPOTENCY_KEY_PATTERN,
  MAX_REQUEST_BYTES,
  type ApiErrorBody,
  type ApiErrorCode,
} from "@food-felonies/contracts";

const REQUEST_ID_PATTERN = /^[A-Za-z0-9._:-]{8,128}$/;

export function requestIdFrom(req: Request): string {
  const incoming = req.headers.get("x-request-id");
  if (incoming && REQUEST_ID_PATTERN.test(incoming)) {
    return incoming;
  }
  return crypto.randomUUID();
}

export function errorResponse(
  status: number,
  code: ApiErrorCode,
  message: string,
  requestId: string,
): Response {
  const body: ApiErrorBody = { code, message, requestId };
  console.log(JSON.stringify({ requestId, status, code }));
  return Response.json(body, { status, headers: { "x-request-id": requestId } });
}

export function readIdempotencyKey(req: Request): string | null {
  const value = req.headers.get("idempotency-key")?.trim() ?? "";
  if (!IDEMPOTENCY_KEY_PATTERN.test(value)) {
    return null;
  }
  return value;
}

export async function readLimitedBody(
  req: Request,
): Promise<{ ok: true; text: string } | { ok: false; reason: "too_large" }> {
  const declared = req.headers.get("content-length");
  if (declared !== null && Number(declared) > MAX_REQUEST_BYTES) {
    return { ok: false, reason: "too_large" };
  }

  if (req.body === null) {
    return { ok: true, text: "" };
  }

  const reader = req.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    if (!value) {
      continue;
    }
    total += value.byteLength;
    if (total > MAX_REQUEST_BYTES) {
      await reader.cancel();
      return { ok: false, reason: "too_large" };
    }
    chunks.push(value);
  }

  const merged = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return { ok: true, text: new TextDecoder().decode(merged) };
}
