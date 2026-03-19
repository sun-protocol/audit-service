# GitLab Integration

Integrate the audit service into your GitLab CI/CD pipeline to automatically audit code on merge requests.

## GitLab CI/CD

Add a `.gitlab-ci.yml` file to your repository to trigger audits automatically.

### Security Audit on Merge Request

```yaml
stages:
  - audit

security-audit:
  stage: audit
  image: alpine:latest
  before_script:
    - apk add --no-cache curl zip jq
  script:
    - zip -r code.zip . -x '.git/*' 'node_modules/*' '.venv/*'
    - |
      RESPONSE=$(curl -s -X POST "${AUDIT_SERVICE_URL}/audit-security/${AUDIT_SECURITY_SKILL}" \
        -H "X-API-Key: ${AUDIT_API_KEY}" \
        -F "file=@code.zip")
      echo "Response: $RESPONSE"
      REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
      STATUS_URL=$(echo "$RESPONSE" | jq -r '.status_url // empty')
      if [ -z "$REPORT_URL" ]; then
        echo "Audit submission failed: $RESPONSE"
        exit 1
      fi
      echo "Report URL: ${AUDIT_SERVICE_URL}${REPORT_URL}"
      echo "Status URL: ${AUDIT_SERVICE_URL}${STATUS_URL}"
    - |
      if [ -n "$CI_MERGE_REQUEST_IID" ]; then
        curl -s --request POST \
          --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}" \
          "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes" \
          --data-urlencode "body=## Security Audit Submitted

      Audit is running in the background.

      - [Check Status](${AUDIT_SERVICE_URL}${STATUS_URL})
      - [View Report](${AUDIT_SERVICE_URL}${REPORT_URL}) (available when completed)"
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

### PR Code Review on Merge Request

This job packages the code **with .git history** so the audit agent can `git diff` between branches.

```yaml
pr-code-review:
  stage: audit
  image: alpine:latest
  before_script:
    - apk add --no-cache curl zip jq git
  script:
    - git fetch origin ${CI_MERGE_REQUEST_TARGET_BRANCH_NAME} --depth=0 || true
    - zip -r code.zip . -x 'node_modules/*' '.venv/*'
    - |
      RESPONSE=$(curl -s -X POST "${AUDIT_SERVICE_URL}/audit-pr/${AUDIT_PR_SKILL}" \
        -H "X-API-Key: ${AUDIT_API_KEY}" \
        -F "file=@code.zip" \
        -F "from_branch=${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" \
        -F "to_branch=${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}")
      echo "Response: $RESPONSE"
      REPORT_URL=$(echo "$RESPONSE" | jq -r '.report_url // empty')
      STATUS_URL=$(echo "$RESPONSE" | jq -r '.status_url // empty')
      if [ -z "$REPORT_URL" ]; then
        echo "PR audit submission failed: $RESPONSE"
        exit 1
      fi
      echo "Report URL: ${AUDIT_SERVICE_URL}${REPORT_URL}"
      echo "Status URL: ${AUDIT_SERVICE_URL}${STATUS_URL}"
    - |
      if [ -n "$CI_MERGE_REQUEST_IID" ]; then
        curl -s --request POST \
          --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}" \
          "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests/${CI_MERGE_REQUEST_IID}/notes" \
          --data-urlencode "body=## PR Code Review Submitted

      Review is running in the background.

      - [Check Status](${AUDIT_SERVICE_URL}${STATUS_URL})
      - [View Report](${AUDIT_SERVICE_URL}${REPORT_URL}) (available when completed)"
      fi
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

**Key differences from security audit:**
- `.git` is **included** in the zip (not excluded)
- `git` package is installed in `before_script`
- `from_branch` uses `CI_MERGE_REQUEST_TARGET_BRANCH_NAME` (e.g. `main`)
- `to_branch` uses `CI_MERGE_REQUEST_SOURCE_BRANCH_NAME` (e.g. `feature/xxx`)

### Required Configuration

In your project **Settings > CI/CD > Variables**:

| Variable | Type | Masked | Description | Example |
|----------|------|--------|-------------|---------|
| `AUDIT_SERVICE_URL` | Variable | No | Audit service base URL | `https://audit.example.com` |
| `AUDIT_API_KEY` | Variable | Yes | Audit service API key | `ask-xxxxx` |
| `AUDIT_SECURITY_SKILL` | Variable | No | Skill for security audit | `smart-contract-audit` |
| `AUDIT_PR_SKILL` | Variable | No | Skill for PR code review | `code-review` |
| `GITLAB_API_TOKEN` | Variable | Yes | GitLab API token (for posting MR comments) | `glpat-xxxxx` |

**Note:** `GITLAB_API_TOKEN` needs `api` scope. You can use a project access token or personal access token. If you use `CI_JOB_TOKEN` instead, replace `PRIVATE-TOKEN` header with `JOB-TOKEN`.

### Group-Level Configuration

To share variables across multiple projects, configure them at the group level:

1. Go to **Group > Settings > CI/CD > Variables**
2. Add `AUDIT_SERVICE_URL`, `AUDIT_API_KEY`, and skill variables
3. Each project inherits these variables and only needs the `.gitlab-ci.yml`

## Network Requirements

The audit service must be accessible from GitLab CI runners:

- **GitLab.com shared runners**: The service must have a public URL or be reachable via a tunnel (e.g., Cloudflare Tunnel, ngrok)
- **Self-hosted runners**: Ensure network connectivity between runners and the audit service
- **GitLab self-managed**: If both GitLab and the audit service are on the same network, use internal URLs
