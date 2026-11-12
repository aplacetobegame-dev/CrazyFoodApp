import { getSupabase } from "@/lib/client";
import { publicSupabaseConfig } from "@/lib/public-config";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export type Allowance = {
  freeRemaining: number;
  earnedRemaining: number;
  dailyMaximum: number;
  resetsAt: string;
};

export type GenerationJob = {
  jobId: string;
  status: "queued" | "processing" | "complete" | "failed";
  recipeId: string | null;
  errorCategory?: string | null;
  allowance?: Allowance;
  createdAt?: string;
};

export type CookedPhoto = {
  id: string;
  taste: number;
  verdict: string;
  status: string;
  imageUrl?: string | null;
  mine: boolean;
};

export type RecipeView = {
  id: string;
  ownerId: string;
  slug: string;
  title: string;
  description: string;
  visibility: "private" | "public";
  owned: boolean;
  author: string;
  weirdness: number;
  crimeLevel: number;
  regretPotential: number;
  sampleImageKey: "rice" | "mac";
  servings: number | null;
  prepMinutes: number | null;
  cookMinutes: number | null;
  ingredients: { name: string; quantity?: string }[];
  steps: string[];
  votes: { guilty: number; acquitted: number; mine: "guilty" | "acquitted" | null };
  cookedResults: CookedPhoto[];
  createdAt: string;
};

export type Kitchen = {
  recipes: RecipeView[];
  jobs: GenerationJob[];
  allowance: Allowance;
};

export type RecipePage = {
  recipes: RecipeView[];
  nextCursor: string | null;
};

async function api<T>(path: string, init: { method?: string; body?: unknown; idempotencyKey?: string } = {}): Promise<T> {
  const { url, publishableKey } = publicSupabaseConfig();
  const headers = new Headers({ apikey: publishableKey, accept: "application/json" });
  const { data } = await getSupabase().auth.getSession();
  const token = data.session?.access_token;
  if (token) headers.set("authorization", `Bearer ${token}`);
  if (init.body !== undefined) headers.set("content-type", "application/json");
  if (init.idempotencyKey) headers.set("idempotency-key", init.idempotencyKey);
  const response = await fetch(`${url}/functions/v1/v1${path}`, {
    method: init.method ?? (init.body === undefined ? "GET" : "POST"),
    headers,
    body: init.body === undefined ? undefined : JSON.stringify(init.body),
  });
  if (response.status === 204) return undefined as T;
  const text = await response.text();
  const payload = text ? JSON.parse(text) as { message?: string } : {};
  if (!response.ok) throw new ApiError(response.status, payload.message ?? "The request could not be completed.");
  return payload as T;
}

export async function fetchPublicRecipe(slug: string): Promise<RecipeView | null> {
  const { url, publishableKey } = publicSupabaseConfig();
  const response = await fetch(`${url}/functions/v1/v1/recipes/by-slug/${encodeURIComponent(slug)}`, {
    headers: { apikey: publishableKey, accept: "application/json" },
  });
  if (!response.ok) return null;
  return await response.json() as RecipeView;
}

export const backend = {
  allowance: () => api<Allowance>("/allowance"),
  generate: (body: unknown, idempotencyKey: string) => api<GenerationJob>("/generations", { body, idempotencyKey }),
  job: (id: string) => api<GenerationJob>(`/generations/${id}`),
  mine: () => api<Kitchen>("/recipes/mine"),
  discover: (query: string, sort: string, cursor?: string | null) => {
    const params = new URLSearchParams({ q: query, sort });
    if (cursor) params.set("cursor", cursor);
    return api<RecipePage>(`/recipes?${params.toString()}`);
  },
  recipe: (id: string) => api<RecipeView>(`/recipes/${id}`),
  recipeBySlug: (slug: string) => api<RecipeView>(`/recipes/by-slug/${slug}`),
  publish: (id: string) => api<RecipeView>(`/recipes/${id}/publish`, { body: {} }),
  vote: (id: string, verdict: "guilty" | "acquitted") => api<RecipeView>(`/recipes/${id}/vote`, { method: "PUT", body: { verdict } }),
  signUpload: () => api<{ path: string; token: string; signedUrl: string }>("/uploads/sign", { body: {} }),
  cooked: (recipeId: string, body: { path: string; taste: number; verdict: string }, idempotencyKey: string) =>
    api<{ resultId: string; status: string }>(`/recipes/${recipeId}/cooked-results`, { body, idempotencyKey }),
  report: (body: { targetType: "recipe" | "cooked_result"; targetId: string; reason: string }) =>
    api<{ ok: boolean }>("/reports", { body }),
  blocks: () => api<{ blocks: { userId: string; displayName: string }[] }>("/blocks"),
  block: (userId: string) => api<{ ok: boolean }>("/blocks", { body: { userId } }),
  unblock: (userId: string) => api<{ ok: boolean }>(`/blocks/${userId}`, { method: "DELETE" }),
  staff: () => api<{ staff: boolean }>("/staff/me"),
  queue: () => api<{ cooked: { id: string; title: string; verdict: string; taste: number; photoReady: boolean; imageUrl?: string | null; note?: string | null }[]; reports: { id: string; targetType: string; reason: string }[] }>("/moderation/queue"),
  decide: (id: string, decision: "approve" | "reject" | "takedown", note: string) =>
    api<{ ok: boolean }>(`/moderation/cooked-results/${id}`, { body: { decision, note } }),
  createClip: (cookedResultId: string, idempotencyKey: string) =>
    api<{ clipId: string; status: string }>("/clips", { body: { cookedResultId }, idempotencyKey }),
  clip: (id: string) => api<{ clipId: string; status: string; downloadUrl: string | null }>(`/clips/${id}`),
  deleteAccount: (idempotencyKey: string) => api<void>("/account", { method: "DELETE", idempotencyKey }),
};

export async function uploadSignedPhoto(path: string, token: string, uri: string, contentType: string): Promise<void> {
  const file = await fetch(uri);
  const body = new Blob([await file.arrayBuffer()], { type: contentType });
  const { error } = await getSupabase().storage.from("uploads").uploadToSignedUrl(path, token, body, { contentType });
  if (error) throw new ApiError(400, error.message);
}
