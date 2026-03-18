# Java / Spring Boot Specialization

> Plugin for the Backend Server Security Audit skill.
> **Type:** Language
> **Loaded by:** Phase 0 when `pom.xml` or `build.gradle` detected with Java source files.
> **Path:** `plugins/java/`

---

## Framework Detection

| Indicator | Detection | Details |
|-----------|-----------|---------|
| `pom.xml` | Maven project | Check `<java.version>`, `<spring-boot.version>` |
| `build.gradle` / `build.gradle.kts` | Gradle project | Check `sourceCompatibility`, Spring Boot plugin |
| `spring-boot-starter-web` | Spring Boot Web | REST controllers via `@RestController` |
| `spring-boot-starter-security` | Spring Security | Auth/authz via `SecurityFilterChain` |
| `spring-boot-starter-data-jpa` | JPA/Hibernate | ORM via `@Entity`, `JpaRepository` |
| `spring-boot-starter-data-mongodb` | MongoDB | NoSQL via `MongoRepository` |
| `spring-boot-starter-actuator` | Actuator | Management endpoints at `/actuator/**` |
| `spring-boot-starter-oauth2-*` | OAuth2 | OAuth2 client/resource server |
| `mybatis-spring-boot-starter` | MyBatis | SQL mapping via XML or annotations |

### Version Significance

| Spring Boot Version | Java Baseline | Key Security Notes |
|-------------------|---------------|-------------------|
| 3.x | Java 17+ | Jakarta EE namespace, new SecurityFilterChain API |
| 2.7.x | Java 8+ | Legacy WebSecurityConfigurerAdapter (deprecated in 3.x) |
| 2.x | Java 8+ | javax namespace, older Spring Security APIs |

---

## SAST Tools

| Tool | Command | Focus | Output |
|------|---------|-------|--------|
| **SpotBugs + Find Security Bugs** | `mvn spotbugs:check` or `gradle spotbugsMain` | Java security bug patterns (SQL injection, XSS, crypto, deserialization) | XML/HTML report |
| **Semgrep (Java + Spring)** | `semgrep --config p/java --config p/spring --json` | Framework-aware rules for Spring Boot patterns | JSON |
| **Semgrep (OWASP)** | `semgrep --config p/owasp-top-ten --config p/security-audit --json` | OWASP Top 10 coverage | JSON |
| **OWASP Dependency-Check** | `mvn dependency-check:check` or `gradle dependencyCheckAnalyze` | Known CVEs in dependencies (NVD database) | HTML/JSON report |
| **PMD** | `mvn pmd:check` | Code quality + security rules | XML report |
| **SonarQube Scanner** | `mvn sonar:sonar` | Comprehensive SAST (if SonarQube server available) | Dashboard |

### Semgrep Custom Rules for Spring Boot

```yaml
rules:
  - id: spring-sqli-concatenation
    patterns:
      - pattern-either:
          - pattern: |
              $REPO.$METHOD("..." + $VAR + "...", ...)
          - pattern: |
              $EM.createQuery("..." + $VAR + "...", ...)
          - pattern: |
              $EM.createNativeQuery("..." + $VAR + "...", ...)
    message: SQL injection via string concatenation in JPA/JDBC query
    severity: ERROR
    languages: [java]
    metadata:
      cwe: "CWE-89"
      owasp: "A03:2021"

  - id: spring-actuator-exposed
    pattern: management.endpoints.web.exposure.include=*
    message: All Actuator endpoints exposed — may leak sensitive info
    severity: WARNING
    languages: [generic]
    metadata:
      cwe: "CWE-200"

  - id: spring-csrf-disabled
    pattern: http.csrf(csrf -> csrf.disable())
    message: CSRF protection disabled — verify this is intentional (API-only with token auth)
    severity: WARNING
    languages: [java]
    metadata:
      cwe: "CWE-352"
```

---

## Key Audit Focus Areas

### 1. Spring Security Configuration
- `SecurityFilterChain` bean definition (Spring Boot 3.x)
- `WebSecurityConfigurerAdapter` override (Spring Boot 2.x, deprecated)
- URL-based access rules (`.requestMatchers()`, `.antMatchers()`)
- Method-level security (`@PreAuthorize`, `@Secured`, `@RolesAllowed`)
- Password encoder configuration (`BCryptPasswordEncoder`, `Argon2PasswordEncoder`)
- CSRF configuration (enabled/disabled, token repository)
- CORS configuration (allowed origins, methods, headers)
- Session management (creation policy, fixation protection, concurrent sessions)
- OAuth2 / JWT configuration (token validation, audience, issuer)

### 2. Actuator Endpoint Exposure
- `management.endpoints.web.exposure.include` / `exclude`
- Sensitive endpoints: `/env`, `/configprops`, `/heapdump`, `/threaddump`, `/mappings`, `/beans`
- Actuator security (should require authentication in production)
- Custom health/info endpoint information leakage

### 3. Data Access Security
- JPA `@Query` with native queries: check for concatenation vs parameterization
- MyBatis `${}` (vulnerable) vs `#{}` (parameterized) in XML mappers and annotations
- `JdbcTemplate` query construction
- `EntityManager.createNativeQuery()` with string concatenation
- Spring Data derived queries (generally safe) vs custom queries

### 4. Input Validation
- `@Valid` / `@Validated` on controller method parameters
- Bean Validation annotations (`@NotNull`, `@Size`, `@Pattern`, `@Email`, etc.)
- Custom validators (`ConstraintValidator` implementations)
- `@RequestParam`, `@PathVariable`, `@RequestBody` validation
- Missing validation on nested objects

### 5. API Response Security
- Returning `Entity` vs `DTO` (Entity may expose internal fields: passwords, internal IDs)
- `@JsonIgnore` on sensitive fields
- Global exception handler (`@ControllerAdvice`) hiding internal details
- `server.error.include-stacktrace=never` in production
- `server.error.include-message=never` in production

### 6. Configuration Security
- `application.properties` / `application.yml` sensitive values
- Profile-specific configs (`application-prod.yml`)
- `spring.datasource.password` hardcoded vs externalized
- `spring.security.user.password` (default user)
- Jasypt / Spring Cloud Vault / AWS Secrets Manager integration

### 7. Java-Specific Code Quality (Security-Relevant)
- Empty catch blocks (silent failures hiding security issues)
- Catching `Throwable` (swallowing critical errors)
- Mutable static fields (thread-safety in concurrent request handling)
- Resource leaks (missing try-with-resources on DB connections, streams)
- Insecure random (`java.util.Random` vs `SecureRandom`)
- Unsafe deserialization (`ObjectInputStream` with untrusted data)

---

## File Patterns to Scan

| Pattern | Purpose | Priority |
|---------|---------|----------|
| `**/SecurityConfig*.java` | Spring Security configuration | CRITICAL |
| `**/WebSecurityConfig*.java` | Spring Security configuration (legacy) | CRITICAL |
| `**/application*.yml`, `**/application*.properties` | App configuration (secrets, debug, actuator) | CRITICAL |
| `**/*Controller.java` | API endpoints (injection, auth, input validation) | HIGH |
| `**/*RestController.java` | REST API endpoints | HIGH |
| `**/*Filter.java`, `**/*Interceptor.java` | Request processing pipeline | HIGH |
| `**/*Service.java`, `**/*ServiceImpl.java` | Business logic (authorization, data handling) | HIGH |
| `**/*Repository.java`, `**/*Dao.java` | Data access (SQL injection, query safety) | HIGH |
| `**/*Mapper.xml` | MyBatis SQL mappings (`${}` vs `#{}`) | HIGH |
| `**/*Config.java`, `**/*Configuration.java` | App configuration classes | MEDIUM |
| `**/*Entity.java`, `**/*Model.java` | Data models (sensitive fields, serialization) | MEDIUM |
| `**/*Dto.java`, `**/*VO.java`, `**/*Request.java` | DTOs (validation annotations) | MEDIUM |
| `**/*Exception*.java`, `**/*Handler.java` | Error handling (info leakage) | MEDIUM |
| `**/*Utils.java`, `**/*Util.java`, `**/*Helper.java` | Utility classes (crypto, file ops) | MEDIUM |
| `pom.xml`, `build.gradle` | Dependencies (CVEs, versions) | MEDIUM |
| `**/logback*.xml`, `**/log4j2*.xml` | Logging config (sensitive data logging) | LOW |
| `**/*.sql` | Database migration scripts | LOW |

---

## Spring Boot Version-Specific Notes

### Spring Boot 3.x (Current)
- Uses `SecurityFilterChain` bean (not `WebSecurityConfigurerAdapter`)
- Jakarta namespace (`jakarta.servlet`, `jakarta.validation`)
- `@Configuration(proxyBeanMethods = false)` preferred
- Native compilation support (GraalVM) — may affect reflection-based security checks
- Problem Details (RFC 7807) for error responses

### Spring Boot 2.x (Legacy)
- `WebSecurityConfigurerAdapter` (deprecated but still used)
- `javax` namespace
- Check for migration issues if upgrading

---

*Java / Spring Boot plugin for Backend Server Security Audit Skill v1.1.0*
