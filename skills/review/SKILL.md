---
description: Use to perform a structured code review of staged or recently changed files, checking correctness, tests, security, performance, readability, and conventions.
invoke-by: both
---

# /review — Code Review

**Usage:** `/review` (reviews staged changes or specified files)

**Review checklist:**
- [ ] **Correctness:** Does the code do what it's supposed to?
- [ ] **Tests:** Are there adequate tests?
- [ ] **Security:** Any vulnerabilities introduced?
- [ ] **Performance:** Any obvious inefficiencies?
- [ ] **Readability:** Is the code clear and well-documented?
- [ ] **Conventions:** Does it follow project standards? (See `.agent/CONVENTIONS.md`)

**Output format:**
```markdown
## Code Review: <scope>

### Summary
Overall assessment.

### Issues Found
1. **[severity]** file:line — Description

### Suggestions
- Optional improvements

### Approval Status
✅ Ready to merge | ⚠️ Changes requested | 🚫 Needs rework
```
