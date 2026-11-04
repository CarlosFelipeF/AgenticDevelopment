---
description: Use for a focused security review of changes, checking for hardcoded secrets, injection vulnerabilities, path traversal, insecure dependencies, and missing input validation.
---

# /security-review — Focused Security Review

**Usage:** `/security-review`

**Check for:**
- Hardcoded secrets or credentials (run the secret scanner, don't eyeball it)
- Injection: SQL, command, template, XSS, path traversal
- New or changed dependencies — do they exist, are they the intended package, are they pinned?
  (AI tools invent package names; attackers register them — "slopsquatting")
- Missing input validation or output encoding
- Weakened auth, permissions, validation or tests
- Error handling that leaks internals
- Agent-specific risks: untrusted content reaching prompts, tools or shells; new outbound
  network calls; anything that combines all three legs of the Rule of Two (see `.agent/SECURITY.md`)
- Changes to governance or guardrail files (`AGENTS.md`, `.agent/`, `hooks/`, CI) — flag for a human

See `.agent/SECURITY.md` for the full OWASP ASI alignment reference and detection patterns. Note that secret commits and writes are also blocked deterministically by `hooks/scripts/block-secret-commit.sh` and `hooks/scripts/block-secret-write.sh` — this skill covers the categories those hooks don't (injection, XSS, path traversal, dependency risk).
