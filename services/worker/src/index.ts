import { createServer } from "node:http";
import postgres from "postgres";
import { loadConfig } from "./config.ts";
import { log } from "./log.ts";
import { processBatch } from "./loop.ts";
import { createPgmqAdapter } from "./queue/pgmq.ts";
import { createPostgresReceiptStore } from "./receipts.ts";

const config = loadConfig(process.env);
const sql = postgres(config.databaseUrl, { max: 2, prepare: false });
const queue = createPgmqAdapter(sql, config.visibilityTimeoutSeconds);
const receipts = createPostgresReceiptStore(sql);

let stopped = false;

const server = createServer((request, response) => {
  const path = request.url?.split("?")[0];
  if (request.method === "GET" && path === "/health") {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(JSON.stringify({ ok: true }));
    return;
  }
  response.writeHead(404, { "content-type": "application/json" });
  response.end(JSON.stringify({ ok: false }));
});

server.listen(config.port, () => {
  log({ event: "worker_listening", port: config.port });
});

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function shutdown(): Promise<void> {
  if (stopped) {
    return;
  }
  stopped = true;
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
        maxAttempts: config.maxAttempts,
        batchSize: 5,
      });
    } catch (error) {
      log({
        event: "poll_failed",
        category: error instanceof Error ? error.name : "error",
      });
    }
    if (!stopped) {
      await delay(config.pollIntervalMs);
    }
  }
}

void poll();
