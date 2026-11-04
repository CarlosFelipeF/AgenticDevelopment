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

# Credential directories: hard deny for every matched tool, reads included.
case "$FILE_PATH" in
  ~/.ssh/*|*/.ssh/*)
    deny "Blocked by .agent/CONSTRAINTS.md: SSH key directories are forbidden." ;;
  ~/.aws/*|*/.aws/*)
    deny "Blocked by .agent/CONSTRAINTS.md: AWS credential directories are forbidden." ;;
esac

# Everything below guards modifications only.
[ "$TOOL_NAME" = "Read" ] && exit 0

# Forbidden directories (hard block) — .agent/CONSTRAINTS.md "Directory Boundaries"
case "$FILE_PATH" in
  ../*|*/../*)
    deny "Blocked by .agent/CONSTRAINTS.md: path traverses outside the repository root." ;;
  /etc/*|/etc)
    deny "Blocked by .agent/CONSTRAINTS.md: /etc/ is a forbidden directory." ;;
esac

# Other users' and your own home files outside the project (Linux /home, macOS /Users).
# Claude Code's own .claude/ folder is exempt here — its memory feature writes there — and
# the guardrail block below still stops writes to its settings, hooks and plugins.
if [[ ( "$FILE_PATH" = /home/* || "$FILE_PATH" = /Users/* ) && -n "$CWD" \
      && "$FILE_PATH" != "$CWD"/* && "$FILE_PATH" != */.claude/* ]]; then
  deny "Blocked by .agent/CONSTRAINTS.md: file is outside the current working directory."
fi

BASENAME="$(basename "$FILE_PATH")"

# Guardrails (hard block) — ASI10 Rogue Agents: an agent must not be able to switch off
# the controls that watch it. Covers project settings and hooks, installed plugins (which
# include these hooks) and git hooks. Other ~/.claude/ paths stay writable on purpose:
# Claude Code's memory feature writes there.
case "$FILE_PATH" in
  .claude/settings.json|*/.claude/settings.json|.claude/settings.local.json|*/.claude/settings.local.json)
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change their own permission or hook settings. Ask the human to edit this file." ;;
  .claude/hooks/*|*/.claude/hooks/*|*/.claude/plugins/*)
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change the hooks or plugins that enforce their rules. Ask the human to edit this file." ;;
  .git/hooks/*|*/.git/hooks/*)
    deny "Blocked by .agent/CONSTRAINTS.md: agents may not change git hooks. Ask the human to edit this file." ;;
esac

# Governance rules (requires approval) — Non-Negotiable Rule 8: agents edit these only
# when the human asked, so the human confirms each edit.
case "$BASENAME" in
  AGENTS.md|CLAUDE.md|CLAUDE.local.md|GEMINI.md|.cursorrules|copilot-instructions.md|CODEOWNERS|.pre-commit-config.yaml|.pre-commit-config.yml)
    ask "Requires approval per AGENTS.md rule 8: governance and guardrail files change only when the human asked." ;;
esac
case "$FILE_PATH" in
  .agent/*|*/.agent/*|.cursor/rules/*|*/.cursor/rules/*|.github/instructions/*|*/.github/instructions/*)
    ask "Requires approval per AGENTS.md rule 8: governance files change only when the human asked." ;;
esac

# Protected files (requires approval) — .agent/CONSTRAINTS.md "File Modification Rules"
case "$BASENAME" in
  .env*)
    ask "Requires approval per .agent/CONSTRAINTS.md: environment files are protected." ;;
  *.pem|*.key)
    ask "Requires approval per .agent/CONSTRAINTS.md: certificate/key files are protected." ;;
  docker-compose*.yml|Dockerfile*)
    ask "Requires approval per .agent/CONSTRAINTS.md: container orchestration files are protected." ;;
esac

case "$FILE_PATH" in
  */config/prod*)
    ask "Requires approval per .agent/CONSTRAINTS.md: production configuration is protected." ;;
  */.github/workflows/*)
    ask "Requires approval per .agent/CONSTRAINTS.md: CI/CD pipeline files are protected." ;;
esac

exit 0
