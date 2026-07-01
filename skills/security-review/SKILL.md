---
description: Use for a focused security review of changes, checking for hardcoded secrets, injection vulnerabilities, path traversal, insecure dependencies, and missing input validation.
invoke-by: both
---

# /security-review — Focused Security Review

**Usage:** `/security-review`

**Check for:**
- Hardcoded secrets or credentials
- SQL injection vulnerabilities
- XSS vulnerabilities
- Path traversal issues
- Insecure dependencies
- Missing input validation
- Improper error handling (information disclosure)

See `.agent/SECURITY.md` for the full OWASP ASI alignment reference and detection patterns. Note that secret commits and writes are also blocked deterministically by `hooks/scripts/block-secret-commit.sh` and `hooks/scripts/block-secret-write.sh` — this skill covers the categories those hooks don't (injection, XSS, path traversal, dependency risk).
