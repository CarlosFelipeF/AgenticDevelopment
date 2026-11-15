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
for f in scripts/*.sh hooks/scripts/*.sh; do
  bash -n "$f" && ok "$f" || bad "$f"
done
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck -S warning scripts/*.sh hooks/scripts/*.sh && ok "shellcheck" || bad "shellcheck"
else
  printf '   skip shellcheck (not installed)\n'
fi

step "Python syntax"
python3 - <<'PY' && ok "hook scripts and tests compile" || bad "python compile"
import ast, sys
for path in ("hooks/scripts/guard-bash.py", "hooks/scripts/protect-files.py", "hooks/scripts/pathpolicy.py",
             "tests/test_guard_bash.py", "tests/test_plugin_hooks.py"):
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

step "GitHub Actions pinned to commit SHAs"
unpinned="$(grep -rhnE '^[[:space:]]*-?[[:space:]]*uses:' .github/workflows examples/enforcement/github 2>/dev/null \
  | grep -vE 'uses:[[:space:]]*([^@[:space:]]+@[0-9a-f]{40}([[:space:]]|$)|\./)' || true)"  # ./local actions can't be pinned
if [ -z "$unpinned" ]; then
  ok "every uses: is pinned to a full commit SHA"
else
  printf '   unpinned: %s\n' "$unpinned"
  bad "unpinned GitHub Actions (tags can be moved; pin to a SHA with a # vX.Y.Z comment)"
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
v_plugin="$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")"
if [ -n "$v_agents" ] && [ "$v_agents" = "$v_change" ] && [ "$v_agents" = "$v_readme" ] && [ "$v_agents" = "$v_plugin" ]; then
  ok "v$v_agents in AGENTS.md, README.md, CHANGELOG.md and plugin.json"
else
  bad "version mismatch: AGENTS.md=$v_agents README.md=$v_readme CHANGELOG.md=$v_change plugin.json=$v_plugin"
fi

step "Plugin wiring"
python3 - <<'PY' && ok "hooks.json scripts exist; every skill has a description" || bad "plugin wiring"
import json, os, re, sys
errors = []
for event in json.load(open("hooks/hooks.json"))["hooks"].values():
    for group in event:
        for hook in group["hooks"]:
            for path in re.findall(r"hooks/scripts/[\w.-]+", hook["command"]):
                if not os.path.isfile(path):
                    errors.append("hooks.json -> missing " + path)
for name in sorted(os.listdir("skills")):
    text = open(os.path.join("skills", name, "SKILL.md")).read()
    if not re.match(r"---\n(.*\n)*?description: .+\n(.*\n)*?---\n", text):
        errors.append("skills/%s/SKILL.md has no description front matter" % name)
for e in errors:
    print("   ", e)
sys.exit(1 if errors else 0)
PY

step "Plugin smoke-test script"
if smoke_out="$(TMPDIR="$logs" scripts/plugin-smoke-test.sh setup 2>&1)"; then
  smoke_dir="$(printf '%s\n' "$smoke_out" | sed -n 's/^Sandbox ready: //p')"
  mkdir -p "$smoke_dir/src" && printf 'print("hello")\n' > "$smoke_dir/src/hello.py"   # the control step
  if scripts/plugin-smoke-test.sh check "$smoke_dir" >"$logs/smoke.log" 2>&1; then
    ok "setup + check on an untouched sandbox: $(tail -1 "$logs/smoke.log")"
  else
    cat "$logs/smoke.log"; bad "plugin-smoke-test.sh check"
  fi
else
  printf '%s\n' "$smoke_out"; bad "plugin-smoke-test.sh setup"
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
