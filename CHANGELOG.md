# Changelog

All notable changes to this framework are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [2.1.0] — 2026-11-03

### Added
- **Enforcement kit** (`examples/enforcement/`): Claude Code permission deny/ask lists, a
  `PreToolUse` command guard, pre-commit config with gitleaks, a GitHub Actions guardrail
  workflow (diff-scoped secret scan with checksum-verified gitleaks, dependency review,
  governance-change summary) and CODEOWNERS covering `AGENTS.md` at any depth.
- **`guard-bash.py`**: a shell-aware command guard (tokenises quotes, pipes, `$(...)`, `<(...)`,
  heredocs, variables, globs). Blocks downloaded-code execution, hook skipping, force/main pushes,
  secret reads and exfiltration, destructive deletes, privilege escalation and agents editing their
  own guardrails. Fails closed on bad input or internal errors.
- **`tests/test_guard_bash.py`**: 150+ adversarial and everyday-command cases, plus glob, branch
  and fail-closed tests. Standard library only.
- **Tool adapters** (`examples/adapters/`): `CLAUDE.md` (`@AGENTS.md` import), Copilot
  instructions, a Cursor rule, Gemini CLI and Aider configs, and a PR template with
  AI-assistance disclosure.
- **`scripts/agent-doctor.sh`**: read-only checker for adopting projects. Proves the hook really
  blocks, flags nested `AGENTS.md` files, and lists the manual checks it can't verify.
- **`scripts/self-test.sh`**: one command to verify this repository (syntax, tests, configs,
  internal links, version consistency, doctor).
- **`.github/SECURITY.md`**: private vulnerability reporting policy.
- Rule that nested `AGENTS.md` files can add rules but never loosen the root ones.
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
- `.gitignore` covers `.env.*`, keys, handoff notes, local agent settings and Python caches.
- More high-signal secret patterns (GitHub fine-grained, GitLab, Stripe, Google, JWT) and a rule
  against putting secrets in prompts.

### Fixed (found in a second, adversarial review before release)
- The first command guard (`guard-bash.sh`, regex-based) let 17 of 18 tested attacks through —
  including `bash -c "$(curl …)"`, `rm -r -f /` and `echo x > AGENTS.md` — blocked legitimate
  commands such as `git push origin main-fix`, and failed open on malformed input. Replaced by
  `guard-bash.py`.
- Claude Code permission rules used `./` (current directory) anchors instead of `/` (project
  root), matched `--no-verify` and `--force` only in one position, and did not stop an agent
  editing `.claude/` — its own guardrails.
- The README said Gemini CLI and Aider read `AGENTS.md` natively; both need a one-line config.
- `agent-doctor` treated any workflow mentioning `secrets.` as a secret scan, used a GNU-only
  grep pattern, and checked `.gitignore` by text instead of with `git check-ignore`.
- CI secret scanning scanned all history on every PR (one old secret would fail every PR forever);
  it now scans only new commits and verifies the gitleaks download checksum.

## [2.0.0] — 2026-01

- Initial public framework: seven `.agent/` protocol files, immutable/configurable rule split,
  OWASP agentic alignment and slash command conventions.
