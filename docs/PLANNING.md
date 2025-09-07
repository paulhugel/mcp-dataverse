# Planning Guide (Current Course)

## Current State (Sat Sep  6 18:38:24 HST 2025)
- Serialization: datetime/date/time serialized to ISO 8601 across all outputs.
- Croissant:
  - GET `/tools/get_croissant_record?doi=…` returns JSON‑LD (`Content-Type: application/ld+json`).
  - MCP tool `get_croissant_record` returns `TextContent` with `mimeType: application/ld+json`.
- SSE Health:
  - GET `/` returns 200 (alias of `/status`).
  - Invalid `POST /messages` without a session returns 204 (health probe friendly). Real SSE sessions unchanged.
- MCP Tools (implemented and callable):
  - `fetch` (text/html), `get_croissant_record` (application/ld+json), `datatool` (application/json),
    `overview`, `overview_datasets`, `overview_files`, `search_datasets`, `now` (time).
- datatool:
  - Robust dataset JSON parsing; returns JSON object (empty for non‑tabular) instead of 500.
- Utility:
  - `GET /time` returns `{"now":"<ISO8601 UTC>"}`; MCP tool `now` mirrors this.

## Jan (SSE) Configuration
- Transport: `SSE`
- URL: `http://localhost:8000/sse`
- Headers: none
- Timeout: `60`
- Notes:
  - Jan probes `/` and `/messages`; server now returns 200 and 204 respectively to avoid health‑check loops.

## How to Verify (External)
- Health:
  - `curl -sSI http://localhost:8000/ | head -n 1` → `HTTP/1.1 200 OK`
  - `curl -i -X POST 'http://localhost:8000/messages/?session_id=test' -H 'Content-Type: application/json' -d '{}' | head -n 1` → `HTTP/1.1 204 No Content`
- Croissant JSON‑LD (RI9JFU):
  - `curl -sS 'http://localhost:8000/tools/get_croissant_record?doi=10.7910/DVN/RI9JFU' | jq -r '.dateCreated'` → `YYYY-MM-DDTHH:MM:SS`
- MCP‑style POST wrapper:
  - `curl -sS -X POST 'http://localhost:8000/get_croissant_record' -H 'Content-Type: application/json' -d '{"doi":"10.7910/DVN/RI9JFU"}' | jq -r '.mimeType'` → `application/ld+json`
- Overview/search:
  - `curl -sS 'http://localhost:8000/overview/datasets?host=dataverse.harvard.edu' | jq -r '.datasets.count // .datasets.total_count'`
  - `curl -sS 'http://localhost:8000/search/datasets?host=dataverse.harvard.edu&query=*' | jq -r '.datasets.count // .datasets.total_count'`
- datatool:
  - `curl -sS 'http://localhost:8000/datatool?doi=10.18710/CHMWOB&file=00_README.txt' | jq -r '.'` → `{}` (no crash)
- Time:
  - `curl -sS http://localhost:8000/time | jq -r '.now'` → ISO 8601 UTC string

## Operate (Docker)
- Build: `docker build -t mcp-dataverse:dev .`
- Run: `docker rm -f mcp-dataverse 2>/dev/null || true; docker run -d --name mcp-dataverse -p 8000:8000 mcp-dataverse:dev`
- Persist: `docker update --restart unless-stopped mcp-dataverse`

## Decisions Log (Implemented vs. Considered)
- Chose server‑side serialization over client serializers; no non‑JSON types emitted.
- Kept single‑URL SSE; added `/` and tolerant `/messages` behavior to satisfy health checks.
- Aligned tools/list with tools/call by adding missing MCP handlers and returning `TextContent`.
- Made datatool resilient to missing/atypical dataset structures; returns JSON instead of 500.
- Added `now` tool and `/time` route for reliable timestamps.

## Known Limitations / Follow‑ups
- `/overview` requires `DATAVERSES` env; returns clear 500 if unset.
- datatool returns empty JSON for non‑tabular files; optional enhancement: text preview fallback.
- Minor duplication in GET/POST parsing paths; consider consolidation later.

## Nightly Closing Checklist
- Repo clean: `git status -sb` (no unexpected changes)
- Push state: `git push` (if on a branch) and verify PR status
- Session notes: update `proposed_Codex_mcp-dataverse_plan.md`
- Container state:
  - Keep running: `docker update --restart unless-stopped mcp-dataverse`
  - Or stop: `docker stop mcp-dataverse && docker rm mcp-dataverse`
- Health check (if server is running): `/`, `/tools`, Croissant GET
- Local clutter: preview `git clean -ndX`; remove with `git clean -fdX`
- Secrets hygiene: no real tokens committed; use env vars

## Restart Next Session
- If container is running with auto‑restart: visit `http://localhost:8000/status`
- If not running: `docker run -d --name mcp-dataverse -p 8000:8000 mcp-dataverse:dev`
- Pull latest: `git checkout main && git pull --ff-only`
