# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A FastAPI service that accepts zip archives of source code, runs a Claude Code SDK-powered audit agent against them using configurable "skills", and produces HTML audit reports. The audit prompt is in Chinese.

## Commands

```bash
# Install
pip install -e ".[dev]"

# Run server
uvicorn src.audit_service.main:app --reload

# Tests
pytest tests/ -v
pytest tests/test_api.py::test_audit_success -v  # single test

# Lint
ruff check src/ tests/
ruff format --check src/ tests/

# Format
ruff format src/ tests/
```

## Architecture

**Request flow:** `POST /audit-security/{skill}` -> validate zip + skill -> extract to `reports/<project>/<timestamp>/code/` -> `run_audit()` calls Claude Code SDK with skill's system prompt -> agent writes markdown report -> convert to HTML -> return report URL. `POST /audit-pr/{skill}` works similarly but takes `from_branch` and `to_branch` form fields, calls `run_pr_audit()` which diffs between branches and audits only changed code.

**Key modules in `src/audit_service/`:**
- `main.py` — FastAPI app with `/audit-security/{skill}`, `/audit-pr/{skill}` endpoints and `/reports/` file browser. API key auth via `X-API-Key` header (optional, controlled by `API_KEYS` env var).
- `auditor.py` — `run_audit()` calls `claude_code_sdk.query()` with `Read/Glob/Grep` tools only; `run_pr_audit()` adds `Bash` tool for git diff. Both use `bypassPermissions` mode. Auth env resolved from config.
- `skill_loader.py` — Loads skills from `skills/` directory. Each skill is a `SKILL.md` with YAML frontmatter + prompt body, plus optional `references/` and `resources/` subdirs that get injected into the system prompt.
- `config.py` — `pydantic-settings` config from `.env`. Two auth modes: `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`.
- `html_converter.py` — Converts markdown reports to styled standalone HTML using `markdown2`.

**Skills system:** Skills live in `skills/<name>/SKILL.md`. Frontmatter defines `name`, `description`, `report_path` (default: `.audit/Audit-Report.md`). The agent writes its report to `report_path` inside the code dir; if not found, falls back to raw agent output.

**Reports:** Saved to `reports/<project_name>/<timestamp>/` containing `upload.zip`, `code/`, and `audit-report.html`. The `/reports/` endpoint serves a browsable directory listing.

## Testing Notes

- Tests use `httpx.AsyncClient` with `ASGITransport` for async FastAPI testing
- `pytest-asyncio` with `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio` decorator (but existing tests use it)
- Claude Code SDK calls are mocked in tests via `patch("src.audit_service.auditor.query")`
- Skills are mocked via `patch("src.audit_service.main._cached_skills")`

## Config

- Python 3.11+, ruff line-length 100, lint rules: E, F, I, W
- Build system: hatchling
