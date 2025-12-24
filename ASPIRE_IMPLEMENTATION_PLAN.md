# Aspire + OpenTelemetry Implementation Plan (PrismWeave)

Date: 2025-12-24

## Goal

Run PrismWeave as a polyglot distributed application via a file-based Aspire AppHost, with **logs, traces, and metrics exported via OpenTelemetry (OTLP)** to the Aspire dashboard.

Target services:

- `ai-processing` (Python, FastAPI + MCP SSE)
- `visualization` (JavaScript, Vite dev server)
- `website` (JavaScript, Node static dev server)

Non-goals (for this phase): browser extension + VS Code extension orchestration.

---

## Current State (what already exists)

- AppHost exists at the repo root:
  - [apphost.cs](apphost.cs)
  - [apphost.run.json](apphost.run.json)

Note:

- `apphost.run.json` now includes a `profiles.Default` launch profile that configures the Aspire dashboard URL + OTLP HTTP endpoint (and allows unsecured HTTP transport for local dev).
- Python service configures OpenTelemetry early:
  - [ai-processing/src/unified_app.py](ai-processing/src/unified_app.py)
  - [ai-processing/src/telemetry.py](ai-processing/src/telemetry.py)
- Node services include OTEL dependencies:
  - [visualization/telemetry.cjs](visualization/telemetry.cjs) preloaded via `NODE_OPTIONS`
  - [website/scripts/telemetry.mjs](website/scripts/telemetry.mjs) imported by the dev server

---

## Implementation Steps

### 1) AppHost orchestration

1. Ensure AppHost includes the Python and JavaScript hosting packages.
2. Model each service as a resource:
   - Python: `AddUvicornApp("ai-processing", "./ai-processing", "src.unified_app:app")`
   - Vite: `AddViteApp("visualization", "./visualization")`
   - Node: `AddNodeApp("website", "./website", "scripts/dev-server.mjs")`
3. Wire dependencies:
   - `.WithReference(aiProcessing)` + `.WaitFor(aiProcessing)` for UIs.
4. Prefer passing runtime config via parameters + `.WithEnvironment()`.

Expected outcome:

- `aspire run` starts all 3 resources and shows them healthy in the dashboard.

### 2) Python OpenTelemetry (logs + traces + metrics)

1. Configure telemetry early in process startup (`unified_app.py`).
2. Export to Aspire using OTLP **HTTP** via `OTEL_EXPORTER_OTLP_ENDPOINT`.
3. Enable:
   - Tracing (FastAPI instrumentation)
   - Metrics (OTLP metric exporter)
   - Logging (stdlib `logging` bridged to OTEL logs)
4. Hard requirement: **never crash** if telemetry setup fails.

Expected outcome:

- Hitting `/health` creates a trace visible in Aspire.
- Python logs appear in Aspire logs view.

### 3) Node OpenTelemetry (logs + traces + metrics)

1. Initialize OpenTelemetry only when `OTEL_EXPORTER_OTLP_ENDPOINT` is present.
2. Export:
   - traces → `/v1/traces`
   - metrics → `/v1/metrics`
   - logs → `/v1/logs`
3. Bridge logging to OpenTelemetry:
   - Patch `console.*` to emit OTEL log records.
   - Keep optional console passthrough controlled by `PRISMWEAVE_OTEL_CONSOLE_PASSTHROUGH`.

Expected outcome:

- Dev-server/Vite logs show up as OTEL logs in Aspire while running under `aspire run`.

---

## Verification Plan

### A) Fast verification (local)

1. Run `aspire run` from the repo root.
2. Open the dashboard URL printed by the CLI.
3. In the **Resources** page, confirm:
   - `ai-processing` is healthy (health check OK)
   - `visualization` is running
   - `website` is running
4. Generate traffic:
   - `ai-processing`: open `/health` in a browser
   - `visualization`: open the UI and refresh once
   - `website`: open the website endpoint and refresh once
5. In the dashboard:
   - Logs: confirm logs exist for each service
   - Traces: confirm at least one trace for `ai-processing` (request)
   - Metrics: confirm metrics arrive (may take a few seconds)

### B) Automated verification (tests)

- Python unit tests:
  - Validate OTLP endpoint normalization for HTTP exporters.
  - Ensure `configure_telemetry()` and `instrument_fastapi()` never crash.

Suggested command:

- `cd ai-processing && pytest`

---

## Rollback / Safety

- If OTLP env vars are absent, telemetry should be a no-op and services should run normally.
- Telemetry setup is best-effort; failures must not prevent startup.

---

## Notes

- Aspire sets `OTEL_*` environment variables automatically in local dev.
- For OTLP **HTTP** exporters, Aspire’s endpoint is typically a base URL like `http://localhost:4318`.
  When explicitly configuring exporters, append the per-signal path (`/v1/traces`, `/v1/metrics`, `/v1/logs`).
