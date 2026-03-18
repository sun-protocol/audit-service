---
name: Code Review
description: |
  PR code review skill. Analyzes git diff between from_branch and to_branch,
  reviews changed code for quality, security, performance, and best practices.
report_path: .audit/Audit-Report.md
---

# Code Review Skill

Performs a comprehensive code review of a Pull Request by analyzing the diff between two branches. Focuses **exclusively** on changed code — does not review unchanged code.

## Skill Resources

| Resource | Path | Description |
|----------|------|-------------|
| **Review Report Template** | `resources/review_report_template.md` | Report structure for `.audit/Audit-Report.md` |
| **Code Review Checklist** | `references/CODE_REVIEW_CHECKLIST.md` | Comprehensive review checklist |

---

## Workflow

```
Trigger (with from_branch and to_branch)
  |
  +- Step 1: Get the Diff            <- run git diff from_branch...to_branch
  +- Step 2: Understand the Changes   <- categorize and understand each changed file
  +- Step 3: Review the Changes       <- multi-dimensional code review
  +- Step 4: Generate Report           <- write .audit/Audit-Report.md
```

---

## Instructions

> **CRITICAL RULES**:
> - You MUST first run `git diff from_branch...to_branch` to get the actual changes.
> - You MUST **only review changed code**. Do NOT audit unchanged files.
> - You MUST read the full context of changed files (not just the diff) to understand the impact.
> - You MUST read `references/CODE_REVIEW_CHECKLIST.md` before reviewing.
> - Every finding MUST include: file location, code evidence, severity, and recommendation.
> - Output the final report following `resources/review_report_template.md` and **SAVE** to `.audit/Audit-Report.md`.

---

### Step 1: Get the Diff

1. Run `git diff from_branch...to_branch` to see all changes.
2. Run `git diff from_branch...to_branch --stat` to get a summary of changed files.
3. Run `git log from_branch...to_branch --oneline` to understand commit history.
4. Record: total files changed, lines added/removed, commit count.

---

### Step 2: Understand the Changes

For each changed file, determine:

| Aspect | What to Identify |
|--------|-----------------|
| **Change type** | New file, modified, deleted, renamed |
| **Change category** | Feature, bugfix, refactor, config, test, docs |
| **Scope** | Which module/component is affected |
| **Dependencies** | What other code depends on or is called by the changed code |

Read the full content of each changed file (not just the diff hunks) to understand the surrounding context.

Group changes by logical unit (e.g., "added user auth endpoint" may span controller + service + test + migration).

---

### Step 3: Review the Changes

Read `references/CODE_REVIEW_CHECKLIST.md` and apply each applicable category to the changed code.

#### A. Correctness & Logic

| Check | What to Look For |
|-------|-----------------|
| **Logic errors** | Off-by-one, incorrect conditions, missing edge cases, wrong operator |
| **Null/undefined handling** | Missing null checks, potential NPE/TypeError on changed paths |
| **Error handling** | Unhandled exceptions, swallowed errors, missing error propagation |
| **Concurrency** | Race conditions, missing locks, shared mutable state |
| **Resource leaks** | Unclosed connections, file handles, streams in changed code |
| **API contract** | Breaking changes to public interfaces, missing backward compatibility |

#### B. Security

| Check | What to Look For |
|-------|-----------------|
| **Injection** | SQL/command/template injection in new or modified code |
| **Auth/Authz** | Missing or weakened authentication/authorization checks |
| **Input validation** | Unvalidated user input in new endpoints or parameters |
| **Sensitive data** | Hardcoded secrets, credentials, tokens, PII exposure |
| **Data exposure** | New API responses leaking internal data |
| **Dependency risk** | New dependencies with known vulnerabilities |

#### C. Performance

| Check | What to Look For |
|-------|-----------------|
| **N+1 queries** | Database queries inside loops |
| **Missing indexes** | New queries on unindexed columns |
| **Unbounded operations** | Missing pagination, loading entire tables, unbounded loops |
| **Unnecessary computation** | Repeated calculations, missing caching opportunities |
| **Memory** | Large object allocation, missing cleanup |

#### D. Code Quality

| Check | What to Look For |
|-------|-----------------|
| **Naming** | Unclear, misleading, or inconsistent naming |
| **Complexity** | Functions too long (>50 lines), deep nesting (>4 levels), high cyclomatic complexity |
| **Duplication** | Copy-pasted code that should be extracted |
| **Dead code** | Unreachable code, unused variables/imports, commented-out code |
| **Consistency** | Style inconsistent with the rest of the codebase |
| **Separation of concerns** | Business logic mixed with infrastructure, UI logic in backend |

#### E. Testing

| Check | What to Look For |
|-------|-----------------|
| **Missing tests** | New logic without corresponding tests |
| **Test quality** | Tests that don't assert meaningful behavior, brittle tests |
| **Edge cases** | Missing boundary condition tests |
| **Test coverage** | Are all new code paths exercised? |

#### F. Documentation & Maintainability

| Check | What to Look For |
|-------|-----------------|
| **Missing docs** | New public APIs without documentation |
| **Outdated docs** | Changed behavior not reflected in existing docs |
| **Complex logic** | Non-obvious code without explanatory comments |
| **Migration** | Schema changes without migration scripts |
| **Config** | New config options without documentation or defaults |

#### Finding Format

For each issue found:

```markdown
### [severity-XX] Title

| Property | Value |
|----------|-------|
| **Severity** | Critical / Major / Minor / Suggestion |
| **Category** | Correctness / Security / Performance / Quality / Testing / Docs |
| **File** | `path/to/file` : Lines X-Y |

**Description:** [What is wrong and why]

**Code:**
\`\`\`
[relevant code snippet from the diff]
\`\`\`

**Recommendation:**
\`\`\`
[suggested fix]
\`\`\`
```

#### Severity Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| **Critical** | Bugs that will cause failures in production, security vulnerabilities, data loss | Must fix before merge |
| **Major** | Significant issues: performance problems, missing error handling, logic flaws | Should fix before merge |
| **Minor** | Code quality issues, naming, minor improvements | Nice to fix, not blocking |
| **Suggestion** | Style preferences, alternative approaches, optimization ideas | Optional, for consideration |

---

### Step 4: Generate Report

> **CRITICAL**: You MUST write the final report to `.audit/Audit-Report.md` (relative to the code directory root). Create the `.audit/` directory if it does not exist. The report file MUST be at this exact path — the system reads the report from this location.

Generate the report following `resources/review_report_template.md`. The report must include:
1. **PR Overview**: Branch info, commit summary, files changed, change statistics
2. **Change Summary**: Grouped by logical unit, what each change does
3. **Detailed Findings**: All issues found, ordered by severity
4. **Positive Observations**: Good practices observed in the changes
5. **Review Verdict**: Approve / Request Changes / Comment, with rationale

After writing, verify the file exists at `.audit/Audit-Report.md`.

---

*Code Review Skill v1.0.0*
