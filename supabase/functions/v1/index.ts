import "@supabase/functions-js/edge-runtime.d.ts";
import { parseGenerationRequest, normalizeFunctionPath, type EchoJobResponse } from "@food-felonies/contracts";
import { withSupabase } from "@supabase/server";
import { errorResponse, readIdempotencyKey, readLimitedBody, requestIdFrom } from "../_shared/http.ts";

const cors = {
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers":
      "authorization, x-client-info, apikey, content-type, idempotency-key, x-request-id, x-retry-count, traceparent, tracestate, baggage",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
  },
};

type RpcError = { code?: string; message?: string };
type Admin = {
  schema: (name: string) => { rpc: (fn: string, args: Record<string, unknown>) => Promise<{ data: unknown; error: RpcError | null }> };
  storage: {
    from: (bucket: string) => {
      createSignedUploadUrl: (path: string) => Promise<{ data: { signedUrl: string; token: string; path: string } | null; error: { message: string } | null }>;
      createSignedUrl: (path: string, expiresIn: number) => Promise<{ data: { signedUrl: string } | null; error: { message: string } | null }>;
      download: (path: string) => Promise<{ data: Blob | null; error: { message: string } | null }>;
      upload: (path: string, body: ArrayBuffer, options: { contentType: string; upsert: boolean }) => Promise<{ error: { message: string } | null }>;
      remove: (paths: string[]) => Promise<{ error: { message: string } | null }>;
    };
  };
  from: (table: string) => {
    select: (columns: string) => {
      eq: (column: string, value: string) => {
        maybeSingle: () => Promise<{ data: Record<string, unknown> | null; error: { message: string } | null }>;
      };
    };
  };
};

function json(body: unknown, status: number, requestId: string): Response {
  return Response.json(body, { status, headers: { "x-request-id": requestId } });
}

function isResponse(value: unknown): value is Response {
  return value instanceof Response;
}

function mapSql(error: RpcError, requestId: string): Response {
  if (error.code === "P0001") {
    return errorResponse(409, "conflict", "The daily generation limit has been reached.", requestId);
  }
  if (error.code === "P0002") {
    return errorResponse(404, "not_found", "That record was not found.", requestId);
  }
  if (error.code === "42501") {
    return errorResponse(403, "forbidden", "Staff access is required.", requestId);
  }
  if (error.code === "22023") {
    return errorResponse(400, "validation_error", "The request is not valid.", requestId);
  }
  console.log(JSON.stringify({ requestId, status: 500, code: error.code ?? "internal_error" }));
  return errorResponse(500, "internal_error", "The request could not be completed.", requestId);
}

function idempotency(req: Request, requestId: string): string | Response {
  if (req.headers.get("idempotency-key") === null) {
    return errorResponse(400, "missing_idempotency_key", "Idempotency-Key is required.", requestId);
  }
  const key = readIdempotencyKey(req);
  if (!key) return errorResponse(400, "validation_error", "Idempotency-Key is invalid.", requestId);
  return key;
}

async function readJson(req: Request, requestId: string): Promise<Record<string, unknown> | Response> {
  const body = await readLimitedBody(req);
  if (!body.ok) return errorResponse(413, "payload_too_large", "Request body is too large.", requestId);
  if (!body.text.trim()) return {};
  try {
    const parsed: unknown = JSON.parse(body.text);
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      return errorResponse(400, "validation_error", "Request body must be a JSON object.", requestId);
    }
    return parsed as Record<string, unknown>;
  } catch {
    return errorResponse(400, "validation_error", "Request body must be JSON.", requestId);
  }
}

async function userId(supabase: { auth: { getUser: () => Promise<{ data: { user: { id: string } | null } }> } }, required: boolean, requestId: string): Promise<string | null | Response> {
  try {
    const { data } = await supabase.auth.getUser();
    if (!data.user) {
      return required ? errorResponse(401, "unauthenticated", "Sign in is required.", requestId) : null;
    }
    return data.user.id;
  } catch {
    return required ? errorResponse(401, "unauthenticated", "Sign in is required.", requestId) : null;
  }
}

async function signPath(admin: Admin, bucket: unknown, path: unknown): Promise<string | null> {
  if (typeof bucket !== "string" || typeof path !== "string" || !path) return null;
  const { data } = await admin.storage.from(bucket).createSignedUrl(path, 60 * 60);
  return data?.signedUrl ?? null;
}

async function withCookedUrls(admin: Admin, recipe: Record<string, unknown> | null): Promise<Record<string, unknown> | null> {
  if (!recipe || !Array.isArray(recipe.cookedResults)) return recipe;
  const cookedResults = [];
  for (const item of recipe.cookedResults) {
    if (typeof item !== "object" || item === null) continue;
    const row = item as Record<string, unknown>;
    cookedResults.push({ ...row, imageUrl: await signPath(admin, row.bucket, row.path) });
  }
  return { ...recipe, cookedResults };
}

export default {
  fetch: withSupabase({ auth: "none", cors }, async (req, ctx) => {
    const requestId = requestIdFrom(req);
    const path = normalizeFunctionPath(new URL(req.url).pathname);
    const admin = ctx.supabaseAdmin as unknown as Admin;
    const url = new URL(req.url);

    async function rpc(fn: string, args: Record<string, unknown>): Promise<unknown | Response> {
      const { data, error } = await admin.schema("private").rpc(fn, args);
      if (error) return mapSql(error, requestId);
      return data;
    }

    if (req.method === "POST" && path === "/jobs/echo") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const key = idempotency(req, requestId);
      if (isResponse(key)) return key;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const data = await rpc("enqueue_echo", { p_user_id: actor, p_idempotency_key: key });
      if (isResponse(data)) return data;
      const messageId = typeof data === "number" || typeof data === "string" ? String(data) : "";
      if (!/^\d+$/.test(messageId)) return errorResponse(500, "internal_error", "Could not queue the job.", requestId);
      const response: EchoJobResponse = { messageId, status: "queued" };
      return json(response, 202, requestId);
    }

    if (req.method === "GET" && path === "/allowance") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("allowance_snapshot", { p_user_id: actor });
      if (isResponse(data)) return data;
      return json(data, 200, requestId);
    }

    if (req.method === "POST" && path === "/generations") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const key = idempotency(req, requestId);
      if (isResponse(key)) return key;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const request = parseGenerationRequest(body);
      if (!request) return errorResponse(400, "validation_error", "The generation request is not valid.", requestId);
      const data = await rpc("enqueue_generation", { p_user_id: actor, p_idempotency_key: key, p_request: request });
      if (isResponse(data)) return data;
      return json(data, 202, requestId);
    }

    const generationMatch = path.match(/^\/generations\/([0-9a-f-]{36})$/i);
    if (req.method === "GET" && generationMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("job_status", { p_user_id: actor, p_job_id: generationMatch[1] });
      if (isResponse(data)) return data;
      if (!data) return errorResponse(404, "not_found", "That generation was not found.", requestId);
      return json(data, 200, requestId);
    }

    if (req.method === "GET" && path === "/recipes/mine") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("list_my_kitchen", { p_user_id: actor });
      if (isResponse(data)) return data;
      return json(data, 200, requestId);
    }

    if (req.method === "GET" && path === "/recipes") {
      const actor = await userId(ctx.supabase, false, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("list_public_recipes", {
        p_viewer: actor,
        p_query: url.searchParams.get("q") ?? "",
        p_sort: url.searchParams.get("sort") ?? "newest",
        p_cursor: url.searchParams.get("cursor"),
        p_limit: Number(url.searchParams.get("limit") ?? "20"),
      });
      if (isResponse(data)) return data;
      return json(data, 200, requestId);
    }

    const recipeIdMatch = path.match(/^\/recipes\/([0-9a-f-]{36})$/i);
    if (req.method === "GET" && recipeIdMatch?.[1]) {
      const actor = await userId(ctx.supabase, false, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("get_recipe", { p_viewer: actor, p_recipe_id: recipeIdMatch[1] });
      if (isResponse(data)) return data;
      if (!data || typeof data !== "object") return errorResponse(404, "not_found", "That recipe was not found.", requestId);
      return json(await withCookedUrls(admin, data as Record<string, unknown>), 200, requestId);
    }

    const slugMatch = path.match(/^\/recipes\/by-slug\/([a-z0-9-]{8,80})$/i);
    if (req.method === "GET" && slugMatch?.[1]) {
      const actor = await userId(ctx.supabase, false, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("get_recipe_by_slug", { p_viewer: actor, p_slug: slugMatch[1] });
      if (isResponse(data)) return data;
      if (!data || typeof data !== "object") return errorResponse(404, "not_found", "That recipe was not found.", requestId);
      return json(await withCookedUrls(admin, data as Record<string, unknown>), 200, requestId);
    }

    const publishMatch = path.match(/^\/recipes\/([0-9a-f-]{36})\/publish$/i);
    if (req.method === "POST" && publishMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("publish_recipe", { p_user_id: actor, p_recipe_id: publishMatch[1] });
      if (isResponse(data)) return data;
      return json(await withCookedUrls(admin, data as Record<string, unknown>), 200, requestId);
    }

    const voteMatch = path.match(/^\/recipes\/([0-9a-f-]{36})\/vote$/i);
    if (req.method === "PUT" && voteMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const data = await rpc("set_vote", { p_user_id: actor, p_recipe_id: voteMatch[1], p_verdict: body.verdict });
      if (isResponse(data)) return data;
      return json(await withCookedUrls(admin, data as Record<string, unknown>), 200, requestId);
    }

    if (req.method === "POST" && path === "/uploads/sign") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const objectPath = `${actor}/${crypto.randomUUID()}`;
      const { data, error } = await admin.storage.from("uploads").createSignedUploadUrl(objectPath);
      if (error || !data) return errorResponse(500, "internal_error", "Could not prepare the upload.", requestId);
      return json({ path: objectPath, token: data.token, signedUrl: data.signedUrl }, 200, requestId);
    }

    const cookedMatch = path.match(/^\/recipes\/([0-9a-f-]{36})\/cooked-results$/i);
    if (req.method === "POST" && cookedMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const key = idempotency(req, requestId);
      if (isResponse(key)) return key;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const data = await rpc("create_cooked_result", {
        p_user_id: actor,
        p_recipe_id: cookedMatch[1],
        p_path: body.path,
        p_taste: body.taste,
        p_verdict: body.verdict,
        p_idempotency_key: key,
      });
      if (isResponse(data)) return data;
      return json(data, 202, requestId);
    }

    if (req.method === "POST" && path === "/reports") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const data = await rpc("create_report", {
        p_user_id: actor,
        p_target_type: body.targetType,
        p_target_id: body.targetId,
        p_reason: body.reason,
      });
      if (isResponse(data)) return data;
      return json({ ok: true }, 201, requestId);
    }

    if (req.method === "GET" && path === "/blocks") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("list_blocks", { p_user_id: actor });
      if (isResponse(data)) return data;
      return json({ blocks: data }, 200, requestId);
    }

    if (req.method === "POST" && path === "/blocks") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const data = await rpc("set_block", { p_blocker: actor, p_blocked: body.userId, p_active: true });
      if (isResponse(data)) return data;
      return json({ ok: true }, 200, requestId);
    }

    const unblockMatch = path.match(/^\/blocks\/([0-9a-f-]{36})$/i);
    if (req.method === "DELETE" && unblockMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("set_block", { p_blocker: actor, p_blocked: unblockMatch[1], p_active: false });
      if (isResponse(data)) return data;
      return json({ ok: true }, 200, requestId);
    }

    if (req.method === "GET" && path === "/staff/me") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("is_staff", { p_user_id: actor });
      if (isResponse(data)) return data;
      return json({ staff: data === true }, 200, requestId);
    }

    if (req.method === "GET" && path === "/moderation/queue") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("moderation_queue", { p_staff_id: actor });
      if (isResponse(data)) return data;
      const queue = data as { cooked?: Record<string, unknown>[] };
      if (Array.isArray(queue?.cooked)) {
        for (const item of queue.cooked) item.imageUrl = await signPath(admin, item.bucket, item.path);
      }
      return json(data, 200, requestId);
    }

    const decisionMatch = path.match(/^\/moderation\/cooked-results\/([0-9a-f-]{36})$/i);
    if (req.method === "POST" && decisionMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const resultId = decisionMatch[1];
      let publicPath: string | null = null;
      if (body.decision === "approve") {
        const { data: row, error } = await admin.from("cooked_results").select("original_path, owner_id, photo_ready, media_type").eq("id", resultId).maybeSingle();
        if (error || !row) return errorResponse(404, "not_found", "That cooked result was not found.", requestId);
        if (row.photo_ready !== true || typeof row.original_path !== "string" || typeof row.owner_id !== "string") {
          return errorResponse(400, "validation_error", "The photo is not ready to approve.", requestId);
        }
        const downloaded = await admin.storage.from("uploads").download(row.original_path);
        if (downloaded.error || !downloaded.data) return errorResponse(500, "internal_error", "Could not read the photo.", requestId);
        const mediaType = row.media_type === "image/png" || row.media_type === "image/webp" ? row.media_type : "image/jpeg";
        const extension = mediaType === "image/png" ? "png" : mediaType === "image/webp" ? "webp" : "jpg";
        publicPath = `${row.owner_id}/${resultId}.${extension}`;
        const uploaded = await admin.storage.from("public-media").upload(publicPath, await downloaded.data.arrayBuffer(), { contentType: mediaType, upsert: true });
        if (uploaded.error) return errorResponse(500, "internal_error", "Could not publish the photo.", requestId);
      }
      const data = await rpc("staff_decision", {
        p_staff_id: actor,
        p_result_id: resultId,
        p_decision: body.decision,
        p_note: body.note ?? "",
        p_public_path: publicPath,
      });
      if (isResponse(data)) return data;
      const previous = (data as { previousPublicPath?: string | null }).previousPublicPath;
      if (body.decision === "takedown" && previous) {
        await admin.storage.from("public-media").remove([previous]);
      }
      return json({ ok: true }, 200, requestId);
    }

    if (req.method === "POST" && path === "/clips") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const key = idempotency(req, requestId);
      if (isResponse(key)) return key;
      const body = await readJson(req, requestId);
      if (isResponse(body)) return body;
      const data = await rpc("create_clip", { p_user_id: actor, p_result_id: body.cookedResultId, p_idempotency_key: key });
      if (isResponse(data)) return data;
      return json(data, 202, requestId);
    }

    const clipMatch = path.match(/^\/clips\/([0-9a-f-]{36})$/i);
    if (req.method === "GET" && clipMatch?.[1]) {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const data = await rpc("get_clip", { p_user_id: actor, p_clip_id: clipMatch[1] });
      if (isResponse(data)) return data;
      if (!data || typeof data !== "object") return errorResponse(404, "not_found", "That clip was not found.", requestId);
      const clip = data as Record<string, unknown>;
      return json({ ...clip, downloadUrl: await signPath(admin, clip.bucket, clip.path) }, 200, requestId);
    }

    if (req.method === "DELETE" && path === "/account") {
      const actor = await userId(ctx.supabase, true, requestId);
      if (isResponse(actor)) return actor;
      const key = idempotency(req, requestId);
      if (isResponse(key)) return key;
      const data = await rpc("delete_account", { p_user_id: actor, p_idempotency_key: key });
      if (isResponse(data)) return data;
      return new Response(null, { status: 204, headers: { "x-request-id": requestId } });
    }

    return errorResponse(404, "not_found", "That route does not exist.", requestId);
  }),
};
