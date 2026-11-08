export type WorkerConfig = {
  databaseUrl: string;
  visibilityTimeoutSeconds: number;
  maxAttempts: number;
  pollIntervalMs: number;
  port: number;
};

export function loadConfig(env: NodeJS.ProcessEnv): WorkerConfig {
  const databaseUrl = env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("Missing DATABASE_URL");
  }

  return {
    databaseUrl,
    visibilityTimeoutSeconds: positiveInt(env.WORKER_VISIBILITY_TIMEOUT_SECONDS, 30),
    maxAttempts: positiveInt(env.WORKER_MAX_ATTEMPTS, 5),
    pollIntervalMs: positiveInt(env.WORKER_POLL_INTERVAL_MS, 1000),
    port: positiveInt(env.PORT, 8080),
  };
}

function positiveInt(value: string | undefined, fallback: number): number {
  if (value === undefined || value.trim() === "") {
    return fallback;
  }
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error("Invalid numeric configuration");
  }
  return parsed;
}
