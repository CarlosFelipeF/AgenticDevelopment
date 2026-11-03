#!/usr/bin/env bash
# self-test.sh — verify this framework repository before committing or releasing.
#
# Usage: scripts/self-test.sh
# Runs : syntax checks, the guard hook's adversarial test suite, config validation,
#        internal link checks and agent-doctor. Changes no tracked files; needs bash, git, python3.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

failed=0
logs="$(mktemp -d)"
trap 'rm -rf "$logs"' EXIT
step() { printf '\n== %s\n' "$1"; }
ok()   { printf '   ok   %s\n' "$1"; }
bad()  { printf '   FAIL %s\n' "$1"; failed=$((failed + 1)); }

step "Shell syntax"
for f in scripts/*.sh; do
  bash -n "$f" && ok "$f" || bad "$f"
done
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -S warning scripts/*.sh && ok "shellcheck" || bad "shellcheck"
else
  printf '   skip shellcheck (not installed)\n'
fi

step "Python syntax"
python3 - <<'PY' && ok "guard-bash.py and tests compile" || bad "python compile"
import ast, sys
for path in ("examples/enforcement/claude/hooks/guard-bash.py", "tests/test_guard_bash.py"):
    ast.parse(open(path).read(), path)
PY

step "Guard hook adversarial tests"
if python3 -m unittest discover -s tests >"$logs/unittest.log" 2>&1; then
  ok "$(grep -E '^Ran ' "$logs/unittest.log")"
else
  cat "$logs/unittest.log"
  bad "unit tests"
fi

step "Config files parse"
while IFS= read -r f; do
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" && ok "$f" || bad "$f"
done < <(git ls-files --cached --others --exclude-standard '*.json')
if python3 -c "import yaml" 2>/dev/null; then
  while IFS= read -r f; do
    python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "$f" && ok "$f" || bad "$f"
  done < <(git ls-files --cached --others --exclude-standard '*.yml' '*.yaml')
else
  printf '   skip YAML (PyYAML not installed)\n'
fi

step "Internal links and file references"
python3 - <<'PY' && ok "all internal references resolve" || bad "broken internal references"
import os, re, subprocess, sys
files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
                       capture_output=True, text=True).stdout.split()
missing = []
for md in files:
    text = open(md).read()
    if "TEMPLATE — replace with your project" in text:
        continue  # placeholder links are expected until the adopter fills the file in
    base = os.path.dirname(md)
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if re.match(r"^[a-z]+:", target):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            missing.append("%s -> %s" % (md, target))
    for ref in re.findall(r"`((?:examples|scripts|\.agent)/[A-Za-z0-9_./-]+)`", text):
        if not os.path.exists(ref.rstrip("/")):
            missing.append("%s -> %s" % (md, ref))
for m in missing:
    print("   missing:", m)
sys.exit(1 if missing else 0)
PY

step "Framework version is consistent"
v_agents="$(grep -oE 'Framework v[0-9]+\.[0-9]+\.[0-9]+' AGENTS.md | head -1 | tr -d 'Framework v')"
v_change="$(grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1 | tr -d '#[] ')"
v_readme="$(grep -oE 'Framework-v[0-9]+\.[0-9]+\.[0-9]+' README.md | head -1 | sed 's/Framework-v//')"
if [ -n "$v_agents" ] && [ "$v_agents" = "$v_change" ] && [ "$v_agents" = "$v_readme" ]; then
  ok "v$v_agents in AGENTS.md, README.md and CHANGELOG.md"
else
  bad "version mismatch: AGENTS.md=$v_agents README.md=$v_readme CHANGELOG.md=$v_change"
fi

step "agent-doctor"
if scripts/agent-doctor.sh >"$logs/doctor.log" 2>&1; then
  ok "$(tail -1 "$logs/doctor.log")"
else
  cat "$logs/doctor.log"
  bad "agent-doctor reported failures"
fi

printf '\n%s\n' "$([ "$failed" -eq 0 ] && echo 'ALL CHECKS PASSED' || echo "$failed CHECK(S) FAILED")"
[ "$failed" -eq 0 ]
