# Spring Boot Security Checklist

> Framework-specific security checklist for Java Spring Boot applications.
> **Primary Use:** Phase 3 (Security Audit) — check alongside `OWASP_BACKEND_CHECKLIST.md`.
> **Reference:** Use Phase 2 (Codebase Understanding) to identify which sections apply.

---

## 🔐 Spring Security Configuration

### SecurityFilterChain (Spring Boot 3.x)
- [ ] `SecurityFilterChain` bean is defined (not relying on defaults)
- [ ] No sensitive paths (admin, actuator, internal) set to `.permitAll()`
- [ ] Default rule is `.anyRequest().authenticated()` (deny by default)
- [ ] `.requestMatchers()` patterns are specific (no overly broad patterns)
- [ ] Order of matchers is correct (most specific first, catch-all last)

### Authentication
- [ ] Password encoder uses `BCryptPasswordEncoder` or `Argon2PasswordEncoder` (not `NoOpPasswordEncoder`, not MD5/SHA)
- [ ] `UserDetailsService` properly implemented (no hardcoded users in production)
- [ ] Login endpoint has rate limiting / brute-force protection
- [ ] Failed login does not reveal whether username or password is wrong
- [ ] Account lockout or progressive delay after repeated failures
- [ ] Default Spring Security user (`spring.security.user.*`) disabled in production

### Method-Level Security
- [ ] `@EnableMethodSecurity` (or `@EnableGlobalMethodSecurity`) enabled
- [ ] Sensitive service methods protected with `@PreAuthorize` or `@Secured`
- [ ] Authorization expressions use roles/permissions, not hardcoded user checks
- [ ] `@PreAuthorize` on controller methods for fine-grained access control

---

## 🔑 Session & Token Management

### Session Security
- [ ] Session creation policy appropriate: `STATELESS` for JWT/API, `IF_REQUIRED` for web
- [ ] Session fixation protection: `.sessionFixation().newSession()` or `.migrateSession()`
- [ ] Concurrent session control configured if needed
- [ ] Session timeout configured (`server.servlet.session.timeout`)
- [ ] Session cookie flags: `Secure`, `HttpOnly`, `SameSite=Lax/Strict`

### JWT Security (if applicable)
- [ ] JWT signed with strong algorithm (`RS256`, `ES256`, not `HS256` with weak secret)
- [ ] `alg: none` not accepted by JWT parser
- [ ] JWT expiration (`exp`) enforced and reasonably short
- [ ] JWT audience (`aud`) and issuer (`iss`) validated
- [ ] JWT refresh token rotation implemented
- [ ] Token revocation mechanism exists (blacklist or short-lived + refresh)
- [ ] JWT secret/key not hardcoded (from env var or key store)

---

## 🛡️ CSRF Protection

- [ ] CSRF protection enabled for session-based authentication
- [ ] CSRF token included in state-changing requests (POST, PUT, DELETE)
- [ ] CSRF token stored in `CookieCsrfTokenRepository.withHttpOnlyFalse()` for SPA
- [ ] If CSRF disabled: confirm application is API-only with token-based auth (no cookies)
- [ ] SameSite cookie attribute set to `Lax` or `Strict`

---

## 🌐 CORS Configuration

- [ ] CORS allowed origins are specific (not `*` for authenticated endpoints)
- [ ] CORS `allowCredentials(true)` NOT combined with `allowedOrigins("*")`
- [ ] CORS allowed methods restricted to necessary methods only
- [ ] CORS allowed headers restricted to necessary headers only
- [ ] CORS `maxAge` set to reasonable value (not excessively long)
- [ ] CORS configuration centralized (not scattered across controllers via `@CrossOrigin`)

---

## 📊 Actuator Security

### Endpoint Exposure
- [ ] `management.endpoints.web.exposure.include` is NOT `*` in production
- [ ] Only safe endpoints exposed: `health`, `info`, `metrics`, `prometheus`
- [ ] Sensitive endpoints disabled or protected:
  - [ ] `/actuator/env` — disabled or admin-only (exposes env vars including secrets)
  - [ ] `/actuator/configprops` — disabled or admin-only (exposes all config)
  - [ ] `/actuator/heapdump` — disabled or admin-only (exposes heap memory)
  - [ ] `/actuator/threaddump` — disabled or admin-only
  - [ ] `/actuator/mappings` — disabled or admin-only (exposes all URL mappings)
  - [ ] `/actuator/beans` — disabled or admin-only (exposes all Spring beans)
  - [ ] `/actuator/shutdown` — disabled (can shut down the application!)
  - [ ] `/actuator/loggers` — admin-only (can change log levels at runtime)

### Actuator Path
- [ ] Actuator base path changed from default `/actuator` (optional but recommended)
- [ ] Actuator endpoints behind authentication (separate `SecurityFilterChain`)
- [ ] Actuator port separated from main application port (if possible)

### Health Endpoint
- [ ] `management.endpoint.health.show-details` is `never` or `when-authorized` (not `always`)
- [ ] Custom health indicators do not expose sensitive information

---

## 📝 Input Validation

### Controller-Level
- [ ] `@Valid` or `@Validated` on all `@RequestBody` parameters
- [ ] `@Valid` on nested objects (cascading validation)
- [ ] `@RequestParam` with `required = true` for mandatory parameters
- [ ] `@PathVariable` values validated (type, range, format)
- [ ] `@RequestHeader` values validated where security-relevant

### DTO / Request Objects
- [ ] All DTOs use Bean Validation annotations:
  - [ ] `@NotNull` / `@NotBlank` for required fields
  - [ ] `@Size` for string length limits
  - [ ] `@Min` / `@Max` for numeric ranges
  - [ ] `@Pattern` for format validation (email, phone, etc.)
  - [ ] `@Email` for email fields
- [ ] Custom `ConstraintValidator` for complex business rules
- [ ] DTOs used instead of `@Entity` for request/response (mass assignment protection)

### Binding & Deserialization
- [ ] `@Entity` classes NEVER used as `@RequestBody` directly
- [ ] Jackson deserialization does not enable `ACCEPT_FLOAT_AS_INT` or other loose modes
- [ ] `@JsonIgnoreProperties(ignoreUnknown = true)` on DTOs (reject unknown fields if needed)

---

## 🗄️ Data Access Security

### JPA / Hibernate
- [ ] `@Query` annotations use parameterized queries (`:param`, `?1`)
- [ ] No string concatenation in JPQL/HQL queries
- [ ] Native queries (`nativeQuery = true`) properly parameterized
- [ ] `EntityManager.createQuery()` / `createNativeQuery()` parameterized
- [ ] Criteria API or QueryDSL used for dynamic queries (not string building)

### MyBatis (if applicable)
- [ ] `#{}` used for ALL user input (not `${}`)
- [ ] `${}` only used for table/column names with strict allowlist validation
- [ ] Dynamic SQL (`<if>`, `<choose>`, `<foreach>`) properly parameterized
- [ ] `@Select`, `@Update` annotations properly parameterized

### JdbcTemplate (if applicable)
- [ ] `JdbcTemplate.query()` with `?` placeholders and parameter array
- [ ] No `String.format()` or `+` concatenation for building SQL

### General
- [ ] Database user has least-privilege permissions
- [ ] Database connection encrypted (TLS)
- [ ] Connection pool configured with limits (prevent connection exhaustion)

---

## 📤 Response Security

### Data Exposure
- [ ] API responses return DTOs (not entities)
- [ ] Sensitive fields excluded from responses (`@JsonIgnore` or DTO mapping)
- [ ] Password hashes never included in any API response
- [ ] Internal IDs / implementation details not exposed
- [ ] Pagination enforced on list endpoints (prevent full table dump)

### Error Handling
- [ ] `@ControllerAdvice` global exception handler defined
- [ ] Exception handler returns generic error messages (not stack traces)
- [ ] `server.error.include-stacktrace=never` in production config
- [ ] `server.error.include-message=never` in production config
- [ ] `server.error.include-binding-errors=never` in production config
- [ ] `server.error.include-exception=false` in production config
- [ ] Custom error response format (ErrorResponse DTO with error code + generic message)

---

## ⚙️ Configuration Security

### Sensitive Properties
- [ ] `spring.datasource.password` externalized (env var, vault, not in config file)
- [ ] `spring.security.user.password` NOT set in config (or disabled in production)
- [ ] API keys / secrets externalized (not in `application.yml`)
- [ ] `spring.mail.password` externalized
- [ ] OAuth client secrets externalized
- [ ] Encryption keys externalized

### Profile Management
- [ ] Production profile (`application-prod.yml`) has strict security settings
- [ ] Debug/development profiles not active in production
- [ ] `spring.profiles.active` set via environment variable (not hardcoded)
- [ ] DevTools (`spring-boot-devtools`) not included in production builds

### Server Configuration
- [ ] `server.error.include-stacktrace=never`
- [ ] `server.servlet.session.cookie.secure=true`
- [ ] `server.servlet.session.cookie.http-only=true`
- [ ] `server.servlet.session.cookie.same-site=Lax`
- [ ] `server.tomcat.max-http-form-post-size` set (limit request size)
- [ ] TLS configured (`server.ssl.*`) or terminated at reverse proxy

---

## 📦 Dependencies

### Known Vulnerabilities
- [ ] No known Critical/High CVEs in current dependencies
- [ ] Spring Boot version is within supported/maintained range
- [ ] Spring Security version matches Spring Boot (no version conflicts)
- [ ] OWASP Dependency-Check or similar tool integrated in CI/CD
- [ ] Dependabot or Renovate configured for automated updates

### Dangerous Dependencies
- [ ] No `commons-collections` < 3.2.2 (deserialization gadgets)
- [ ] No `log4j-core` < 2.17.1 (Log4Shell)
- [ ] No `spring-cloud-function` with known RCE vulnerabilities
- [ ] No `snakeyaml` < 2.0 (deserialization issues)
- [ ] No `jackson-databind` with known CVEs (polymorphic deserialization)

---

## 🪵 Logging Security

- [ ] Passwords never logged at any log level
- [ ] Authentication tokens never logged at any log level
- [ ] PII (email, phone, address) not logged at INFO level or above
- [ ] Credit card / financial data never logged
- [ ] Log messages use parameterized format `{}` (not string concatenation)
- [ ] `@ToString.Exclude` (Lombok) on sensitive entity fields
- [ ] Request/response logging middleware excludes sensitive headers (`Authorization`, `Cookie`)

---

## 🏗️ Architecture Patterns

### Controller Layer
- [ ] Controllers are thin (delegate to services)
- [ ] No business logic in controllers
- [ ] No direct repository access from controllers (always via service)

### Service Layer
- [ ] Authorization checks in service layer (not just controller)
- [ ] Transaction boundaries properly managed (`@Transactional`)
- [ ] No `@Transactional` on controller methods

### Exception Handling
- [ ] Specific exception types for different error conditions
- [ ] No empty catch blocks in security-related code
- [ ] No `catch (Throwable)` or `catch (Exception)` swallowing security errors
- [ ] Security exceptions (auth/authz) always result in 401/403 (never 200/500)

---

*Java / Spring Boot plugin — security checklist for Backend Server Security Audit Skill v1.1.0*
