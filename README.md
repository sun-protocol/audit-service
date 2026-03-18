# Code Audit Service

A code audit service powered by the Claude Code SDK. Upload a zip archive of source code, specify an audit skill, and receive an HTML audit report.

## Prerequisites

- Python 3.11+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Service API keys for client auth (comma-separated). Leave empty to disable. | |
| `ANTHROPIC_API_KEY` | Anthropic API key (option 1) | |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code subscription token (option 2) | |
| `SKILLS_DIR` | Path to skills directory | `./skills` |
| `CLAUDE_MODEL` | Claude model to use | `claude-sonnet-4-6` |
| `MAX_UPLOAD_SIZE` | Max upload size in bytes | `52428800` (50MB) |

### Authentication

**Claude authentication** (configure one):
- `ANTHROPIC_API_KEY` — use an Anthropic API key directly
- `CLAUDE_CODE_OAUTH_TOKEN` — use a Claude Code subscription token

To generate a `CLAUDE_CODE_OAUTH_TOKEN` (requires a Claude subscription):

```bash
claude setup-token
```

This opens the browser for OAuth authorization and generates a long-lived token. Copy it to `.env`:

```
CLAUDE_CODE_OAUTH_TOKEN=your-token-here
```

**Service authentication** (optional):
- `API_KEYS` — comma-separated list of valid API keys for clients calling the audit endpoints
- Generate keys with: `python tools/gen_api_key.py`
- When `API_KEYS` is empty, the audit endpoints are open (no auth required)

## Running

```bash
uvicorn src.audit_service.main:app --host 0.0.0.0 --port 8000
```

Development mode (hot reload):

```bash
uvicorn src.audit_service.main:app --reload
```

### Docker

Make sure `.env` is configured (see [Configuration](#configuration)), then:

```bash
docker compose up --build        # foreground
docker compose up --build -d     # detached (background)
```

The service will be available at `http://localhost:8000`. The reports directory is mounted as a volume so reports persist across restarts. Skills are baked into the image — rebuild to update them.

## API

### POST /audit-security/{skill}

Upload a zip archive and submit a full security audit with the specified skill. The audit runs asynchronously in the background — the endpoint returns immediately with a `status_url` to poll for completion.

**Path parameter:**

| Parameter | Description |
|-----------|-------------|
| `skill` | Skill name (directory name under `skills/`) |

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | file | Zip archive of source code |

**Headers:**

| Header | Description |
|--------|-------------|
| `X-API-Key` | Service API key (required when `API_KEYS` is configured) |

**Example:**

```bash
curl -X POST http://localhost:8000/audit-security/smart-contract-audit \
  -H "X-API-Key: ask-xxxxx" \
  -F "file=@code.zip"
```

**Response:** `application/json`

```json
{
  "report_url": "/reports/code/security/20260318-150000/audit-report.html",
  "status_url": "/audit-status/code/security/20260318-150000/audit-report.html",
  "status": "processing"
}
```

| Status | Description |
|--------|-------------|
| 200 | Audit submitted, returns report URL and status URL |
| 400 | Invalid skill / invalid zip / file too large |
| 401 | Invalid or missing API key |

### POST /audit-pr/{skill}

Upload a zip archive (with `.git` history) and audit only the changes between two branches. The audit runs asynchronously in the background.

**Path parameter:**

| Parameter | Description |
|-----------|-------------|
| `skill` | Skill name (directory name under `skills/`) |

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | file | Zip archive of source code (must include `.git` directory) |
| `from_branch` | string | Target branch, e.g. `main` |
| `to_branch` | string | Source branch, e.g. `feature/xxx` |

**Headers:**

| Header | Description |
|--------|-------------|
| `X-API-Key` | Service API key (required when `API_KEYS` is configured) |

**Example:**

```bash
curl -X POST http://localhost:8000/audit-pr/code-review \
  -H "X-API-Key: ask-xxxxx" \
  -F "file=@code.zip" \
  -F "from_branch=main" \
  -F "to_branch=feature/new-token"
```

**Response:** `application/json`

```json
{
  "report_url": "/reports/code/pr/20260318-150000/audit-report.html",
  "status_url": "/audit-status/code/pr/20260318-150000/audit-report.html",
  "status": "processing"
}
```

| Status | Description |
|--------|-------------|
| 200 | Audit submitted, returns report URL and status URL |
| 400 | Invalid skill / invalid zip / file too large / missing `.git` / missing branch params |
| 401 | Invalid or missing API key |
| 422 | Missing required form fields |

### GET /audit-status/{path}

Poll the status of a submitted audit.

**Example:**

```bash
curl http://localhost:8000/audit-status/code/security/20260318-150000/audit-report.html
```

**Response:**

```json
{"status": "pending"}
```

or when complete:

```json
{"status": "completed", "report_url": "/reports/code/security/20260318-150000/audit-report.html"}
```

### GET /reports/{path}

Browse audit reports. Navigate directories and view generated HTML reports directly in the browser.

- `GET /` redirects to `/reports/`
- `GET /reports/` lists all projects
- `GET /reports/{project}/security/{timestamp}/audit-report.html` serves security audit report
- `GET /reports/{project}/pr/{timestamp}/audit-report.html` serves PR audit report

## Skills

Each skill is a directory under `skills/`:

```
skills/
├── backend-server-scanner/
│   ├── SKILL.md                # Skill definition (YAML frontmatter + prompt)
│   ├── references/             # Reference docs (injected into system prompt)
│   │   └── OWASP_BACKEND_CHECKLIST.md
│   ├── resources/              # Templates and checklists
│   │   └── audit_report_template.md
│   └── plugins/                # Optional plugins
│       └── java/
├── code-review/                # PR code review skill
│   ├── SKILL.md
│   ├── references/
│   │   └── CODE_REVIEW_CHECKLIST.md
│   └── resources/
│       └── review_report_template.md
└── smart-contract-audit/
    ├── SKILL.md
    ├── references/
    │   ├── DEFI_CHECKLIST.md
    │   └── VULNERABILITY_PATTERNS.md
    └── resources/
        └── audit_report_template.md
```

### SKILL.md format

```markdown
---
name: smart-contract-audit
description: DeFi smart contract security audit
report_path: .audit/Audit-Report.md   # optional, default: .audit/Audit-Report.md
---

You are a senior security auditor. Perform a comprehensive audit...
```

| Frontmatter field | Description | Default |
|-------------------|-------------|---------|
| `name` | Display name | Directory name |
| `description` | Short description | |
| `report_path` | Path where the agent writes its report (relative to code dir) | `.audit/Audit-Report.md` |

Legacy single-file format (`skills/my-skill.md`) is also supported but directory format is recommended.

## Tools

### Generate API keys

```bash
python tools/gen_api_key.py       # generate 1 key
python tools/gen_api_key.py 5     # generate 5 keys
```

### Convert Markdown to HTML

```bash
python tools/md2html.py report.md              # outputs report.html
python tools/md2html.py report.md output.html   # custom output path
```

## Reports

Audit reports are saved under `reports/<project_name>/<type>/<timestamp>/`:

```
reports/
└── my-project/
    ├── security/                   # Security audit reports
    │   └── 20260318-131955/
    │       ├── audit-report.html   # HTML report
    │       ├── upload.zip          # Original uploaded archive
    │       └── code/               # Extracted source code
    └── pr/                         # PR code review reports
        └── 20260318-180005/
            ├── audit-report.html
            ├── upload.zip
            └── code/
```

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
audit-service/
├── src/audit_service/
│   ├── main.py              # FastAPI app, /audit-security + /audit-pr endpoints, report browser
│   ├── auditor.py           # Claude Code SDK audit execution
│   ├── auth.py              # Claude auth env resolution
│   ├── config.py            # Settings (pydantic-settings)
│   ├── skill_loader.py      # Parse skills directory
│   └── html_converter.py    # Markdown to HTML conversion
├── skills/                  # Audit skill definitions
├── reports/                 # Generated audit reports
├── tools/                   # CLI utilities
│   ├── gen_api_key.py       # API key generator
│   └── md2html.py           # Markdown to HTML converter
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```
