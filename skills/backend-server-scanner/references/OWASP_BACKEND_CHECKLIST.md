# OWASP Backend Security Checklist

> Universal security checklist for backend server applications, independent of language or framework.
> **Primary Use:** Phase 3 (Security Audit) — check these items alongside language-specific checklists.
> **Reference:** OWASP Top 10 (2021), OWASP ASVS, CWE Top 25.

---

## A01:2021 — Broken Access Control

### Authentication
- [ ] All API endpoints require authentication (except public endpoints explicitly documented)
- [ ] Login endpoint has brute-force protection (rate limiting, account lockout, CAPTCHA)
- [ ] Password stored using strong adaptive hashing (bcrypt, scrypt, Argon2) with salt
- [ ] Password policy enforces minimum complexity (length ≥ 12, no common passwords)
- [ ] Multi-factor authentication available for sensitive operations
- [ ] Session/token invalidated on logout
- [ ] Session/token invalidated on password change
- [ ] "Forgot password" flow does not reveal whether account exists (timing-safe)
- [ ] Re-authentication required for sensitive operations (password change, email change, financial)

### Authorization
- [ ] Every API endpoint enforces authorization checks (not just authentication)
- [ ] Server-side authorization — never rely on client-side role checks
- [ ] Default deny: resources inaccessible unless explicitly allowed
- [ ] IDOR protection: resource access verified against authenticated user's ownership/role
- [ ] Vertical privilege escalation prevented: users cannot access admin endpoints
- [ ] Horizontal privilege escalation prevented: users cannot access other users' resources
- [ ] API endpoints for admin/management are separated and protected
- [ ] Consistent authorization logic across all code paths (no bypass through alternative routes)

### Session Management
- [ ] Session tokens are cryptographically random (≥ 128 bits entropy)
- [ ] Session tokens transmitted only over HTTPS
- [ ] Session tokens not in URL parameters
- [ ] Session timeout configured (idle timeout + absolute timeout)
- [ ] Session fixation prevented (new session ID on login)
- [ ] Concurrent session control if required by business logic

---

## A02:2021 — Cryptographic Failures

### Data Protection
- [ ] Sensitive data identified and classified (PII, credentials, financial, health)
- [ ] Sensitive data encrypted at rest (database encryption, file encryption)
- [ ] Sensitive data encrypted in transit (TLS 1.2+ enforced, HSTS)
- [ ] Sensitive data not cached unnecessarily (Cache-Control: no-store)
- [ ] Sensitive data not logged (passwords, tokens, PII not in log files)
- [ ] Sensitive data not exposed in error messages or stack traces
- [ ] Sensitive data not returned in API responses unless necessary (data minimization)

### Cryptography
- [ ] No deprecated algorithms (MD5, SHA1 for security, DES, RC4)
- [ ] Strong encryption for sensitive data (AES-256-GCM or ChaCha20-Poly1305)
- [ ] Proper key management (keys not hardcoded, rotation policy, secure storage)
- [ ] Cryptographic random number generator used (not Math.random / java.util.Random)
- [ ] TLS certificates valid and properly configured
- [ ] No self-signed certificates in production

---

## A03:2021 — Injection

### SQL Injection
- [ ] All database queries use parameterized queries / prepared statements
- [ ] ORM used correctly (no raw query concatenation)
- [ ] Dynamic query construction (sorting, filtering) uses allowlists
- [ ] Stored procedures do not use dynamic SQL with user input
- [ ] Database user has minimal privileges (no DROP, no GRANT)

### Command Injection
- [ ] No system shell calls with user input
- [ ] If shell calls necessary: use array-based APIs (not string concatenation)
- [ ] User input validated and sanitized before use in commands
- [ ] Process execution uses minimal privileges

### Other Injection
- [ ] LDAP injection prevented (parameterized LDAP queries)
- [ ] Template injection prevented (user input not in template expressions)
- [ ] XPath injection prevented (parameterized queries)
- [ ] XML External Entity (XXE) prevented (external entity processing disabled)
- [ ] Server-Side Template Injection (SSTI) prevented
- [ ] Expression Language (EL) injection prevented

---

## A04:2021 — Insecure Design

### Input Validation
- [ ] All external input validated on server side (never trust client validation alone)
- [ ] Input validation uses allowlists (not blocklists) where possible
- [ ] Input type validation: expected data types enforced
- [ ] Input length validation: maximum length enforced
- [ ] Input range validation: numeric ranges enforced
- [ ] Input format validation: regex or schema validation for structured data
- [ ] File upload validation: file type, size, content verified (not just extension)
- [ ] Uploaded files stored outside web root, served through controlled endpoint

### Business Logic
- [ ] Business logic enforced server-side (not client-side)
- [ ] Race conditions prevented on concurrent operations (database locks, optimistic locking)
- [ ] Idempotency ensured for operations that should not be repeated
- [ ] Transaction integrity maintained (ACID compliance for critical operations)
- [ ] Workflow sequence enforced (cannot skip steps)

### Mass Assignment
- [ ] Object binding from request restricted to allowed fields only (DTO pattern or allowlist)
- [ ] Admin-only fields (role, isAdmin, balance) cannot be set via API by normal users
- [ ] Nested object binding restricted

---

## A05:2021 — Security Misconfiguration

### Server Configuration
- [ ] Debug mode disabled in production
- [ ] Default credentials changed or removed
- [ ] Unnecessary features/endpoints disabled (admin panels, test endpoints)
- [ ] Directory listing disabled
- [ ] Server version information hidden (Server header, X-Powered-By removed)
- [ ] Unnecessary HTTP methods disabled (TRACE, OPTIONS if not needed)

### HTTP Security Headers
- [ ] `Strict-Transport-Security` (HSTS) set with adequate max-age
- [ ] `Content-Security-Policy` (CSP) configured if serving HTML
- [ ] `X-Content-Type-Options: nosniff` set
- [ ] `X-Frame-Options: DENY` or `SAMEORIGIN` set
- [ ] `Referrer-Policy` configured appropriately
- [ ] `Permissions-Policy` configured to restrict browser features

### CORS
- [ ] CORS origin not set to wildcard `*` for authenticated endpoints
- [ ] CORS origin validated against allowlist
- [ ] CORS credentials (`Access-Control-Allow-Credentials`) not enabled with wildcard origin
- [ ] CORS methods and headers restricted to necessary values

### CSRF
- [ ] CSRF protection enabled for state-changing operations (POST, PUT, DELETE)
- [ ] CSRF token is per-session and unpredictable
- [ ] SameSite cookie attribute set (Lax or Strict)

---

## A06:2021 — Vulnerable & Outdated Components

### Dependency Management
- [ ] All dependencies listed with specific versions (no floating versions)
- [ ] No known critical/high CVEs in dependencies
- [ ] Automated dependency vulnerability scanning in CI/CD
- [ ] Dependencies regularly updated (within supported version ranges)
- [ ] Unused dependencies removed
- [ ] Dependencies from trusted sources only (official repositories)

---

## A07:2021 — Identification & Authentication Failures

### Token Security (JWT / API Keys)
- [ ] JWT signed with strong algorithm (RS256 or ES256, not HS256 with weak secret)
- [ ] JWT `alg: none` not accepted
- [ ] JWT expiration (`exp`) enforced and reasonable
- [ ] JWT audience (`aud`) and issuer (`iss`) validated
- [ ] API keys not embedded in URLs (use headers)
- [ ] API keys have appropriate scope and expiration
- [ ] Token revocation mechanism exists

### Credential Handling
- [ ] Credentials never logged
- [ ] Credentials never included in URL parameters
- [ ] Credentials never stored in plain text
- [ ] Credentials never transmitted in plain text (always HTTPS)
- [ ] Credentials never included in API responses

---

## A08:2021 — Software & Data Integrity Failures

### Deserialization
- [ ] Untrusted data never deserialized with unsafe deserializers
- [ ] JSON used instead of binary serialization formats where possible
- [ ] If binary deserialization needed: strict type allowlists enforced
- [ ] Deserialized data validated before use

### CI/CD Security
- [ ] CI/CD pipeline has integrity checks (signed commits, protected branches)
- [ ] Build artifacts verified (checksums, signatures)
- [ ] Environment variables for secrets (not hardcoded in pipeline config)

---

## A09:2021 — Security Logging & Monitoring

### Logging
- [ ] Authentication events logged (login success/failure, logout, password change)
- [ ] Authorization failures logged (access denied)
- [ ] Input validation failures logged
- [ ] Server errors logged with sufficient context
- [ ] Sensitive data NOT logged (passwords, tokens, credit cards, PII)
- [ ] Log injection prevented (user input sanitized before logging)
- [ ] Logs stored securely, tamper-protected
- [ ] Logs have sufficient retention period

### Monitoring & Alerting
- [ ] Alerting on repeated authentication failures (potential brute force)
- [ ] Alerting on unusual access patterns (potential scraping, enumeration)
- [ ] Alerting on critical errors (potential exploitation)
- [ ] Health check endpoints available for monitoring

---

## A10:2021 — Server-Side Request Forgery (SSRF)

- [ ] User-supplied URLs validated against allowlist of allowed domains/IPs
- [ ] Internal network addresses blocked (127.0.0.1, 10.x, 172.16-31.x, 192.168.x, metadata endpoints)
- [ ] URL scheme restricted (only http/https, no file://, gopher://, etc.)
- [ ] Redirect following disabled or limited for server-side HTTP clients
- [ ] DNS rebinding protection (resolve hostname and validate IP before connection)
- [ ] Cloud metadata endpoints blocked (169.254.169.254, metadata.google.internal, etc.)

---

## Additional Backend-Specific Checks

### Rate Limiting & DoS Protection
- [ ] Rate limiting on authentication endpoints (login, register, password reset)
- [ ] Rate limiting on resource-intensive endpoints
- [ ] Request size limits configured (body, headers, URL length)
- [ ] Pagination enforced on list endpoints (no unbounded queries)
- [ ] Query complexity limits for GraphQL (if applicable)
- [ ] File upload size limits enforced

### API Security
- [ ] API versioning strategy in place
- [ ] API documentation does not expose internal implementation details
- [ ] Deprecated endpoints properly handled (return 410 or redirect)
- [ ] Content-Type validation (accept only expected content types)
- [ ] Response content type set correctly (application/json, not text/html for APIs)

### Database Security
- [ ] Database connection uses TLS
- [ ] Database credentials not hardcoded
- [ ] Database user has least-privilege permissions
- [ ] Connection pooling configured properly (no connection leaks)
- [ ] Sensitive data in database encrypted at column level where appropriate

### Environment & Secrets
- [ ] No secrets in source code (API keys, passwords, tokens)
- [ ] No secrets in version control history
- [ ] Environment-specific configuration separated (dev/staging/production)
- [ ] Production configuration not accessible from development environments
- [ ] `.env` files not served by web server, included in `.gitignore`

---

*Based on OWASP Top 10 (2021), OWASP ASVS v4.0, CWE Top 25 (2023)*
