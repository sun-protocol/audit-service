# Installation Guide (Docker)

## Prerequisites

- Docker and Docker Compose installed
- An Anthropic API key or Claude Code subscription token

## 1. Configure Environment

Copy the example env file and fill in the values:

```bash
cp .env.example .env
```

**Claude authentication** (configure one):

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key (option 1) |
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code subscription token (option 2) |

To generate a `CLAUDE_CODE_OAUTH_TOKEN` (requires a Claude subscription):

```bash
claude setup-token
```

**Service authentication** (optional):

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated API keys for client auth. Leave empty to disable. | |
| `CLAUDE_MODEL` | Claude model to use | `claude-sonnet-4-6` |
| `MAX_UPLOAD_SIZE` | Max upload size in bytes | `52428800` (50MB) |

Generate API keys with:

```bash
python tools/gen_api_key.py       # generate 1 key
python tools/gen_api_key.py 5     # generate 5 keys
```

## 2. Build Image

```bash
docker compose build
```

The image includes:
- Python 3.11 + FastAPI / Uvicorn
- Node.js 20 + Claude Code CLI
- Slither and Mythril (Solidity analysis tools)

## 3. Prepare Reports Directory

Reports are persisted via a volume mount to the local `reports/` directory. Create it if it doesn't exist:

```bash
mkdir -p reports
```

## 4. Start Service

```bash
docker compose up -d
```

The service will be available at `http://localhost:8000`.

To rebuild and restart after code or skill changes:

```bash
docker compose up --build -d
```

## 5. Verify

Check the service is running:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f audit-service
```

Browse reports at `http://localhost:8000/reports/`.

## 6. Stop Service

```bash
docker compose down
```
