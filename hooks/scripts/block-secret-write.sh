#!/usr/bin/env bash
# PreToolUse hook (matcher: Write|Edit|NotebookEdit) — enforces .agent/SECURITY.md
# "Never commit" list before a secret ever lands on disk, not just at commit time.
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./secret-patterns.sh
source "$HOOK_DIR/secret-patterns.sh"

INPUT="$(cat)"
CONTENT="$(printf '%s' "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // .tool_input.new_source // empty')"

[ -z "$CONTENT" ] && exit 0

if printf '%s' "$CONTENT" | grep -qE -e "$SECRET_PATTERN"; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked by .agent/SECURITY.md: this write appears to contain a secret (API key, private key, password, or connection string). Use an environment variable or secret manager instead."
    }
  }'
fi

exit 0
