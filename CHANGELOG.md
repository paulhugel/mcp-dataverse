# Changelog

This project follows a simple, explicit change‑tracking process. Every change is recorded here with date, scope, and rationale. Edits proceed only with explicit approval from the maintainer.

Conventions
- Entries grouped by date (HST). Keep bullets concise and actionable.
- Categories: Added, Changed, Fixed, Docs, Process.
- Reference files by path; larger diffs live in Git history.

## Unreleased
- Placeholder for next approved changes.

## 2025-09-05 (HST)

Context
- Shift to Docker‑first local workflow via VS Code Docker extension due to hosted MCP client‑compat issue.
- Record initial local code adjustments made to improve MCP compliance and stability.

Changed
- semantic_croissant/server.py: Rename internal helper `datatool(...)` → `process_datatool(...)` to avoid name collision with MCP tool handler and accidental recursion; update call sites.
- semantic_croissant/server.py: Tool handlers return MCP content lists (e.g., `TextContent` with `mimeType`) instead of raw dicts/strings (`fetch`, `get_croissant_record`, `datatool`).
- semantic_croissant/server.py: Tool definitions in `list_tools()` use only MCP‑spec fields; HTTP endpoint mapping is exposed only via `/tools` JSON for manual browsing.
- semantic_croissant/server.py: Add `import os` for overview endpoints using `os.environ`.
- semantic_croissant/__main__.py: Use relative import (`from .server import main`) so `python -m semantic_croissant` works.

Docs
- proposed_Codex_mcp-dataverse_plan.md: Update timeline (Fri Sep 5, 2025 HST), adopt Docker‑first workflow, and note the above code changes.

Process
- Establish approval protocol: No further edits without explicit “APPROVED” from maintainer; each change documented in this changelog.

