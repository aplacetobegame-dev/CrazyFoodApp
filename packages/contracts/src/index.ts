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

export const JOB_TYPES = ["echo", "generate_recipe", "moderate_photo", "render_clip"] as const;

export type JobType = (typeof JOB_TYPES)[number];

export type EchoJobPayload = {
  idempotencyKey: string;
  requestedBy: string;
};

export type GenerateJobPayload = EchoJobPayload & { jobId: string };

export type PhotoJobPayload = EchoJobPayload & { resultId: string };

export type ClipJobPayload = EchoJobPayload & { clipId: string };

export type JobMessage =
  | { type: "echo"; idempotencyKey: string; payload: EchoJobPayload }
  | { type: "generate_recipe"; idempotencyKey: string; payload: GenerateJobPayload }
  | { type: "moderate_photo"; idempotencyKey: string; payload: PhotoJobPayload }
  | { type: "render_clip"; idempotencyKey: string; payload: ClipJobPayload };

export const DAILY_FREE_GENERATIONS = 3;
export const MAX_SERVINGS = 12;

export type GenerationIngredient = { name: string; quantity?: string };

export type GenerationRequest = {
  ingredients: GenerationIngredient[];
  excludedIngredients: string[];
  servings: number;
  weirdness: number;
  constraints: {
    maxMinutes?: number;
    equipment: string[];
    cuisine?: string;
    dietary: string[];
  };
};

export type RecipeDocument = {
  title: string;
  description: string;
  servings: number;
  ingredients: GenerationIngredient[];
  steps: string[];
  prepMinutes: number;
  cookMinutes: number;
  crimeLevel: number;
  regretPotential: number;
  sampleImageKey: "rice" | "mac";
  exclusionsHonored: string[];
};

export type Allowance = {
  freeRemaining: number;
  earnedRemaining: number;
  dailyMaximum: number;
  resetsAt: string;
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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function cleanText(value: unknown, max: number): string | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  if (!trimmed || trimmed.length > max) return null;
  return trimmed;
}

function stringList(value: unknown, maxItems: number, maxLength: number): string[] | null {
  if (!Array.isArray(value) || value.length > maxItems) return null;
  const items: string[] = [];
  for (const entry of value) {
    const text = cleanText(entry, maxLength);
    if (!text) return null;
    items.push(text);
  }
  return items;
}

export function parseGenerationRequest(value: unknown): GenerationRequest | null {
  if (!isRecord(value) || !Array.isArray(value.ingredients)) return null;
  if (value.ingredients.length < 1 || value.ingredients.length > 20) return null;
  const ingredients: GenerationIngredient[] = [];
  for (const entry of value.ingredients) {
    if (!isRecord(entry)) return null;
    const name = cleanText(entry.name, 60);
    if (!name) return null;
    const quantity = entry.quantity === undefined ? undefined : cleanText(entry.quantity, 40) ?? null;
    if (quantity === null) return null;
    ingredients.push(quantity ? { name, quantity } : { name });
  }
  const excludedIngredients = stringList(value.excludedIngredients, 20, 60);
  if (!excludedIngredients) return null;
  const included = new Set(ingredients.map((item) => item.name.toLowerCase()));
  if (excludedIngredients.some((item) => included.has(item.toLowerCase()))) return null;
  if (typeof value.servings !== "number" || !Number.isInteger(value.servings) || value.servings < 1 || value.servings > MAX_SERVINGS) {
    return null;
  }
  if (typeof value.weirdness !== "number" || !Number.isInteger(value.weirdness) || value.weirdness < 0 || value.weirdness > 100) {
    return null;
  }
  const constraints = isRecord(value.constraints) ? value.constraints : {};
  let maxMinutes: number | undefined;
  if (constraints.maxMinutes !== undefined) {
    if (typeof constraints.maxMinutes !== "number" || !Number.isInteger(constraints.maxMinutes) || constraints.maxMinutes < 1 || constraints.maxMinutes > 1440) {
      return null;
    }
    maxMinutes = constraints.maxMinutes;
  }
  const equipment = stringList(constraints.equipment ?? [], 8, 40);
  const dietary = stringList(constraints.dietary ?? [], 8, 40);
  if (!equipment || !dietary) return null;
  const cuisine = constraints.cuisine === undefined ? undefined : cleanText(constraints.cuisine, 40) ?? null;
  if (cuisine === null) return null;
  return {
    ingredients,
    excludedIngredients,
    servings: value.servings,
    weirdness: value.weirdness,
    constraints: { maxMinutes, equipment, cuisine, dietary },
  };
}

export function isJobMessage(value: unknown): value is JobMessage {
  if (!isRecord(value) || typeof value.idempotencyKey !== "string" || !isRecord(value.payload)) {
    return false;
  }
  const payload = value.payload;
  if (payload.idempotencyKey !== value.idempotencyKey || typeof payload.requestedBy !== "string") {
    return false;
  }
  if (value.type === "echo") return true;
  if (value.type === "generate_recipe") return typeof payload.jobId === "string";
  if (value.type === "moderate_photo") return typeof payload.resultId === "string";
  if (value.type === "render_clip") return typeof payload.clipId === "string";
  return false;
}
