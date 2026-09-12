import { defineConfig, devices } from "@playwright/test";

// NOTE: Playwright only manages the frontend (Vite) dev server here.
// The FastAPI backend must be started separately before running this
// suite, e.g. from the repo root:
//   .venv/Scripts/python.exe -m uvicorn backend.app.main:app --port 8000
// A single Playwright `webServer` array entry can only run one command
// with one cwd, and the backend lives in a different directory/venv
// than `npm run dev`, so we don't try to shoehorn both into the same
// array entry - it starts the frontend only and expects the backend to
// already be reachable at http://localhost:8000 (see api.js's
// VITE_API_BASE_URL default).
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "npm run dev -- --port 5173 --strictPort",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 30_000,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
