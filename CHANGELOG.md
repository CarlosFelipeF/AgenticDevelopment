# Changelog

All notable changes to this framework are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [2.1.0] — 2026-11-03

### Added
- **Enforcement kit** (`examples/enforcement/`): Claude Code permission deny/ask lists, a
  `PreToolUse` command guard hook, pre-commit config with gitleaks, a GitHub Actions guardrail
  workflow (secret scan, dependency review, governance-change warning) and CODEOWNERS.
- **Tool adapters** (`examples/adapters/`): `CLAUDE.md` (`@AGENTS.md` import), Copilot
  instructions, a Cursor rule and a PR template with AI-assistance disclosure.
- **`scripts/agent-doctor.sh`**: read-only checker for framework setup and enforcement gaps.
- Non-negotiable rules inline in `AGENTS.md`, a Definition of Done, and an explicit precedence order.
- Indirect prompt injection guidance and the **Rule of Two** (`SECURITY.md`).
- Supply-chain checks against hallucinated packages ("slopsquatting"); MCP servers, plugins and
  skills treated as dependencies.
- Code integrity rules: never weaken tests or security controls to get a green build.
- Autonomy levels (`restricted`, `supervised`, `standard`) in `CONSTRAINTS.md`.
- `/verify` and `/handoff` commands; agent test rules in `TESTING.md`; rules for AI-generated code.
- AI attribution trailers and evidence-based PR descriptions in `WORKFLOW.md`.
- TEMPLATE banners on project-context files so agents don't treat sample content as fact.

### Changed
- **Progressive context loading:** only `SECURITY`, `CONSTRAINTS` and `PROJECT` load every
  session; other files load when the task needs them.
- OWASP mapping corrected to the official **OWASP Top 10 for Agentic Applications (2026)** names
  (e.g. ASI01 Agent Goal Hijack, ASI05 Unexpected Code Execution, ASI10 Rogue Agents).
- Secret detection now relies on scanners; the over-broad generic regex was replaced with
  high-signal patterns. Exposed secrets must be rotated, not just removed.
- `CONSTRAINTS.md` contradictions resolved (dependency installs, commit approval, reading `.env`);
  approval no longer carries over between actions; agents may not edit their own governance files.
- `WORKFLOW.md`: explicit `git add <path>`, no interactive rebase, agents never merge to `main`.
- `SESSIONS.md`: handoff notes treated as untrusted; context hygiene; no hard-coded `npm`.
- README rewritten to be honest about limits: instructions guide, enforcement contains.
- `.gitignore` covers `.env.*`, keys, handoff notes and local agent settings.

## [2.0.0] — 2026-01

- Initial public framework: seven `.agent/` protocol files, immutable/configurable rule split,
  OWASP agentic alignment and slash command conventions.
