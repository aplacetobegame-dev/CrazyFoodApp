import "@supabase/functions-js/edge-runtime.d.ts";
import type { EchoJobResponse } from "@food-felonies/contracts";
import { normalizeFunctionPath } from "@food-felonies/contracts";
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

function messageIdFrom(data: unknown): string | null {
  if (typeof data === "number" && Number.isSafeInteger(data)) {
    return String(data);
  }
  if (typeof data === "string" && /^\d+$/.test(data)) {
    return data;
  }
  return null;
}

export default {
  fetch: withSupabase({ auth: "user", cors }, async (req, ctx) => {
    const requestId = requestIdFrom(req);
    const path = normalizeFunctionPath(new URL(req.url).pathname);

    const { data: userData, error: userError } = await ctx.supabase.auth.getUser();
    if (userError || !userData.user) {
      return errorResponse(401, "unauthenticated", "Sign in is required.", requestId);
    }
    const userId = userData.user.id;

    if (req.method === "POST" && path === "/jobs/echo") {
      const idempotencyKey = readIdempotencyKey(req);
      if (req.headers.get("idempotency-key") === null) {
        return errorResponse(
          400,
          "missing_idempotency_key",
          "Idempotency-Key is required.",
          requestId,
        );
      }
      if (!idempotencyKey) {
        return errorResponse(400, "validation_error", "Idempotency-Key is invalid.", requestId);
      }

      const body = await readLimitedBody(req);
      if (!body.ok) {
        return errorResponse(413, "payload_too_large", "Request body is too large.", requestId);
      }
      if (body.text.trim() !== "") {
        try {
          const parsed: unknown = JSON.parse(body.text);
          if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
            return errorResponse(400, "validation_error", "Request body must be a JSON object.", requestId);
          }
        } catch {
          return errorResponse(400, "validation_error", "Request body must be JSON.", requestId);
        }
      }

      const { data, error } = await ctx.supabaseAdmin.schema("private").rpc("enqueue_echo", {
        p_user_id: userId,
        p_idempotency_key: idempotencyKey,
      });
      if (error) {
        console.log(JSON.stringify({ requestId, status: 500, code: "internal_error" }));
        return errorResponse(500, "internal_error", "Could not queue the job.", requestId);
      }

      const messageId = messageIdFrom(data);
      if (!messageId) {
        return errorResponse(500, "internal_error", "Could not queue the job.", requestId);
      }

      const response: EchoJobResponse = { messageId, status: "queued" };
      console.log(JSON.stringify({ requestId, status: 202, code: "queued", userId }));
      return Response.json(response, { status: 202, headers: { "x-request-id": requestId } });
    }

    if (req.method === "DELETE" && path === "/account") {
      const idempotencyKey = readIdempotencyKey(req);
      if (req.headers.get("idempotency-key") === null) {
        return errorResponse(
          400,
          "missing_idempotency_key",
          "Idempotency-Key is required.",
          requestId,
        );
      }
      if (!idempotencyKey) {
        return errorResponse(400, "validation_error", "Idempotency-Key is invalid.", requestId);
      }

      const { error } = await ctx.supabaseAdmin.schema("private").rpc("delete_account", {
        p_user_id: userId,
      });
      if (error) {
        console.log(JSON.stringify({ requestId, status: 500, code: "internal_error" }));
        return errorResponse(500, "internal_error", "Could not delete the account.", requestId);
      }

      console.log(JSON.stringify({ requestId, status: 204, code: "account_deleted", userId }));
      return new Response(null, { status: 204, headers: { "x-request-id": requestId } });
    }

    return errorResponse(404, "not_found", "That route does not exist.", requestId);
  }),
};
