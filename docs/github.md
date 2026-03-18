# GitHub Integration

Integrate the audit service into your GitHub workflow to automatically audit code on pull requests or manual triggers.

## Option 1: GitHub Actions

Add a workflow file to your repository to trigger audits automatically.

### Security Audit on Pull Request

Create `.github/workflows/audit-security.yml` in the target repository:

```yaml
name: Security Audit

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

      - name: Submit audit
        id: audit
        run: |
          RESPONSE=$(curl -s -X POST "${{ vars.AUDIT_SERVICE_URL }}/audit-security/${{ vars.AUDIT_SECURITY_SKILL }}" \
            -H "X-API-Key: ${{ secrets.AUDIT_API_KEY }}" \
            -F "file=@code.zip")
          echo "response=$RESPONSE" >> "$GITHUB_OUTPUT"
          STATUS_URL=$(echo "$RESPONSE" | jq -r '.status_url // empty')
          REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
          if [ -z "$STATUS_URL" ]; then
            echo "Audit submission failed: $RESPONSE"
            exit 1
          fi
          echo "status_url=$STATUS_URL" >> "$GITHUB_OUTPUT"
          echo "report_url=$REPORT_URL" >> "$GITHUB_OUTPUT"

      - name: Wait for audit to complete
        id: wait
        run: |
          STATUS_URL="${{ vars.AUDIT_SERVICE_URL }}${{ steps.audit.outputs.status_url }}"
          for i in $(seq 1 60); do
            STATUS=$(curl -s "$STATUS_URL" | jq -r '.status')
            if [ "$STATUS" = "completed" ]; then
              echo "Audit completed"
              exit 0
            fi
            echo "Attempt $i: status=$STATUS, waiting 30s..."
            sleep 30
          done
          echo "Audit timed out after 30 minutes"
          exit 1

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
              body: `## Security Audit Report\n\nAudit completed. [View Report](${reportUrl})`
            });
```

### PR Code Review on Pull Request

Create `.github/workflows/audit-pr.yml` in the target repository.
This packages the code **with .git history** so the audit agent can `git diff` between branches.

```yaml
name: PR Code Review

on:
  pull_request:
    branches: [main]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code (with full history)
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Package source code (including .git)
        run: |
          zip -r code.zip . -x 'node_modules/*' '.venv/*'

      - name: Submit PR audit
        id: audit
        run: |
          RESPONSE=$(curl -s -X POST "${{ vars.AUDIT_SERVICE_URL }}/audit-pr/${{ vars.AUDIT_PR_SKILL }}" \
            -H "X-API-Key: ${{ secrets.AUDIT_API_KEY }}" \
            -F "file=@code.zip" \
            -F "from_branch=${{ github.base_ref }}" \
            -F "to_branch=${{ github.head_ref }}")
          echo "response=$RESPONSE" >> "$GITHUB_OUTPUT"
          STATUS_URL=$(echo "$RESPONSE" | jq -r '.status_url // empty')
          REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
          if [ -z "$STATUS_URL" ]; then
            echo "PR audit submission failed: $RESPONSE"
            exit 1
          fi
          echo "status_url=$STATUS_URL" >> "$GITHUB_OUTPUT"
          echo "report_url=$REPORT_URL" >> "$GITHUB_OUTPUT"

      - name: Wait for audit to complete
        id: wait
        run: |
          STATUS_URL="${{ vars.AUDIT_SERVICE_URL }}${{ steps.audit.outputs.status_url }}"
          for i in $(seq 1 60); do
            STATUS=$(curl -s "$STATUS_URL" | jq -r '.status')
            if [ "$STATUS" = "completed" ]; then
              echo "PR audit completed"
              exit 0
            fi
            echo "Attempt $i: status=$STATUS, waiting 30s..."
            sleep 30
          done
          echo "PR audit timed out after 30 minutes"
          exit 1

      - name: Comment PR with report link
        uses: actions/github-script@v7
        with:
          script: |
            const reportUrl = `${{ vars.AUDIT_SERVICE_URL }}${{ steps.audit.outputs.report_url }}`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## PR Code Review Report\n\nReview completed. [View Report](${reportUrl})`
            });
```

**Key differences from security audit:**
- `fetch-depth: 0` — fetches full git history (required for `git diff`)
- `.git` is **included** in the zip (not excluded)
- `from_branch` and `to_branch` are passed as form fields, using `github.base_ref` and `github.head_ref`

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
| `AUDIT_SECURITY_SKILL` | Skill for security audit | `smart-contract-audit` |
| `AUDIT_PR_SKILL` | Skill for PR code review | `code-review` |

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
