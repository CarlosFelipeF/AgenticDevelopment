# Examples — Adapters & Enforcement

The `.agent/` files tell a cooperative agent what to do. **They cannot stop an agent that has been
tricked, has drifted, or simply makes a mistake.** These examples turn the most important rules into
controls that hold either way.

Copy what you need into your project. Nothing here is active in this repository.

## Layers of defence

| Layer | What it does | Stops a misbehaving agent? | Files |
|-------|--------------|:--:|-------|
| 1. Instructions | Tells the agent the rules | ❌ Guidance only | `AGENTS.md`, `.agent/` |
| 2. Tool permissions | Agent tool refuses denied actions | ✅ In that tool | `enforcement/claude/settings.json` |
| 3. Hooks | Inspect each command before it runs | ✅ Best-effort | `enforcement/claude/hooks/guard-bash.sh` |
| 4. Pre-commit | Blocks secrets and junk at commit time | ⚠️ Unless `--no-verify` | `enforcement/pre-commit-config.yaml` |
| 5. CI + branch protection | Server-side checks; humans must approve | ✅ Yes | `enforcement/github/` |
| 6. Sandbox + egress control | Limits what any process can reach | ✅ Yes | Your platform — see `AGENTIC-SECURITY-CHECKLIST.md` |

Rule of thumb: **anything that must never happen needs a control at layer 2 or above.**

## Adapters — one source of truth for every tool

Keep shared rules in `AGENTS.md`. Each tool gets a thin pointer file.

| Tool | Copy | To |
|------|------|----|
| Claude Code | `adapters/claude/CLAUDE.md` | `CLAUDE.md` |
| GitHub Copilot | `adapters/github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Cursor | `adapters/cursor/agents.mdc` | `.cursor/rules/agents.mdc` |
| Codex, Gemini CLI, Jules, Aider, Zed and others | — | Read `AGENTS.md` natively |
| Any PR workflow | `adapters/github/pull_request_template.md` | `.github/pull_request_template.md` |

## Enforcement — quick install

```bash
# From your project root, with this framework checked out at ../AgenticDevelopment
FW=../AgenticDevelopment/examples

# Claude Code permissions + command guard (needs jq or python3)
mkdir -p .claude/hooks
cp "$FW/enforcement/claude/settings.json" .claude/settings.json
cp "$FW/enforcement/claude/hooks/guard-bash.sh" .claude/hooks/
chmod +x .claude/hooks/guard-bash.sh

# Pre-commit secret scanning
cp "$FW/enforcement/pre-commit-config.yaml" .pre-commit-config.yaml
pre-commit install

# CI guardrails and code owners (then enable branch protection — see below)
mkdir -p .github/workflows
cp "$FW/enforcement/github/agent-guardrails.yml" .github/workflows/
cp "$FW/enforcement/github/CODEOWNERS" .github/CODEOWNERS   # edit team names

# Check your setup
../AgenticDevelopment/scripts/agent-doctor.sh
```

**Then, in your Git host settings (this is the step that actually holds):**
- Protect `main`: require a pull request, at least one human approval, and passing status checks
- Turn on "Require review from Code Owners"
- Turn on secret scanning push protection if your host offers it
- Give agents their own credentials with the least access they need — never your personal admin token

## Notes

- **Review before copying.** These are starting points. Tune the deny and ask lists to your stack.
- **`guard-bash.sh` is pattern-based.** It catches common mistakes and simple injections. A
  determined attacker can get around regexes. That's why layers 5 and 6 exist.
- **Pin versions.** Tool versions shown were current in November 2026. Pin GitHub Actions to a full
  commit SHA in production, and run `pre-commit autoupdate` regularly.
