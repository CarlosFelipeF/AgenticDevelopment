#!/usr/bin/env bash
# agent-doctor.sh — check that a repository has the agent governance framework set up
# and that its rules are backed by real enforcement.
#
# Usage:  scripts/agent-doctor.sh [path-to-repo]     (default: current directory)
# Exit:   0 = no failures (warnings allowed), 1 = at least one failure
#
# Read-only: this script never changes files.
set -uo pipefail

repo="${1:-.}"
cd "$repo" || { echo "Cannot open $repo"; exit 1; }

fails=0; warns=0
if [ -t 1 ]; then G=$'\033[32m' Y=$'\033[33m' R=$'\033[31m' N=$'\033[0m'; else G='' Y='' R='' N=''; fi
pass() { printf '  %sPASS%s %s\n' "$G" "$N" "$1"; }
warn() { printf '  %sWARN%s %s\n' "$Y" "$N" "$1"; warns=$((warns + 1)); }
fail() { printf '  %sFAIL%s %s\n' "$R" "$N" "$1"; fails=$((fails + 1)); }

in_git=false
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && in_git=true
tracked() { $in_git && git ls-files -- "$@" 2>/dev/null; }

echo "Governance files"
[ -f AGENTS.md ] && pass "AGENTS.md present" || fail "AGENTS.md missing — agents have no entry point"
for f in SECURITY CONSTRAINTS PROJECT; do
  [ -f ".agent/$f.md" ] && pass ".agent/$f.md present" || fail ".agent/$f.md missing (always-load file)"
done
for f in WORKFLOW CONVENTIONS SESSIONS PROTOCOLS; do
  [ -f ".agent/$f.md" ] || warn ".agent/$f.md missing (load-on-demand file)"
done

echo "Customisation"
for f in .agent/PROJECT.md ARCHITECTURE.md TESTING.md GLOSSARY.md; do
  [ -f "$f" ] || continue
  if grep -q 'TEMPLATE — replace with your project' "$f"; then
    warn "$f still has the TEMPLATE banner — agents will treat it as illustrative only"
  else
    pass "$f customised"
  fi
done

echo "Tool adapters"
if [ -f CLAUDE.md ]; then
  grep -q '@AGENTS.md' CLAUDE.md && pass "CLAUDE.md imports AGENTS.md" \
    || warn "CLAUDE.md exists but does not import @AGENTS.md — rules may drift"
fi
if [ -f .github/copilot-instructions.md ]; then
  grep -q 'AGENTS.md' .github/copilot-instructions.md && pass "Copilot instructions reference AGENTS.md" \
    || warn ".github/copilot-instructions.md does not reference AGENTS.md"
fi
[ -f .cursorrules ] && warn ".cursorrules is a legacy format — prefer AGENTS.md or .cursor/rules/*.mdc"

echo "Secrets"
if [ -f .gitignore ] && grep -Eq '^\.env(\*|$)|^\.env\.\*' .gitignore; then
  pass ".gitignore excludes .env files"
else
  fail ".gitignore does not exclude .env files"
fi
leaked="$(tracked '.env' '*.env' '.env.*' '*.pem' '*.key' 'id_rsa' 'id_ed25519' | grep -Ev '\.example$|\.sample$|\.template$' || true)"
if [ -n "$leaked" ]; then
  fail "secret-like files are tracked by git: $(echo "$leaked" | tr '\n' ' ')"
else
  pass "no secret-like files tracked"
fi
if command -v gitleaks >/dev/null 2>&1 && $in_git; then
  if gitleaks git --redact --no-banner . >/dev/null 2>&1; then
    pass "gitleaks found no secrets in history"
  else
    fail "gitleaks found possible secrets — run 'gitleaks git --redact -v .' and rotate any real ones"
  fi
else
  warn "gitleaks not installed or not a git repo — history not scanned"
fi

echo "Enforcement (rules backed by controls)"
if [ -f .pre-commit-config.yaml ] && grep -Eq 'gitleaks|detect-secrets|trufflehog' .pre-commit-config.yaml; then
  pass "pre-commit secret scanning configured"
else
  warn "no pre-commit secret scanner — see examples/enforcement/pre-commit-config.yaml"
fi
if ls .github/workflows/*.y*ml >/dev/null 2>&1 && grep -lEq 'gitleaks|trufflehog|secret' .github/workflows/*.y*ml 2>/dev/null; then
  pass "CI runs a secret scan"
else
  warn "no CI secret scan — see examples/enforcement/github/agent-guardrails.yml"
fi
if [ -f .github/CODEOWNERS ] || [ -f CODEOWNERS ] || [ -f docs/CODEOWNERS ]; then
  grep -hq 'AGENTS.md\|\.agent/' .github/CODEOWNERS CODEOWNERS docs/CODEOWNERS 2>/dev/null \
    && pass "CODEOWNERS protects governance files" \
    || warn "CODEOWNERS does not cover AGENTS.md / .agent/"
else
  warn "no CODEOWNERS — governance changes can merge without a named reviewer"
fi
if [ -f .claude/settings.json ]; then
  grep -q '"deny"' .claude/settings.json && pass ".claude/settings.json has deny rules" \
    || warn ".claude/settings.json has no permission deny rules"
fi
if [ -f .claude/settings.json ] && grep -q 'guard-bash' .claude/settings.json; then
  [ -x .claude/hooks/guard-bash.sh ] && pass "guard-bash hook installed and executable" \
    || fail ".claude/settings.json references guard-bash.sh but it is missing or not executable"
fi

echo
echo "Result: $fails failure(s), $warns warning(s)"
[ "$fails" -eq 0 ]
