# Planning Guide

## Nightly Closing Checklist

Use this quick checklist to close out a work session cleanly and be ready to resume later.

- Repo clean: run `git status -sb` and ensure no unexpected changes
- Push state: `git push` (if on a branch) and verify PR status
- Session notes: update `proposed_Codex_mcp-dataverse_plan.md` (or your local notes)
- Container state:
  - If keeping local server: `docker update --restart unless-stopped mcp-dataverse`
  - If stopping for the night: `docker stop mcp-dataverse && docker rm mcp-dataverse`
- Quick health check (if server is running):
  - `curl -sS localhost:8000/status` → expects `{ "status": "ok" }`
  - `curl -sS localhost:8000/tools` → lists tools
  - `curl -sS 'http://localhost:8000/tools/get_croissant_record?doi=10.18710/CHMWOB'` → returns JSON-LD
- Local clutter: `git clean -ndX` to preview ignored files; `git clean -fdX` to remove
- Secrets hygiene: ensure no real tokens in repo; keep using environment variables

## Restarting Next Session

- If container is running with auto-restart: visit `http://localhost:8000/status`
- If not running: `docker run -d --name mcp-dataverse -p 8000:8000 mcp-dataverse:dev`
- Pull latest: `git checkout main && git pull --ff-only`

