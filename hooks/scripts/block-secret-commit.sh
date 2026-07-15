#!/usr/bin/env bash
# PreToolUse hook (matcher: Bash) — enforces .agent/SECURITY.md "Never commit" list
# by scanning the changes a `git commit` is about to record.
#
# Command segments are checked individually (same approach as
# block-destructive-git.sh) so `cd subdir && git commit` and
# `git -C /repo commit` forms can't skip the scan. Plain `git commit` records
# the index, so only the staged diff is scanned; `-a`/`--all` and pathspec
# commits also record working-tree content, so those scan `git diff HEAD` too.
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./secret-patterns.sh
source "$HOOK_DIR/secret-patterns.sh"

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"
[ -z "$COMMAND" ] && exit 0

deny() {
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Blocked by .agent/SECURITY.md: the changes this commit would record appear to contain a secret (API key, private key, password, or connection string). Use an environment variable or secret manager instead, then retry the commit."
    }
  }'
  exit 0
}

GIT_COMMIT='^\s*git(\s+(-C|-c|--git-dir|--work-tree|--namespace)\s+\S+|\s+--?\S+)*\s+commit(\s|$)'

mapfile -t SEGMENTS < <(printf '%s\n' "$COMMAND" | sed -E 's/&&|\|\||;|\|/\n/g')

for seg in "${SEGMENTS[@]}"; do
  printf '%s' "$seg" | grep -qE "$GIT_COMMIT" || continue

  # `git -C <path> commit` must be scanned in that repo, not the hook's cwd.
  GITDIR_ARGS=()
  C_PATH="$(printf '%s' "$seg" | grep -oE '(^|[[:space:]])git[[:space:]]+-C[[:space:]]+[^[:space:]]+' | awk '{print $NF}' || true)"
  [ -n "$C_PATH" ] && GITDIR_ARGS=(-C "$C_PATH")

  SCAN_WORKTREE=false
  if printf '%s' "$seg" | grep -qE '\s(-[a-zA-Z]*a[a-zA-Z]*|--all)(\s|$)'; then
    SCAN_WORKTREE=true
  else
    # Pathspec heuristic: a non-option token after `commit` that looks like a
    # path (contains . or /), skipping message/file option arguments. Erring
    # toward scanning more is safe — worst case is a deny the user can review.
    read -ra WORDS <<< "$(printf '%s' "$seg" | sed -E 's/.*[[:space:]]commit([[:space:]]|$)//')"
    skip_next=false
    for w in "${WORDS[@]}"; do
      if [ "$skip_next" = true ]; then skip_next=false; continue; fi
      case "$w" in
        -m|--message|-F|--file) skip_next=true ;;
        -*) ;;
        *[./]*) SCAN_WORKTREE=true; break ;;
      esac
    done
  fi

  if git "${GITDIR_ARGS[@]}" diff --cached 2>/dev/null | grep -qE -e "$SECRET_PATTERN"; then
    deny
  fi
  if [ "$SCAN_WORKTREE" = true ] && git "${GITDIR_ARGS[@]}" diff HEAD 2>/dev/null | grep -qE -e "$SECRET_PATTERN"; then
    deny
  fi
done

exit 0
