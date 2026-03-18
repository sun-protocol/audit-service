# GitHub Integration

Integrate the audit service into your GitHub workflow to automatically audit code on pull requests or manual triggers.

## Option 1: GitHub Actions

Add a workflow file to your repository to trigger audits automatically.

### Auto Audit on Pull Request

Create `.github/workflows/audit.yml` in the target repository:

```yaml
name: Code Audit

on:
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Package source code
        run: |
          zip -r code.zip . -x '.git/*' 'node_modules/*' '.venv/*'

      - name: Run audit
        id: audit
        run: |
          RESPONSE=$(curl -s -X POST "${{ vars.AUDIT_SERVICE_URL }}/audit/${{ vars.AUDIT_SKILL }}" \
            -H "X-API-Key: ${{ secrets.AUDIT_API_KEY }}" \
            -F "file=@code.zip")
          echo "response=$RESPONSE" >> "$GITHUB_OUTPUT"
          REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
          if [ -z "$REPORT_URL" ]; then
            echo "Audit failed: $RESPONSE"
            exit 1
          fi
          echo "report_url=$REPORT_URL" >> "$GITHUB_OUTPUT"

      - name: Comment PR with report link
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const reportUrl = `${{ vars.AUDIT_SERVICE_URL }}${{ steps.audit.outputs.report_url }}`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## Audit Report\n\nAudit completed. [View Report](${reportUrl})`
            });
```

### Required Configuration

In your repository **Settings > Secrets and variables > Actions**:

**Secrets:**

| Name | Value |
|------|-------|
| `AUDIT_API_KEY` | Your audit service API key |

**Variables:**

| Name | Value | Example |
|------|-------|---------|
| `AUDIT_SERVICE_URL` | Audit service base URL | `https://audit.example.com` |
| `AUDIT_SKILL` | Skill to use for audit | `smart-contract-audit` |

## Option 2: GitHub Webhooks

Configure a webhook to trigger audits when code is pushed or a PR is opened. This requires adding a webhook handler to the audit service.

### Setup

1. Go to your repository **Settings > Webhooks > Add webhook**

2. Configure the webhook:

| Field | Value |
|-------|-------|
| Payload URL | `https://audit.example.com/webhook/github` |
| Content type | `application/json` |
| Secret | A shared secret for signature verification |
| Events | Select "Pull requests" |

3. Add the webhook secret to your audit service `.env`:

```
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

### Webhook Flow

```
GitHub PR opened/updated
  → POST /webhook/github (with event payload)
  → Service downloads code via GitHub API
  → Runs audit
  → Posts report link as PR comment via GitHub API
```

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_WEBHOOK_SECRET` | Webhook signature verification secret |
| `GITHUB_TOKEN` | GitHub personal access token (for downloading code and posting comments) |

## Option 3: GitHub App

For organization-wide deployment, create a GitHub App that can be installed on multiple repositories.

### Advantages over Webhooks

- Fine-grained permissions per repository
- No need for personal access tokens
- Installation UI in GitHub Marketplace
- Automatic token refresh

### Setup Overview

1. Create a GitHub App at **Settings > Developer settings > GitHub Apps**
2. Set permissions: `Pull requests: Read & write`, `Contents: Read`
3. Subscribe to events: `Pull request`
4. Set webhook URL to `https://audit.example.com/webhook/github-app`
5. Install the app on target repositories

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_APP_ID` | GitHub App ID |
| `GITHUB_APP_PRIVATE_KEY` | App private key (PEM format) |
| `GITHUB_WEBHOOK_SECRET` | Webhook signature verification secret |

## Network Requirements

The audit service must be accessible from GitHub Actions runners or GitHub's webhook IPs:

- **GitHub Actions**: Runners make outbound requests to your service. The service must have a public URL or be reachable via a tunnel (e.g., Cloudflare Tunnel, ngrok).
- **Webhooks / App**: GitHub sends POST requests to your service. See [GitHub's IP ranges](https://api.github.com/meta) for allowlisting.
