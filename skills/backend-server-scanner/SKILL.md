---
name: Backend Server Security Audit
description: |
  Security audit for backend server applications. Auto-detects language/framework,
  loads matching plugins, and produces a professional audit report in one pass.
version: "2.0.0"
updated: "2026-02"
---

# Backend Server Security Audit Skill

Performs a complete security audit of a backend server application in a **single continuous pass**. Auto-detects language/framework, loads all matching plugins from `plugins/`, and outputs a professional audit report.

## Skill Resources

| Resource | Path | Description |
|----------|------|-------------|
| **Audit Report Template** | `resources/audit_report_template.md` | Report structure for `.audit/Audit-Report.md` |
| **OWASP Backend Checklist** | `references/OWASP_BACKEND_CHECKLIST.md` | Universal backend security checklist |

### Plugins

| Plugin | Path | Type | Detection |
|--------|------|------|-----------|
| **Java / Spring Boot** | `plugins/java/` | Language | `pom.xml` or `build.gradle` with `.java` files |

Each plugin folder contains three files:

```
plugins/<name>/
├── SPEC.md                    ← Detection rules, SAST tools, audit focus areas
├── VULNERABILITY_PATTERNS.md  ← Vulnerable/secure code examples
└── CHECKLIST.md               ← Security checklist
```

Plugin types: **Language** (`java/`, `python/`), **Framework** (`spring-boot/`, `django/`), **Library** (`mybatis/`, `graphql/`), **Infrastructure** (`docker/`, `kubernetes/`).

Multiple plugins can be active simultaneously. Adding a new plugin = adding a new folder.

---

## Workflow

```
Trigger
  │
  ├─ Step 1: Detect & Load Plugins      ← read build files, config, load matching plugins
  ├─ Step 2: Understand the Codebase     ← read all source, map architecture & data flows
  ├─ Step 3: Security Audit              ← endpoint-based + flow-based analysis
  ├─ Step 4: (Optional) Run SAST Tools   ← semgrep, spotbugs, etc. if available
  │
  └─ Output: .audit/Audit-Report.md      ← single report, following template
```

---

## Instructions

> **CRITICAL RULES**:
> - You MUST complete steps **in order**: detect → understand → audit → report.
> - You MUST **understand the codebase before auditing**. Do NOT skip straight to pattern matching.
> - You MUST read `references/OWASP_BACKEND_CHECKLIST.md` and every active plugin's `CHECKLIST.md` + `VULNERABILITY_PATTERNS.md` before auditing.
> - Every finding MUST include: code evidence, severity, CWE/OWASP mapping, exploit scenario, and fix recommendation.
> - Only report findings you are confident about. Mark uncertain findings with ⚠️ and explain why.
> - Output the final report following `resources/audit_report_template.md` and **SAVE** to `.audit/Audit-Report.md`.

---

### Step 1: Detect & Load Plugins

1. **Identify language and framework** from build files:

   | Indicator | Language | Framework Detection |
   |-----------|----------|-------------------|
   | `pom.xml` / `build.gradle` | Java | `spring-boot-starter-*` dependencies |
   | `requirements.txt` / `pyproject.toml` | Python | `django`, `flask`, `fastapi` |
   | `go.mod` | Go | `gin`, `echo`, `fiber` |
   | `package.json` + server code | Node.js | `express`, `nestjs`, `fastify` |

2. **Load plugins**: Read each `plugins/<name>/SPEC.md`, check detection rules, activate all that match.

3. **Record**: language, framework, version, build tool, active plugins, key dependencies.

---

### Step 2: Understand the Codebase

**Read all relevant source files before auditing.** Build a mental model of:

#### Architecture & Layers
- API entry points (controllers, routes, handlers)
- Middleware / filters / interceptors pipeline
- Service / business logic layer
- Data access layer (ORM, raw queries, mappers)
- Configuration files (security config, app config, env)

#### API Surface
For every endpoint, understand: HTTP method & path, auth/authz requirements, input parameters & validation, service calls, data access, response structure, error handling.

#### Security-Critical Flows
- **Authentication**: login → token/session creation → validation → refresh → logout
- **Authorization**: request → role resolution → permission check → resource access
- **Sensitive data**: where passwords/PII/tokens enter, are processed, stored, and returned
- **Error handling**: exception → handler → response (what leaks?)

#### Configuration
- Security config (auth, CORS, CSRF, session, headers)
- Secret management (env vars, vault, config files — any hardcoded?)
- Logging config (sensitive data in logs?)

---

### Step 3: Security Audit

Using your understanding from Step 2, perform two complementary analyses. Reference these files throughout:
- `references/OWASP_BACKEND_CHECKLIST.md`
- Each active plugin's `CHECKLIST.md`
- Each active plugin's `VULNERABILITY_PATTERNS.md`

#### A. Endpoint-Based Analysis

For each API endpoint, re-read its code (controller → service → repository) and check for:

| Category | What to Look For |
|----------|-----------------|
| **Injection** | SQL injection (string concat in queries), command injection, template injection, NoSQL injection |
| **Auth/Authz** | Missing authentication, missing authorization, IDOR (no ownership check), privilege escalation |
| **Input Validation** | Missing `@Valid` / validation, no type/range/length checks, mass assignment (Entity as @RequestBody) |
| **Data Exposure** | Returning Entity instead of DTO, sensitive fields in response, verbose errors with stack traces |
| **Misconfiguration** | Debug mode, default credentials, overly permissive CORS/CSRF, exposed actuator/admin endpoints |
| **Rate Limiting** | No rate limit on login, password reset, OTP, or other sensitive endpoints |

#### B. Flow-Based Analysis

Trace each security-critical flow end-to-end and check for:

| Flow | What to Look For |
|------|-----------------|
| **Authentication** | Brute force protection, password storage (bcrypt/argon2?), session fixation, token security |
| **Authorization** | Bypass paths, inconsistent checks, default-allow vs default-deny |
| **Input Processing** | Validation completeness, sanitization before use, consistent rules across endpoints |
| **Error Handling** | Stack trace exposure, internal details leaked, generic vs specific error messages |
| **Data Access** | Parameterized queries, ORM misuse, raw query injection |
| **File Operations** | Path traversal, file type validation, upload to web root |
| **External Calls** | SSRF (user-controlled URLs), credential exposure, response validation |

#### Finding Format

For each vulnerability found:

```markdown
### [C/H/M/L/I-XX] Title

| Property | Value |
|----------|-------|
| **Severity** | 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low / ⚪ Info |
| **Location** | `File.java` : `method()` : Lines X–Y |
| **Endpoint** | `POST /api/path` |
| **CWE** | CWE-XXX |
| **OWASP** | A0X:2021 |

**Description:** [What is wrong and why it's dangerous]

**Vulnerable Code:**
​```java
[code snippet]
​```

**Exploit Scenario:**
1. [step-by-step attack]

**Impact:** [specific consequences]

**Recommendation:**
​```java
[fixed code]
​```
```

#### Severity Classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| 🔴 **Critical** | Direct data breach, RCE, full system compromise. Easy to exploit. | SQL injection with data exfil, auth bypass, deserialization RCE |
| 🟠 **High** | Significant data exposure, partial compromise. Moderate difficulty. | IDOR, privilege escalation, SSRF to internal services |
| 🟡 **Medium** | Conditional impact, requires specific setup. | CSRF, verbose errors, missing rate limiting |
| 🟢 **Low** | Minor issues, defense-in-depth. | Missing security headers, weak session config |
| ⚪ **Info** | Best practices, no direct security impact. | Code quality, deprecated APIs |

---

### Step 4: Run SAST Tools (Optional)

If automated tools are available, run them to supplement the manual audit. Refer to each active plugin's `SPEC.md` for recommended tools.

**Universal**: `semgrep --config=auto --config=p/security-audit --config=p/owasp-top-ten .`

Merge SAST findings into the report. Tag with `[AUTO]` and verify each before including.

---

### Output: Audit Report

Generate the final report following `resources/audit_report_template.md`. **SAVE** to `.audit/Audit-Report.md`.

The report must include:
1. **Executive Summary**: Overall risk level, finding counts, key findings narrative
2. **Application Overview**: Tech stack, architecture, files reviewed
3. **Detailed Findings**: All confirmed findings, ordered by severity (using format above)
4. **Recommendations Summary**: Prioritized action plan (immediate / short-term / medium-term / long-term)
5. **Positive Findings**: What the application does well
6. **Appendix**: OWASP checklist results, plugin checklist results, vulnerability pattern verification, severity classification, disclaimer

---

## Common Backend Attack Patterns (Quick Reference)

| Attack | Target | Key Indicator |
|--------|--------|---------------|
| SQL Injection | Queries with string concat | User input in SQL without parameterization |
| Command Injection | System/process calls | User input in shell commands |
| SSRF | HTTP clients | User-controlled URLs in server-side requests |
| Path Traversal | File operations | `../` in user-controlled file paths |
| IDOR | Resource access by ID | Missing ownership verification |
| Auth Bypass | Login / token validation | Logic flaws in auth flow |
| Privilege Escalation | Role-based endpoints | Missing or incorrect role checks |
| Mass Assignment | Object binding | Entity used directly as request body |
| Deserialization | ObjectInputStream | Untrusted data deserialized |
| XXE | XML parsing | External entity processing enabled |
| CSRF | State-changing endpoints | Missing CSRF token |
| Info Disclosure | Error responses | Stack traces, internal paths |

---

*Backend Server Security Audit Skill v2.0.0*
