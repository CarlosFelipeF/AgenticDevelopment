#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash) — enforces .agent/CONSTRAINTS.md "Hard Blocks":
# force push, direct push to main/master, and rm -rf outside the project.
#
# The command string is split on shell separators (&&, ||, ;, |, newline) and
# every segment is checked, so `cd /tmp && git push --force` can't slip past
# the anchors. Splitting ignores quoting, which can only cause false positives
# (a deny on a harmless command), never false negatives from the separators.
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

# `git` may carry global options before the subcommand (git -C /repo push,
# git -c key=val push, git --no-pager push).
GIT_PUSH='^\s*git(\s+(-C|-c|--git-dir|--work-tree|--namespace)\s+\S+|\s+--?\S+)*\s+push(\s|$)'

mapfile -t SEGMENTS < <(printf '%s\n' "$COMMAND" | sed -E 's/&&|\|\||;|\|/\n/g')

for seg in "${SEGMENTS[@]}"; do
  if printf '%s' "$seg" | grep -qE "$GIT_PUSH"; then
    if printf '%s' "$seg" | grep -qE '\s(--force(-with-lease(=\S*)?|-if-includes)?|-f)(\s|$)'; then
      deny "Blocked by .agent/CONSTRAINTS.md: force push to any shared branch is a hard block."
    fi
    # Bare branch args and refspec destinations (HEAD:main, feature:refs/heads/main).
    if printf '%s' "$seg" | grep -qE '\s((\S*:)?(refs/heads/)?(main|master))(\s|$)'; then
      deny "Blocked by .agent/CONSTRAINTS.md: direct push to main/master is a hard block."
    fi
  fi

  # rm with recursive + force flags (combined, separate, or long form) against
  # an absolute path, home directory, or parent-directory traversal.
  if printf '%s' "$seg" | grep -qE '(^|\s)rm(\s|$)' \
    && printf '%s' "$seg" | grep -qE '(^|\s)(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)(\s|$)' \
    && printf '%s' "$seg" | grep -qE '(^|\s)(-[a-zA-Z]*f[a-zA-Z]*|--force)(\s|$)' \
    && printf '%s' "$seg" | grep -qE '\s(/|~|\$HOME|\.\.(/|\s|$))'; then
    deny "Blocked by .agent/CONSTRAINTS.md: rm -rf outside the project directory is a hard block."
  fi
done

exit 0
