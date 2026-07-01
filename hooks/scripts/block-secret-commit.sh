#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash) — enforces .agent/SECURITY.md "Never commit" list
# by scanning staged changes before a `git commit` is allowed to run.
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./secret-patterns.sh
source "$HOOK_DIR/secret-patterns.sh"

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

[ -z "$COMMAND" ] && exit 0
printf '%s' "$COMMAND" | grep -qE '^\s*git\s+commit\b' || exit 0

if git diff --cached | grep -qE -e "$SECRET_PATTERN"; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked by .agent/SECURITY.md: staged changes appear to contain a secret (API key, private key, password, or connection string). Use an environment variable or secret manager instead, then retry the commit."
    }
  }'
fi

exit 0
