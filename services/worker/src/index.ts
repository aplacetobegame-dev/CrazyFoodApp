import { createServer, type ServerResponse } from "node:http";
import postgres from "postgres";
import { loadConfig } from "./config.ts";
import { createJobEffects } from "./effects.ts";
import { log } from "./log.ts";
import { processBatch } from "./loop.ts";
import { createPgmqAdapter } from "./queue/pgmq.ts";
import { createPostgresReceiptStore } from "./receipts.ts";
import { createStorage } from "./storage.ts";

const config = loadConfig(process.env);
const sql = postgres(config.databaseUrl, { max: 2, prepare: false });
const queue = createPgmqAdapter(sql, config.visibilityTimeoutSeconds);
const receipts = createPostgresReceiptStore(sql);
const storage = config.supabaseUrl && config.supabaseSecretKey
  ? createStorage(config.supabaseUrl, config.supabaseSecretKey)
  : null;
const jobs = createJobEffects(sql, storage);

let stopped = false;
let lastPollError: string | null = null;
let wake: (() => void) | null = null;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      wake = null;
      resolve();
    }, ms);
    wake = () => {
      clearTimeout(timer);
      wake = null;
      resolve();
    };
  });
}

async function databaseUp(): Promise<boolean> {
  try {
    await sql`select 1`;
    return true;
  } catch {
    return false;
  }
}

function sendJson(response: ServerResponse, status: number, body: unknown) {
  response.writeHead(status, { "content-type": "application/json" });
  response.end(JSON.stringify(body));
}

const server = createServer((request, response) => {
  const path = request.url?.split("?")[0];
  if (request.method === "GET" && path === "/health") {
    void databaseUp().then((up) => {
      const ok = up && lastPollError === null;
      sendJson(response, ok ? 200 : 503, { ok });
    }).catch(() => {
      sendJson(response, 503, { ok: false });
    });
    return;
  }
  sendJson(response, 404, { ok: false });
});

server.listen(config.port, () => {
  log({ event: "worker_listening", port: config.port });
});

async function shutdown(): Promise<void> {
  if (stopped) return;
  stopped = true;
  wake?.();
  await pollLoop;
  await new Promise<void>((resolve) => {
    server.close(() => resolve());
  });
  await sql.end({ timeout: 5 });
}

process.on("SIGTERM", () => {
  void shutdown();
});
process.on("SIGINT", () => {
  void shutdown();
});

async function poll(): Promise<void> {
  while (!stopped) {
    try {
      await processBatch({
        queue,
        receipts,
        jobs,
        maxAttempts: config.maxAttempts,
        batchSize: 5,
      });
      lastPollError = null;
    } catch (error) {
      lastPollError = error instanceof Error ? error.name : "error";
      log({ event: "poll_failed", category: lastPollError });
    }
    if (!stopped) await delay(config.pollIntervalMs);
  }
}

const pollLoop = poll();
