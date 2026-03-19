# GitHub Integration

Integrate the audit service into your GitHub workflow to automatically audit code on pull requests or manual triggers.

### Security Audit on Pull Request

Create `.github/workflows/audit-security.yml` in the target repository:

```yaml
name: Security Audit

on:
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  pull-requests: write

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
          REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
          STATUS_URL=$(echo "$RESPONSE" | jq -r '.status_url // empty')
          if [ -z "$REPORT_URL" ]; then
            echo "Audit submission failed: $RESPONSE"
            exit 1
          fi
          echo "report_url=$REPORT_URL" >> "$GITHUB_OUTPUT"
          echo "status_url=$STATUS_URL" >> "$GITHUB_OUTPUT"

      - name: Comment PR with audit links
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const baseUrl = `${{ vars.AUDIT_SERVICE_URL }}`;
            const reportUrl = `${baseUrl}${{ steps.audit.outputs.report_url }}`;
            const statusUrl = `${baseUrl}${{ steps.audit.outputs.status_url }}`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## Security Audit Submitted\n\nAudit is running in the background.\n\n- [Check Status](${statusUrl})\n- [View Report](${reportUrl}) (available when completed)`
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

permissions:
  pull-requests: write

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
          REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
          STATUS_URL=$(echo "$RESPONSE" | jq -r '.status_url // empty')
          if [ -z "$REPORT_URL" ]; then
            echo "PR audit submission failed: $RESPONSE"
            exit 1
          fi
          echo "report_url=$REPORT_URL" >> "$GITHUB_OUTPUT"
          echo "status_url=$STATUS_URL" >> "$GITHUB_OUTPUT"

      - name: Comment PR with audit links
        uses: actions/github-script@v7
        with:
          script: |
            const baseUrl = `${{ vars.AUDIT_SERVICE_URL }}`;
            const reportUrl = `${baseUrl}${{ steps.audit.outputs.report_url }}`;
            const statusUrl = `${baseUrl}${{ steps.audit.outputs.status_url }}`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## PR Code Review Submitted\n\nReview is running in the background.\n\n- [Check Status](${statusUrl})\n- [View Report](${reportUrl}) (available when completed)`
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

## Network Requirements

The audit service must be accessible from GitHub Actions runners. The service must have a public URL or be reachable via a tunnel (e.g., Cloudflare Tunnel, ngrok).
