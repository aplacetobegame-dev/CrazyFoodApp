export const API_ERROR_CODES = [
  "unauthenticated",
  "forbidden",
  "validation_error",
  "payload_too_large",
  "missing_idempotency_key",
  "not_found",
  "conflict",
  "internal_error",
] as const;

export type ApiErrorCode = (typeof API_ERROR_CODES)[number];

export type ApiErrorBody = {
  code: ApiErrorCode;
  message: string;
  requestId: string;
};

export const JOB_TYPES = ["echo"] as const;

export type JobType = (typeof JOB_TYPES)[number];

export type EchoJobPayload = {
  idempotencyKey: string;
  requestedBy: string;
};

export type JobMessage = {
  type: "echo";
  idempotencyKey: string;
  payload: EchoJobPayload;
};

export type EchoJobResponse = {
  messageId: string;
  status: "queued";
};

export const MAX_REQUEST_BYTES = 16_384;

export const IDEMPOTENCY_KEY_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$/;

export function normalizeFunctionPath(pathname: string): string {
  const trimmed = pathname.replace(/\/+$/, "") || "/";
  const withoutGateway = trimmed.replace(/^\/functions\/v1(?=\/|$)/, "") || "/";
  const withoutFunction = withoutGateway.replace(/^\/v1(?=\/|$)/, "") || "/";
  return withoutFunction;
}

export function isJobMessage(value: unknown): value is JobMessage {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const message = value as Partial<JobMessage>;
  return (
    message.type === "echo" &&
    typeof message.idempotencyKey === "string" &&
    typeof message.payload === "object" &&
    message.payload !== null &&
    message.payload.idempotencyKey === message.idempotencyKey &&
    typeof message.payload.requestedBy === "string"
  );
}
