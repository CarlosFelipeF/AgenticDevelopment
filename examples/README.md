# Examples — Adapters & Enforcement

The `.agent/` files tell a cooperative agent what to do. **They cannot stop an agent that has been
tricked, has drifted, or simply makes a mistake.** These examples turn the most important rules into
controls that hold either way.

Copy what you need into your project. Nothing here is active in this repository.

## Layers of defence

| Layer | What it does | Holds if the agent is hijacked? | Files |
|-------|--------------|:--:|-------|
| 1. Instructions | Tells the agent the rules | ❌ Guidance only | `AGENTS.md`, `.agent/` |
| 2. Tool permissions | The agent's tool refuses denied actions | ✅ In that tool | `enforcement/claude/settings.json` |
| 3. Hooks | Check each command and file action before it runs | ⚠️ Strong, not perfect | `../hooks/` (plugin) |
| 4. Pre-commit | Blocks secrets and junk at commit time | ⚠️ Unless bypassed | `enforcement/pre-commit-config.yaml` |
| 5. CI + branch protection + CODEOWNERS | Server-side checks; named humans must approve | ✅ Yes | `enforcement/github/` |
| 6. Sandbox + egress control | Limits what any process can reach | ✅ Yes | `enforcement/claude/settings.json` (`sandbox`), plus your platform |

Rule of thumb: **anything that must never happen needs a control at layer 2 or above.**
Layers 3 and 4 catch most mistakes early; layers 5 and 6 are the ones an attacker can't talk past.

## Adapters — one source of truth for every tool

Keep shared rules in `AGENTS.md`. Each tool gets, at most, a thin pointer.

| Tool | Copy | To |
|------|------|----|
| Claude Code | `adapters/claude/CLAUDE.md` | `CLAUDE.md` |
| GitHub Copilot (IDE chat) | `adapters/github/copilot-instructions.md` | `.github/copilot-instructions.md` |
| Cursor (always-on rule) | `adapters/cursor/agents.mdc` | `.cursor/rules/agents.mdc` |
| Gemini CLI | `adapters/gemini/settings.json` | `.gemini/settings.json` |
| Aider | `adapters/aider/.aider.conf.yml` | `.aider.conf.yml` |
| Codex, Jules, Copilot coding agent, Zed, goose, Devin and others | — | Read `AGENTS.md` natively |
| Any PR workflow | `adapters/github/pull_request_template.md` | `.github/pull_request_template.md` |

## Enforcement — quick install

Run these yourself (not through your agent — the hooks are designed to block agents from writing
to `.claude/`).

**Claude Code hooks — recommended: the plugin** (installs all hooks and skills):
```
/plugin install agent-governance-framework --marketplace CarlosFelipeF/AgenticDevelopment
```
(On Claude Code versions older than 2.1.275, first run
`/plugin marketplace add CarlosFelipeF/AgenticDevelopment`, then `/plugin install agent-governance-framework`.)
Then copy the `sandbox` and `permissions` blocks of `enforcement/claude/settings.json` into your
`.claude/settings.json` — the plugin registers the hooks itself.

**Without the plugin**, copy the hooks into the project and use the full settings file:
```bash
# From your project root, with this framework checked out at ../AgenticDevelopment
FW=../AgenticDevelopment

# Claude Code permissions + hooks (needs Python 3.8+, bash and jq)
mkdir -p .claude/hooks
cp "$FW/examples/enforcement/claude/settings.json" .claude/settings.json
cp "$FW"/hooks/scripts/* .claude/hooks/
```

**For every project:**
```bash
FW=../AgenticDevelopment/examples

# Pre-commit secret scanning
cp "$FW/enforcement/pre-commit-config.yaml" .pre-commit-config.yaml
pre-commit install

# CI guardrails and code owners (then turn on branch protection — see below)
mkdir -p .github/workflows
cp "$FW/enforcement/github/agent-guardrails.yml" .github/workflows/
cp "$FW/enforcement/github/CODEOWNERS" .github/CODEOWNERS   # edit the team names

# Check your setup (also proves the hook really blocks)
../AgenticDevelopment/scripts/agent-doctor.sh
```

**Then, in your Git host settings (this is the step that actually holds):**
- Protect `main`: require a pull request, at least one human approval, and passing status checks
- Turn on "Require review from Code Owners"
- Turn on secret scanning push protection if your host offers it
- Give agents their own credentials with the least access they need — never your personal admin token

## The sandbox

Hooks check commands one by one; the sandbox limits what *any* command can touch, at the
operating-system level (Seatbelt on macOS, bubblewrap on Linux and WSL2). The example settings
turn it on with three choices that matter:

- `failIfUnavailable: true` — Claude Code refuses to start if the sandbox can't run, instead of
  quietly running commands without it (the default behaviour).
- `allowUnsandboxedCommands: false` — the agent can't retry a failed command outside the sandbox.
- `network.allowedDomains` — sandboxed commands reach only these hosts. Add your own registries;
  everything else is blocked, which stops most data exfiltration.

Linux and WSL2 need `bubblewrap` and `socat` (`sudo apt-get install bubblewrap socat`). Native
Windows isn't supported — with `failIfUnavailable: true` Claude Code won't start there, so remove
that line if your team works on native Windows. See the
[sandboxing docs](https://code.claude.com/docs/en/sandboxing).

## What the hooks block

| Hook | Watches | Blocks |
|------|---------|--------|
| `guard-bash.py` | Shell commands | Everything in the list below, plus commits whose added lines contain a secret |
| `block-secret-write.sh` | Write / Edit | Writing a secret into a file |
| `protect-files.sh` | Read / Write / Edit | Credential and system folders; edits to `.claude/` settings, hooks, plugins and `.git/hooks/`; asks before editing `AGENTS.md`, `.agent/` and other protected files |

`guard-bash.py` tokenises commands like a shell (quotes, pipes, `&&`, `$(...)`, heredocs), so
words inside a commit message don't trigger it and quoting tricks don't hide a command. It blocks:

- **Running downloaded or piped code:** `curl … | sh`, `bash <(curl …)`, `bash -c "$(curl …)"`, `base64 -d | sh`
- **Skipping checks:** `--no-verify`, `git commit -n`, `core.hooksPath`, `SKIP=…`, `HUSKY=0`
- **Risky git:** force pushes, pushes to `main`/`master` (including a bare `git push` while on `main`),
  remote branch deletion, `reset --hard`, `clean -f`, history rewrites
- **Secrets:** reading `.env`, keys and credential files (including via globs, braces and variables),
  dumping the environment, echoing or sending `$…TOKEN`-style variables
- **Exfiltration:** `curl -d @file`, `-F x=@file`, `-T`, `wget --post-file`, `scp` to remote hosts, `nc`
- **Destruction:** `rm -rf` on `/`, `~`, `..`, `.`, `*`, `.git`, system folders or unchecked variables
- **Privilege escalation:** `sudo`, `su`, `doas`
- **Self-modification:** writing to `AGENTS.md`, `CLAUDE.md`, `.agent/`, `.claude/`, `.git/hooks/`,
  CI workflows or pre-commit config — through redirects, `sed -i`, `tee`, `cp`, `mv` or inline code

Proof: `python3 -m unittest discover -s tests` runs 150+ attack and everyday-command cases
against `guard-bash.py`, plus tests for the other three hooks.

**Known gaps (why layers 5 and 6 still matter):**
- A script written to disk and then run (`bash ./x.sh`) is not inspected.
- Inline Python/Node code is checked with simple heuristics only.
- `grep -r` over the whole repo can still print `.env` contents. Claude Code applies `Read` deny
  rules to its own Grep tool on a best-effort basis; shell `grep -r` is not covered. Keep real
  secrets out of the working tree where you can (use a secret manager or `~/.config`).
- Hooks fail open if `python3` or `jq` is missing — `agent-doctor` checks for both.

Found a bypass? Report it privately (see `.github/SECURITY.md`), then add a test case.

## Notes

- **Your agent can't edit its own guardrails** — by design. The plugin blocks edits to `.claude/`
  settings, hooks and plugins and asks before edits to `AGENTS.md` and `.agent/`; the example deny
  rules block both. Edit those files yourself, or approve the change outside the agent.
- **Review before copying.** These are starting points. Tune the deny and ask lists to your stack.
- **Pin versions.** The example workflows pin GitHub Actions to full commit SHAs; copy
  `enforcement/github/dependabot.yml` so Dependabot keeps them current. Run `pre-commit autoupdate` regularly.
