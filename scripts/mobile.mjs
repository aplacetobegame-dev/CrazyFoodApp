import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import process from "node:process";
import { fileURLToPath, URL } from "node:url";

const appDirectory = new URL("../apps/mobile/", import.meta.url);
const appRequire = createRequire(new URL("package.json", appDirectory));
const args = process.argv.slice(2);
const mode = args.includes("--test") ? "preview" : "connected";
const expoArgs = args.filter((arg) => arg !== "--test");

const { error, status } = spawnSync(
  process.execPath,
  [appRequire.resolve("expo/bin/cli"), "start", ...expoArgs],
  {
    cwd: fileURLToPath(appDirectory),
    env: { ...process.env, EXPO_PUBLIC_APP_MODE: mode },
    stdio: "inherit",
  },
);

if (error) {
  throw error;
}
process.exitCode = status ?? 1;
