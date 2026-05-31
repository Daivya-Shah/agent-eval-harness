/**
 * Vitest config for eval task_003.
 * Loaded from apps/issueflow-frontend so Vite plugins resolve from local node_modules.
 * Pass test paths on the CLI (see task.yaml); do not rely on root under evals/tasks.
 */
import path from "node:path";
import { fileURLToPath } from "node:url";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const frontendDir = path.dirname(fileURLToPath(import.meta.url));
const taskDir = path.resolve(frontendDir, "../../evals/tasks/task_003_frontend_stale_state");

export default defineConfig({
  plugins: [react()],
  root: frontendDir,
  resolve: {
    alias: {
      "@": path.join(frontendDir, "src"),
    },
  },
  server: {
    fs: {
      allow: [frontendDir, taskDir],
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: [path.join(frontendDir, "src/test/setup.ts")],
  },
});
