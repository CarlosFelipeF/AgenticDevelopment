#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash) — enforces .agent/CONSTRAINTS.md "Hard Blocks":
# force push, direct push to main/master, and rm -rf outside the project.
set -euo pipefail

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

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

[ -z "$COMMAND" ] && exit 0

if printf '%s' "$COMMAND" | grep -qE '^\s*git\s+push(\s+.*)?\s+(--force\b|-f\b)'; then
  deny "Blocked by .agent/CONSTRAINTS.md: force push to any shared branch is a hard block."
fi

if printf '%s' "$COMMAND" | grep -qE '^\s*git\s+push(\s+\S+)*\s+(origin\s+)?(main|master)\s*$'; then
  deny "Blocked by .agent/CONSTRAINTS.md: direct push to main/master is a hard block."
fi

if printf '%s' "$COMMAND" | grep -qE '\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)\s+(/|~|\$HOME|\.\./)'; then
  deny "Blocked by .agent/CONSTRAINTS.md: rm -rf outside the project directory is a hard block."
fi

exit 0
