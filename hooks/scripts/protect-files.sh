#!/usr/bin/env bash
# PreToolUse hook (matcher: Write|Edit) — enforces .agent/CONSTRAINTS.md's
# "Protected files" (ask) and "Forbidden directories" (deny) rules.
set -euo pipefail

INPUT="$(cat)"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"
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

# Forbidden directories (hard block) — .agent/CONSTRAINTS.md "Directory Boundaries"
case "$FILE_PATH" in
  ../*|*/../*)
    deny "Blocked by .agent/CONSTRAINTS.md: path traverses outside the repository root." ;;
  /etc/*|/etc)
    deny "Blocked by .agent/CONSTRAINTS.md: /etc/ is a forbidden directory." ;;
  ~/.ssh/*|*/.ssh/*)
    deny "Blocked by .agent/CONSTRAINTS.md: SSH key directories are forbidden." ;;
  ~/.aws/*|*/.aws/*)
    deny "Blocked by .agent/CONSTRAINTS.md: AWS credential directories are forbidden." ;;
esac

if [[ "$FILE_PATH" = /home/* && -n "$CWD" && "$FILE_PATH" != "$CWD"/* ]]; then
  deny "Blocked by .agent/CONSTRAINTS.md: file is outside the current working directory."
fi

BASENAME="$(basename "$FILE_PATH")"

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
