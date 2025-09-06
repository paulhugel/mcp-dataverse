> Update — Fri Sep 5, 2025 (HST)

- Status: VS Code Docker (Container Tools) extension installed; we will run locally via Docker first to avoid the hosted MCP issue with Jan/VS Code.
- Rationale: Hosted `mcp-dataverse` currently has a client-compat bug; local run lets us iterate and validate fixes.
- Local changes made today (can revert on request):
  - semantic_croissant/server.py: renamed internal helper to `process_datatool` to avoid recursion with the `datatool` tool handler.
  - semantic_croissant/server.py: tool handlers now return MCP-compliant content (e.g., `TextContent` with `mimeType`) instead of raw dict/string.
  - semantic_croissant/server.py: removed non‑spec fields from `list_tools` definitions; kept endpoint mapping only in `/tools` JSON for browsing.
  - semantic_croissant/server.py: added `import os` for overview endpoints to avoid `NameError`.
  - semantic_croissant/__main__.py: switched to relative import so `python -m semantic_croissant` works.
  - Git remotes configured: `origin` → `https://github.com/paulhugel/mcp-dataverse.git`, `upstream` → `https://github.com/gdcc/mcp-dataverse.git`.

—

**Purpose**
- Establish a stable, maintainable setup for mcp-dataverse for multi‑year use, with clear steps to run locally (no Docker) and via Docker later, plus hardening tasks (pin deps, tests, and observability).

**Current State**
- Server: `semantic_croissant/server.py:1` exposes MCP over SSE and REST tools.
- CLI: `semantic_croissant/pyproject.toml:23` → `semantic-croissant = "semantic_croissant.server:main"`.
- Docs: `README.md:1` covers client setup and curl examples.
- Risks: unpinned deps; import-time side effects in `utils/dataframe.py:124` and `semantic_croissant/dataframe.py:124`; heavy optional deps in `requirements.txt:1`.

**Today (Fri Sep 5, 2025): Docker‑First via VS Code Docker**
- Ensure Docker Desktop is running; verify in VS Code Docker panel.
- Create `.env` (can be empty for now) and use Docker extension to build and bring up `docker-compose.yaml`.
- Verify service:
  - Open `http://127.0.0.1:8100/tools` and `http://127.0.0.1:8100/status`.
  - Curl test: `curl -X POST "http://localhost:8100/tools/get_croissant_record" -H "Content-Type: application/json" -d '{"doi":"doi:10.7910/DVN/WGCRY7"}'`.
- Configure clients to local SSE:
  - Jan/VS Code MCP SSE URL: `http://localhost:8100/sse`.

**Next: Local Run (no Docker) — optional**
- Option A: venv + pip
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - `pip install -e semantic_croissant`  # installs CLI entrypoint and `mcp`
  - Run: `semantic_croissant --transport sse --port 8000`
- Option B: uv (faster, reproducible)
  - Install `uv` (e.g., `brew install uv`)
  - `cd semantic_croissant && uv sync`
  - Run: `uv run semantic_croissant --transport sse --port 8000`
- Verify endpoints
  - `curl http://localhost:8000/tools`
  - `curl -X POST "http://localhost:8000/tools/get_croissant_record" -H "Content-Type: application/json" -d '{"doi":"doi:10.7910/DVN/WGCRY7"}'`

**Client Configuration**
- MCP SSE URL to use in clients: `http://localhost:8000/sse` (or `http://localhost:8100/sse` via Docker Compose).
- Jan HTTPS Proxy: requires a forward proxy (not FastAPI). If needed:
  - `brew install mitmproxy`
  - `mitmdump --mode regular --listen-port 8080`
  - Configure Jan HTTPS Proxy: `http://127.0.0.1:8080` (toggle “Ignore SSL Certificates” only if required).

**Weeks 1–2 (starting Sep 5, 2025)**
- Pin dependencies
  - Replace loose pins in `requirements.txt:1` with exact versions (use `pip-tools` or `uv lock`).
  - Replace `git+https://github.com/Dans-labs/pyDataverse@development` with a tagged release or a fixed commit SHA.
  - Consider moving heavy, optional deps (`torch`, `yt-dlp`, `ollama`) to optional extras or a separate extras file.
- Remove import-time side effects
  - Wrap demo code in `if __name__ == "__main__":` in `utils/dataframe.py:124` and `semantic_croissant/dataframe.py:124` to make imports safe.
- Version and health
  - Add `/version` returning app version + git SHA.
  - Keep `/status` as lightweight health probe (already present in `semantic_croissant/server.py:300`).
- Logging
  - Ensure structured logs to stdout; standardize log level via env (e.g., `LOG_LEVEL`).

**Week 2 (optional): Docker Improvements**
- Base image: switch to `python:3.12-slim` LTS and pin by digest.
- Multi-stage build: install build deps in builder stage; copy locked site-packages to runtime.
- Cache: mount `./cache:/root/.cache` as in `docker-compose.yaml:18`.

**Week 3: CI and Maintenance**
- GitHub Actions
  - Build image on PR; run smoke tests:
    - `curl /tools` returns tool list.
    - `POST /tools/get_croissant_record` returns JSON.
  - Scheduled monthly rebuild to pick up base image security patches.
- Dependabot/Renovate for Docker base and Python deps.

**Smoke Test Checklist**
- Start server (local or Docker).
- `GET /tools` returns tool metadata.
- `POST /tools/get_croissant_record` with a known DOI returns Croissant JSON.
- `GET /status` returns `{ "status": "ok" }`.

**Open Questions**
- Preferred runtime long-term: Docker or local service (launchd/systemd)?
- Which clients should we optimize for first (Jan, Cursor, VS Code, Claude)?
- Are heavy deps (`torch`, `yt-dlp`, `ollama`) required for your use-case now, or can they become optional?

**Next Actions (one step at a time, with approval)**
- Walk you through VS Code Docker build/up and verify endpoints.
- If confirmed working: pin/lock dependencies and remove remaining import-time side effects.
- Add `/version` endpoint and a smoke test script.
- Document Jan config (local SSE URL; optional HTTPS proxy).
