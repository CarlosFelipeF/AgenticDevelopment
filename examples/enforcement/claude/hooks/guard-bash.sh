#!/usr/bin/env bash
# guard-bash.sh — Claude Code PreToolUse hook (defence in depth, not a sandbox).
#
# Blocks shell commands that break the "Never" rules in .agent/CONSTRAINTS.md.
# Pattern matching can be bypassed by a determined attacker; pair it with the
# permission deny-list in settings.json, a sandbox, and CI checks.
#
# Install: copy to .claude/hooks/guard-bash.sh and `chmod +x` it.
# Exit 2 = block (stderr is shown to the agent). Exit 0 = normal permission flow.
set -euo pipefail

input="$(cat)"

if command -v jq >/dev/null 2>&1; then
  cmd="$(jq -r '.tool_input.command // empty' <<<"$input")"
elif command -v python3 >/dev/null 2>&1; then
  cmd="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' <<<"$input")"
else
  echo "guard-bash: need jq or python3 to inspect commands; blocking to fail secure." >&2
  exit 2
fi

block() {
  echo "Blocked by guard-bash: $1. See .agent/CONSTRAINTS.md. Ask the human if this is really needed." >&2
  exit 2
}

# Downloaded content piped into a shell or interpreter (ASI05).
if grep -Eq '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z|da)?sh\b|(curl|wget)[^|]*\|[[:space:]]*(python|node|perl|ruby)' <<<"$cmd"; then
  block "piping downloaded content into a shell or interpreter"
fi

# Skipping hooks or forcing history changes.
if grep -Eq -- '--no-verify|git[[:space:]]+push[^;&|]*(--force|[[:space:]]-f\b)|git[[:space:]]+push[^;&|]*\+[A-Za-z0-9_./-]+' <<<"$cmd"; then
  block "skipping git hooks or force-pushing"
fi

# Direct pushes to main/master.
if grep -Eq 'git[[:space:]]+push[^;&|]*[[:space:]:](main|master)\b' <<<"$cmd"; then
  block "pushing directly to main/master"
fi

# Reading secret files through the shell (the Read deny-list does not cover `cat`).
if grep -Eq '(cat|less|more|head|tail|bat|cp|scp|base64|xxd)[[:space:]][^;&|]*(\.env($|[^.a-zA-Z])|\.env\.(local|prod|production|dev|development|staging)|id_rsa|id_ed25519|\.pem\b|\.aws/credentials)' <<<"$cmd"; then
  block "reading a secret file"
fi

# Dangerous deletes: root, home, parent dirs, or unchecked variables.
if grep -Eq 'rm[[:space:]]+(-[a-zA-Z]*[rR][a-zA-Z]*[[:space:]]+)+(/|~|\.\.|\$HOME|"?\$\{?[A-Za-z_]+\}?"?/?)([[:space:]]|$)' <<<"$cmd"; then
  block "recursive delete of root, home, parent or a bare variable path"
fi

# Privilege escalation.
if grep -Eq '(^|[;&|[:space:]])sudo[[:space:]]' <<<"$cmd"; then
  block "privilege escalation"
fi

exit 0
