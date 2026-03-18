# Backend Server Security Audit Report

**Project:** {{PROJECT_NAME}}
**Language / Framework:** {{LANGUAGE}} / {{FRAMEWORK}}
**Audit Date:** {{DATE}}
**Auditor:** AI Security Auditor (Backend Server Security Audit Skill v2.0.0)

---

## Executive Summary

### Risk Level

> **Overall Risk:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

### Findings at a Glance

| | Critical | High | Medium | Low | Info |
|---|:---:|:---:|:---:|:---:|:---:|
| **Count** | 0 | 0 | 0 | 0 | 0 |

### Risk Score

```
╔══════════════════════════════════════════════════════════╗
║  Risk Score:  ██████████░░░░░░░░░░  XX / 100            ║
║                                                          ║
║  Critical ████████  N findings                           ║
║  High     ██████    N findings                           ║
║  Medium   ████      N findings                           ║
║  Low      ██        N findings                           ║
╚══════════════════════════════════════════════════════════╝
```

### Key Findings

> *1–3 paragraph narrative: most impactful findings, business consequences, and overall security posture.*

---

## Application Overview

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | {{LANGUAGE}} | {{VERSION}} |
| Framework | {{FRAMEWORK}} | {{FW_VERSION}} |
| Build Tool | {{BUILD_TOOL}} | — |
| Database | {{DATABASE}} | — |
| Auth | {{AUTH_MECHANISM}} | — |

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│   Client     │────▶│  Controller  │────▶│   Service    │────▶│   Repo   │
│              │     │              │     │              │     │          │
│              │◀────│              │◀────│              │◀────│          │
└─────────────┘     └──────┬───────┘     └──────────────┘     └────┬─────┘
                           │                                       │
                    ┌──────▼───────┐                        ┌──────▼─────┐
                    │   Filters /  │                        │  Database  │
                    │  Security    │                        │            │
                    └──────────────┘                        └────────────┘
```

### Files Reviewed

| File / Package | Type | Lines | Audit Focus |
|---------------|------|-------|-------------|
| [file] | [type] | — | [focus] |

### Active Plugins

| Plugin | Path | Matched By |
|--------|------|-----------|
| [name] | `plugins/[name]/` | [indicator] |

---

## Detailed Findings

> *All confirmed findings, ordered by severity.*

---

### 🔴 Critical

#### [C-01] {{Finding Title}}

| Property | Value |
|----------|-------|
| **Severity** | 🔴 Critical |
| **Location** | `{{File}}` : `{{method()}}` : Lines {{X}}–{{Y}} |
| **Endpoint** | `{{HTTP_METHOD}} {{/api/path}}` |
| **CWE** | CWE-{{XXX}} — {{CWE Name}} |
| **OWASP** | A{{XX}}:2021 — {{Category}} |

**Description**

> [Clear, concise description of the vulnerability and root cause.]

**Vulnerable Code**

```java
// [code snippet]
```

**Impact**

> [What can an attacker achieve? Be specific.]

**Exploit Scenario**

```
1. Attacker sends...
2. Application processes...
3. Attacker gains...
```

**Recommendation**

```java
// [fixed code]
```

> [Additional guidance]

---

### 🟠 High

#### [H-01] {{Finding Title}}

| Property | Value |
|----------|-------|
| **Severity** | 🟠 High |
| **Location** | `{{File}}` : `{{method()}}` : Lines {{X}}–{{Y}} |
| **Endpoint** | `{{HTTP_METHOD}} {{/api/path}}` |
| **CWE** | CWE-{{XXX}} |
| **OWASP** | A{{XX}}:2021 |

**Description**
> [Description]

**Vulnerable Code**
```java
// [code]
```

**Impact**
> [Impact]

**Recommendation**
```java
// [fix]
```

---

### 🟡 Medium

#### [M-01] {{Finding Title}}

| Property | Value |
|----------|-------|
| **Severity** | 🟡 Medium |
| **Location** | `{{File}}` : Lines {{X}}–{{Y}} |
| **CWE** | CWE-{{XXX}} |

**Description**
> [Description]

**Recommendation**
> [Recommendation]

---

### 🟢 Low

#### [L-01] {{Finding Title}}

| Property | Value |
|----------|-------|
| **Severity** | 🟢 Low |
| **Location** | `{{File}}` : Lines {{X}}–{{Y}} |

**Description**
> [Description]

**Recommendation**
> [Recommendation]

---

### ⚪ Informational

#### [I-01] {{Finding Title}}

**Location:** `{{File}}`
**Description:** [Brief description]
**Recommendation:** [Brief recommendation]

---

## Recommendations Summary

### Immediate (Fix Before Deployment)

| # | Finding | Action | Effort |
|---|---------|--------|--------|
| 1 | [C-01] | {{action}} | {{Low/Med/High}} |

### Short-term (Fix Within 1 Sprint)

| # | Finding | Action | Effort |
|---|---------|--------|--------|
| 1 | [H-01] | {{action}} | {{Low/Med/High}} |

### Medium-term (Fix Within 1 Month)

| # | Finding | Action | Effort |
|---|---------|--------|--------|
| 1 | [M-01] | {{action}} | {{Low/Med/High}} |

### Long-term (Continuous Improvement)

| # | Finding | Action | Effort |
|---|---------|--------|--------|
| 1 | [L-01] | {{action}} | {{Low/Med/High}} |

---

## Positive Findings

> *Security practices that are well-implemented.*

| Area | Observation |
|------|-------------|
| {{area}} | {{positive observation}} |

---

## Appendix

### A. OWASP Backend Checklist Results

| OWASP Category | Items Checked | ✅ Pass | ❌ Fail | ⚠️ Partial | Notes |
|----------------|:---:|:---:|:---:|:---:|-------|
| A01 Broken Access Control | — | — | — | — | |
| A02 Cryptographic Failures | — | — | — | — | |
| A03 Injection | — | — | — | — | |
| A04 Insecure Design | — | — | — | — | |
| A05 Security Misconfiguration | — | — | — | — | |
| A06 Vulnerable Components | — | — | — | — | |
| A07 Auth Failures | — | — | — | — | |
| A08 Data Integrity | — | — | — | — | |
| A09 Logging & Monitoring | — | — | — | — | |
| A10 SSRF | — | — | — | — | |
| **Total** | **—** | **—** | **—** | **—** | |

### B. Plugin Checklist Results

> *Repeat for each active plugin.*

#### Plugin: {{plugin_name}} (`plugins/{{name}}/CHECKLIST.md`)

| Section | Items Checked | ✅ Pass | ❌ Fail | ⚠️ Partial | Notes |
|---------|:---:|:---:|:---:|:---:|-------|
| [section] | — | — | — | — | |
| **Total** | **—** | **—** | **—** | **—** | |

### C. Vulnerability Pattern Verification

> *Repeat for each active plugin.*

#### Plugin: {{plugin_name}} (`plugins/{{name}}/VULNERABILITY_PATTERNS.md`)

| # | Pattern | Checked | Violations | Notes |
|---|---------|:---:|:---:|-------|
| [N] | [pattern name] | ✅ | 0 | |

### D. SAST Tool Results (if applicable)

| Tool | Findings | Critical | High | Medium | Low |
|------|:---:|:---:|:---:|:---:|:---:|
| {{tool}} | 0 | 0 | 0 | 0 | 0 |

### E. Severity Classification

| Severity | Impact | Likelihood | Examples |
|----------|--------|------------|----------|
| 🔴 **Critical** | Direct data breach, RCE | High | SQL injection, auth bypass, deserialization RCE |
| 🟠 **High** | Significant data exposure | Medium-High | IDOR, privilege escalation, SSRF |
| 🟡 **Medium** | Conditional impact | Medium | CSRF, verbose errors, missing rate limiting |
| 🟢 **Low** | Minor / defense-in-depth | Low | Missing headers, weak session config |
| ⚪ **Info** | Best practices | N/A | Code quality, deprecated APIs |

### F. Disclaimer

This audit is a point-in-time assessment. It does not guarantee the absence of vulnerabilities. This audit does **not** cover: runtime/dynamic testing, infrastructure security, frontend security, third-party service security, social engineering, or compliance certification.

---

*Report generated by Backend Server Security Audit Skill v2.0.0*
*Date: {{DATE}}*
