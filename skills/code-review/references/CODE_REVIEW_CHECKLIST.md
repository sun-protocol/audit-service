# Code Review Checklist

Use this checklist when reviewing PR changes. Only check items relevant to the changed code.

---

## 1. Correctness

- [ ] Logic is correct and handles all expected inputs
- [ ] Edge cases are handled (null, empty, boundary values, overflow)
- [ ] Error paths are handled and propagate correctly
- [ ] Return values are checked where applicable
- [ ] Concurrency is handled correctly (no race conditions, proper locking)
- [ ] Resources are properly closed/released (connections, files, streams)
- [ ] API contracts are preserved (no unintended breaking changes)
- [ ] State mutations are intentional and safe

## 2. Security

- [ ] No hardcoded secrets, API keys, passwords, or tokens
- [ ] User input is validated and sanitized
- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] Authentication is required on new endpoints
- [ ] Authorization checks are present for resource access
- [ ] Sensitive data is not logged or exposed in responses
- [ ] New dependencies are from trusted sources and up to date
- [ ] File operations validate paths (no path traversal)
- [ ] External URLs are validated (no SSRF)
- [ ] CORS, CSRF protections are maintained

## 3. Performance

- [ ] No N+1 query patterns (queries inside loops)
- [ ] Database queries have appropriate indexes
- [ ] Large data sets use pagination or streaming
- [ ] Expensive operations are not repeated unnecessarily
- [ ] Caching is used where appropriate
- [ ] No unbounded growth (lists, maps, queues)
- [ ] Async operations are used correctly (no blocking in async context)

## 4. Code Quality

- [ ] Functions are small and focused (<50 lines)
- [ ] Files are not too large (<800 lines)
- [ ] Naming is clear and consistent with codebase conventions
- [ ] No deep nesting (>4 levels)
- [ ] No code duplication (DRY)
- [ ] No dead code (unused variables, unreachable branches, commented-out code)
- [ ] Imports are clean (no unused imports)
- [ ] Error messages are helpful and actionable
- [ ] Magic numbers/strings are extracted to constants
- [ ] Proper separation of concerns

## 5. Testing

- [ ] New functionality has corresponding tests
- [ ] Bug fixes include regression tests
- [ ] Tests cover happy path and error paths
- [ ] Tests cover edge cases and boundary conditions
- [ ] Tests are independent and not order-dependent
- [ ] Mocks are used appropriately (not over-mocking)
- [ ] Test names describe the scenario being tested

## 6. Documentation

- [ ] New public APIs have docstrings/documentation
- [ ] Changed behavior is reflected in existing documentation
- [ ] Complex algorithms have explanatory comments
- [ ] Configuration changes are documented
- [ ] Database schema changes have migration scripts
- [ ] Breaking changes are documented in changelog/release notes

## 7. Compatibility

- [ ] Backward compatibility is maintained (or breaking changes are intentional)
- [ ] Database migrations are reversible
- [ ] API versioning is handled correctly
- [ ] Feature flags are used for gradual rollout if needed
- [ ] Environment-specific code is properly gated

## 8. Observability

- [ ] Key operations have appropriate logging
- [ ] Error conditions are logged with context
- [ ] No sensitive data in logs
- [ ] Metrics are added for new features if applicable
- [ ] Health checks are updated if new dependencies are added
