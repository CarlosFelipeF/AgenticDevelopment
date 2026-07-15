#!/usr/bin/env bash
# PreToolUse hook (matcher: Read|Write|Edit|NotebookEdit) — enforces
# .agent/CONSTRAINTS.md's "Protected files" (ask) and "Forbidden directories"
# (deny) rules.
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
