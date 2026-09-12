# OWASP / security posture checklist

This documents the *actual* current state of this project, not generic
boilerplate. It's organized loosely around the OWASP API Security Top 10,
citing real files. Reviewed 2026-09-12.

## Mitigated today

- **Rate limiting (API4:2023 Unrestricted Resource Consumption).**
  `slowapi` limits `POST /predict` and `POST /predict/batch` to 30
  requests/minute per client IP (`@limiter.limit("30/minute")` in
  `backend/app/main.py`), keyed by `get_remote_address`. A 429 is returned
  with a consistent error shape via the `RateLimitExceeded` handler.

- **CORS restriction (API8:2023 Security Misconfiguration).**
  `CORSMiddleware` in `backend/app/main.py` restricts origins to an
  explicit allowlist (`CORS_ALLOWED_ORIGINS` env var, comma-separated,
  defaulting to `http://localhost:5173,http://localhost:3000` for local
  dev) and restricts methods to `GET`/`POST`. It is no longer hardcoded
  to localhost only - see `.env.example` and
  `docker-compose.staging.yml.example` / `docker-compose.prod.yml.example`
  for how a real deployment would set it to its actual origin.

- **Input validation / length limits (API3:2023 Broken Object Property
  Level Authorization overlaps here re: mass input abuse).**
  `backend/app/schemas.py` enforces `min_length=1, max_length=300` on
  `PredictRequest.smiles` and `max_length=20` (`MAX_BATCH_SIZE`) on
  `PredictBatchRequest.smiles_list`, via Pydantic, before any RDKit
  parsing happens. Malformed SMILES that pass length checks but fail
  RDKit parsing are still rejected with a 422
  (`InvalidSmilesError` -> `HTTPException(422)` in `main.py`).

- **No secrets in git.** `.gitignore` excludes `.env` and `.env.local`;
  `.env.example` documents variable *names* only, with placeholder/
  localhost values, never real credentials. There are no API keys or
  credentials in this codebase to leak in the first place (see "no auth"
  below) - the main secret-shaped things to guard against were CORS
  origins and future deployment URLs, which now live in `.env`/compose
  override files that are not committed.

- **Dependency scanning.**
  - `pip-audit` runs in CI against `requirements.txt`
    (`.github/workflows/ci.yml` line ~42), currently non-blocking
    (`|| true`) so a new advisory doesn't red the build unexpectedly, but
    it's visible in CI logs.
  - `npm audit --audit-level=high` runs similarly for the frontend
    (`ci.yml` line ~69), also non-blocking today.
  - `.github/dependabot.yml` covers `pip` (root), `npm` (`/frontend`),
    `github-actions`, and `docker` (`/backend`, `/frontend`) ecosystems on
    a weekly schedule, so version bumps (including security patches) show
    up as PRs automatically rather than depending on someone remembering
    to run an audit.

- **Parametrized SQL (API8:2023 / classic SQLi).**
  `backend/app/db.py`'s `insert_history` and `list_history` use `?`
  placeholders with `sqlite3`'s parameter binding
  (`conn.execute("INSERT INTO history (...) VALUES (?, ?, ?, ?, ?)", (...))`),
  never string-formatted SQL. There is exactly one file that touches SQL
  in this codebase, which keeps this easy to audit.

- **Structured logging without body leakage.** `backend/app/logging_config.py`'s
  `log_requests_middleware` deliberately logs method/path/status/latency
  but not the request body, so SMILES strings aren't duplicated into the
  generic request log (they're logged once, deliberately, at the
  `predict_ok`/`predict_rejected` call sites in `main.py`).

## Explicitly NOT done, and why

- **No HTTPS enforcement.** There is no TLS termination, HSTS header, or
  `https://` redirect anywhere in this codebase. Per the README's
  "Status" section, this project is not yet deployed to any real hosting
  - it currently only runs on `localhost` via `docker compose up`, where
  TLS is meaningless (there's no network hop to protect). HTTPS
  enforcement is a hosting-layer concern (reverse proxy / load balancer /
  platform-provided TLS) that will be added when a real hosting choice is
  made, not something to fake in application code today. Tracked as a
  known gap, not an oversight.

- **No API-key/auth.** `/predict`, `/predict/batch`, `/history`, and
  `/model/info` are all unauthenticated. This is intentional: the project
  is a public portfolio/demo, not a service with user accounts or private
  data - `/history` stores only SMILES + predictions, nothing personally
  identifying. Adding auth would add complexity (user management, token
  issuance/rotation) with no real access-control benefit for a stateless
  public demo, and would work against the "try it live" purpose of a
  portfolio piece. Rate limiting (above) is the control actually needed
  here - to prevent abuse/cost blowout, not to restrict who can use it.

- **No WAF / DDoS protection.** There is no Cloudflare/AWS WAF/rate-
  limiting-at-the-edge in front of the backend. This naturally comes
  bundled with whatever real hosting platform is eventually chosen
  (e.g. a managed platform's built-in DDoS protection, or a CDN in front
  of it) rather than being something to build into the FastAPI app
  itself. Building a bespoke WAF-equivalent in application code ahead of
  knowing the actual hosting platform would likely be wasted or
  redundant work.

## Summary

The mitigations above target what's actually exploitable in this
project's current form: a stateless, unauthenticated, public prediction
API with no persistent user data and no real hosting yet. The explicit
non-mitigations are hosting-layer or threat-model decisions, not gaps
that were missed - they should be revisited if/when this moves from
"runs locally via docker compose" to "deployed somewhere with a real
domain," at which point HTTPS enforcement and WAF/DDoS protection become
concrete, host-specific tasks, and the auth question should be re-asked
if the scope grows beyond a public demo (e.g. if `/history` ever became
per-user rather than global).
