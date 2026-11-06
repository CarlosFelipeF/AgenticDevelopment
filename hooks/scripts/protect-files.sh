#!/usr/bin/env bash
# PreToolUse hook (matcher: Read|Write|Edit|NotebookEdit) — enforces
# .agent/CONSTRAINTS.md's "Protected files" (ask) and "Forbidden directories"
# (deny) rules, and stops agents editing their own guardrails (deny) or
# governance rules (ask) — ASI10 Rogue Agents.
#
# Credential directories (~/.ssh, ~/.aws) are denied for reads and writes
# alike — reading a private key into context is as bad as modifying it. The
# remaining rules guard modifications only: denying reads of /etc/* or asking
# on .env* reads (.env.example is read constantly) would break normal work.
set -euo pipefail

INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // empty')"

[ -z "$FILE_PATH" ] && exit 0

ask() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

deny() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

# Match on a canonical path, never the raw string: resolve it against CWD, collapse "."
# and "//", resolve symlinks, then lowercase it (macOS disks are case-insensitive, so
# ".claude/Settings.json" is the same file). Lowercasing everywhere can only add an
# approval prompt on Linux, never remove a block. Needs python3, like guard-bash.py;
# without it every file action is denied (fail closed), because raw-string matching can
# be dodged with "./", "//" or a symlink.
# canon PATH BASE [norm]: absolute path with symlinks resolved; with "norm", only "." and
# "//" are collapsed and symlinks are kept (macOS links /home to /System/Volumes/Data/home,
# so prefix checks like "is this under /home?" must use the unresolved form).
canon() {
  python3 -c 'import os, sys
p = os.path.expanduser(sys.argv[1])
if not os.path.isabs(p):
    p = os.path.join(sys.argv[2] or os.getcwd(), p)
print(os.path.normpath(p) if sys.argv[3] == "norm" else os.path.realpath(p))' "$1" "${2:-}" "${3:-}" 2>/dev/null
}
command -v python3 >/dev/null 2>&1 \
  || deny "Blocked: protect-files.sh needs python3 to check file paths safely. Install python3, then retry."
lower() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }

P_RAW="$(canon "$FILE_PATH" "$CWD")" && N_RAW="$(canon "$FILE_PATH" "$CWD" norm)" \
  && [ -n "$P_RAW" ] && [ -n "$N_RAW" ] \
  || deny "Blocked: protect-files.sh could not resolve this path, so it cannot check it safely."
P="$(lower "$P_RAW")"   # resolved: for guardrail patterns
N="$(lower "$N_RAW")"   # unresolved: for location checks
C=""; CN=""
if [ -n "$CWD" ]; then C="$(lower "$(canon "$CWD" "")")"; CN="$(lower "$(canon "$CWD" "" norm)")"; fi
H=""; HN=""
if [ -n "${HOME:-}" ]; then H="$(lower "$(canon "$HOME" "")")"; HN="$(lower "$(canon "$HOME" "" norm)")"; fi
BASENAME="$(basename "$P")"

# Credential directories: hard deny for every matched tool, reads included.
case "$P" in
  */.ssh|*/.ssh/*)
    deny "Blocked by .agent/CONSTRAINTS.md: SSH key directories are forbidden." ;;
  */.aws|*/.aws/*)
    deny "Blocked by .agent/CONSTRAINTS.md: AWS credential directories are forbidden." ;;
esac

# Everything below guards modifications only.
[ "$TOOL_NAME" = "Read" ] && exit 0

# Forbidden directories (hard block) — .agent/CONSTRAINTS.md "Directory Boundaries"
case "$FILE_PATH" in
  ../*|*/../*)
    deny "Blocked by .agent/CONSTRAINTS.md: path traverses outside the repository root." ;;
esac
case "$P" in
  /etc|/etc/*|/private/etc|/private/etc/*)
    deny "Blocked by .agent/CONSTRAINTS.md: /etc/ is a forbidden directory." ;;
esac

# Home folders outside the project (Linux /home, macOS /Users), including other projects'
# .claude/ folders. The only exemption is your own Claude Code memory folder.
# A path counts as outside the project if EITHER form is outside: a symlink inside the repo
# (docs/notes -> ~/.bashrc) is inside as written but outside once resolved. The resolved
# forms of the file and the project are compared with each other, so a project that lives
# under a symlinked folder (macOS /home) still counts as inside.
in_homes() {
  case "$1" in /home/*|/users/*|/system/volumes/data/home/*|/system/volumes/data/users/*) return 0 ;; esac
  [ -n "$H" ] && case "$1" in "$H"/*) return 0 ;; esac          # your own home, wherever it is
  [ -n "$HN" ] && case "$1" in "$HN"/*) return 0 ;; esac
  return 1
}
# Claude Code's auto memory for THIS project: ~/.claude/projects/<project>/memory/, where
# <project> comes from the git repository root (shared by subfolders and worktrees), or the
# working directory outside a repo, or CLAUDE_CODE_PROJECT_DIR_NAME. Memory is loaded into
# every later session of its project, so writing another project's memory is a persistent
# prompt injection: only this project's folder is exempt. The name encoding isn't
# documented ("/" becomes "-"), so both likely encodings are accepted.
own_memory() {
  [ -n "$H" ] || return 1
  local slug
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    slug="$(lower "$slug")"
    [[ "$P" == "$H/.claude/projects/$slug/memory/"* ]] && return 0
  done < <(python3 -c 'import os, re, subprocess, sys
cwd = sys.argv[1]
root = cwd
try:
    out = subprocess.run(["git", "-C", cwd, "rev-parse", "--git-common-dir"],
                         capture_output=True, text=True, timeout=3)
    if out.returncode == 0 and out.stdout.strip():
        d = os.path.normpath(os.path.join(cwd, out.stdout.strip()))
        root = os.path.dirname(d) if os.path.basename(d) == ".git" else d
except (OSError, subprocess.SubprocessError):
    pass
names = set()
if os.environ.get("CLAUDE_CODE_PROJECT_DIR_NAME"):
    names.add(os.environ["CLAUDE_CODE_PROJECT_DIR_NAME"])
for r in {root, os.path.realpath(root)}:
    names.add(re.sub(r"[^A-Za-z0-9]", "-", r))
    names.add(r.replace("/", "-"))
print("\n".join(n for n in names if "/" not in n and n not in (".", "..")))' "${CWD:-$PWD}" 2>/dev/null)
  return 1
}
if { in_homes "$N" || in_homes "$P"; } && [ -n "$C" ] && [[ "$P" != "$C"/* || "$N" != "$CN"/* ]]; then
  # The memory exemption needs the RESOLVED path inside this project's own memory folder.
  own_memory || deny "Blocked by .agent/CONSTRAINTS.md: file is outside the current working directory, or a link inside it points outside."
fi

# Guardrails (hard block) — ASI10 Rogue Agents: an agent must not be able to switch off
# the controls that watch it: Claude Code settings and hooks, installed plugins (which
# include these hooks) and git hooks.
case "$P" in
  */.claude/settings.json|*/.claude/settings.local.json)
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change their own permission or hook settings. Ask the human to edit this file." ;;
  */.claude/hooks/*|*/.claude/plugins/*)
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change the hooks or plugins that enforce their rules. Ask the human to edit this file." ;;
  */.git/hooks/*)
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change git hooks. Ask the human to edit this file." ;;
  */.git/config|*/.git/info/*)
    # core.hooksPath turns off pre-commit checks; core.fsmonitor, aliases or sshCommand run
    # commands the next time a human uses git, outside any sandbox.
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change git configuration. Ask the human to edit this file." ;;
esac

# Governance rules and instruction-bearing files (requires approval) — Non-Negotiable
# Rule 8. Agent, skill, command and rule files carry instructions (and can declare
# hooks), so planting one is a persistent prompt injection.
case "$BASENAME" in
  agents.md|claude.md|claude.local.md|gemini.md|.cursorrules|copilot-instructions.md|codeowners|.pre-commit-config.yaml|.pre-commit-config.yml)
    ask "Requires approval per AGENTS.md rule 8: governance and guardrail files change only when the human asked." ;;
esac
case "$P" in
  */.agent/*|*/.cursor/rules/*|*/.github/instructions/*|*/.claude-plugin/*)
    ask "Requires approval per AGENTS.md rule 8: governance files change only when the human asked." ;;
  */.claude/agents/*|*/.claude/skills/*|*/.claude/commands/*|*/.claude/rules/*|*/.claude/output-styles/*)
    ask "Requires approval per AGENTS.md rule 8: agent, skill, command and rule files carry instructions." ;;
esac

# Protected files (requires approval) — .agent/CONSTRAINTS.md "File Modification Rules"
case "$BASENAME" in
  .env*)
    ask "Requires approval per .agent/CONSTRAINTS.md: environment files are protected." ;;
  *.pem|*.key)
    ask "Requires approval per .agent/CONSTRAINTS.md: certificate/key files are protected." ;;
  docker-compose*.yml|dockerfile*)
    ask "Requires approval per .agent/CONSTRAINTS.md: container orchestration files are protected." ;;
esac

case "$P" in
  */config/prod*)
    ask "Requires approval per .agent/CONSTRAINTS.md: production configuration is protected." ;;
  */.github/workflows/*)
    ask "Requires approval per .agent/CONSTRAINTS.md: CI/CD pipeline files are protected." ;;
esac

exit 0
