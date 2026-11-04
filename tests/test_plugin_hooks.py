"""Tests for the plugin hooks in hooks/scripts/: the commit secret scan, secret writes, protected files.

Run:  python3 -m unittest discover -s tests -v
Needs: bash, git, jq (the hooks use jq to read their JSON input).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "hooks", "scripts")
FAKE_KEY = "sk-" + "a" * 24  # matches the provider-key pattern; not a real key


GUARD = os.path.join(SCRIPTS, "guard-bash.py")


def run_guard(command, cwd):
    res = subprocess.run([sys.executable, GUARD], input=json.dumps({"tool_input": {"command": command}, "cwd": cwd}),
                         capture_output=True, text=True, timeout=60)
    return res.returncode


# CI sets HOOK_BASH=/bin/bash on macOS to test with the bash 3.2 that ships there.
HOOK_BASH = os.environ.get("HOOK_BASH", "bash")


def run(script, payload, cwd, home=None):
    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": ROOT}
    if home:
        env["HOME"] = home
    res = subprocess.run([HOOK_BASH, os.path.join(SCRIPTS, script)], input=json.dumps(payload),
                         capture_output=True, text=True, cwd=cwd, timeout=30, env=env)
    decision = ""
    if res.stdout.strip():
        decision = json.loads(res.stdout)["hookSpecificOutput"]["permissionDecision"]
    return res.returncode, decision


class SecretCommitTest(unittest.TestCase):
    """The commit secret scan in guard-bash.py.

    Includes regressions for bypasses in the old block-secret-commit.sh found in PR #4's
    review: early-exit pipes on large diffs, quoted -C paths, bash -c wrappers, and
    -s swallowing -n.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "my repo")  # a space on purpose
        subprocess.run(["git", "init", "-q", "-b", "feat", self.repo], check=True)
        self.write("cfg.py", 'key = "%s"\n' % FAKE_KEY)
        self.git("add", "cfg.py")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        with open(os.path.join(self.repo, name), "w") as fh:
            fh.write(text)

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, "-c", "user.email=t@example.com", "-c", "user.name=t"] + list(args),
                       check=True, capture_output=True)

    def decide(self, command, cwd=None):
        return run_guard(command, cwd or self.repo)

    def test_blocks_commit_of_staged_secret(self):
        for cmd in ("git commit -m x", "cd . && git commit -m x", "git status; git commit -am x",
                    "git commit -s -m x", "bash -c 'git commit -m x'", 'echo "$(git commit -m x)"'):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.decide(cmd), 2)

    def test_quoted_and_relative_repo_paths(self):
        parent = self.tmp.name
        for cmd in ('git -C "%s" commit -m x' % self.repo, "git -C 'my repo' commit -m x",
                    'cd "my repo" && git commit -m x'):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.decide(cmd, parent), 2)

    def test_secret_before_a_large_diff(self):
        self.write("big.txt", "ordinary line\n" * 100000)
        self.git("add", "big.txt")
        self.assertEqual(self.decide("git commit -m x"), 2)

    def test_worktree_commits_scan_unstaged_changes(self):
        self.git("commit", "-q", "--no-verify", "-m", "seed")  # test setup, outside the hook
        self.write("cfg.py", 'key = "%s"\nmore = 1\n' % FAKE_KEY.replace("a", "b"))
        self.assertEqual(self.decide("git commit -m x"), 0)   # nothing staged: index is clean
        self.assertEqual(self.decide("git commit -am x"), 2)  # -a records the worktree
        self.assertEqual(self.decide("git commit -m x cfg.py"), 2)  # pathspec too

    def test_removing_a_leaked_secret_is_allowed(self):
        self.git("commit", "-q", "--no-verify", "-m", "leak")
        self.write("cfg.py", 'key = os.environ["API_KEY"]\n')
        self.git("add", "cfg.py")
        self.assertEqual(self.decide("git commit -m 'remove leaked key'"), 0)

    def test_fails_closed_when_it_cannot_scan(self):
        self.assertEqual(self.decide("git -C /nonexistent/repo commit -m x"), 2)

    def test_signoff_does_not_hide_no_verify(self):
        self.write("cfg.py", "print('clean')\n")
        self.git("add", "cfg.py")
        self.assertEqual(self.decide("git commit -s -n -m x"), 2)

    def test_allows_clean_commit_and_other_commands(self):
        self.write("cfg.py", 'key = os.environ["API_KEY"]\n')
        self.git("add", "cfg.py")
        for cmd in ("git commit -m x", "git status", "git log --oneline", "echo commit"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.decide(cmd), 0)


@unittest.skipUnless(shutil.which("jq"), "jq is required by the plugin hooks")
class SecretWriteAndProtectedFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_blocks_writing_a_secret(self):
        payload = {"tool_name": "Write", "cwd": self.cwd,
                   "tool_input": {"file_path": os.path.join(self.cwd, "a.py"), "content": 'k = "%s"' % FAKE_KEY}}
        self.assertEqual(run("block-secret-write.sh", payload, self.cwd), (0, "deny"))

    def test_allows_writing_normal_code(self):
        payload = {"tool_name": "Write", "cwd": self.cwd,
                   "tool_input": {"file_path": os.path.join(self.cwd, "a.py"), "content": "print('hi')"}}
        self.assertEqual(run("block-secret-write.sh", payload, self.cwd), (0, ""))

    def test_blocks_reading_ssh_keys(self):
        payload = {"tool_name": "Read", "cwd": self.cwd,
                   "tool_input": {"file_path": os.path.expanduser("~/.ssh/id_ed25519")}}
        self.assertEqual(run("protect-files.sh", payload, self.cwd), (0, "deny"))

    def file_decision(self, tool, rel_path):
        path = rel_path if os.path.isabs(rel_path) else os.path.join(self.cwd, rel_path)
        payload = {"tool_name": tool, "cwd": self.cwd, "tool_input": {"file_path": path}}
        return run("protect-files.sh", payload, self.cwd)

    def test_blocks_edits_to_guardrails(self):
        home = os.path.expanduser("~")
        for path in (".claude/settings.json", ".claude/settings.local.json", ".claude/hooks/guard-bash.py",
                     ".git/hooks/pre-commit",
                     os.path.join(home, ".claude/plugins/cache/x/hooks/scripts/guard-bash.py")):
            for tool in ("Write", "Edit"):
                with self.subTest(path=path, tool=tool):
                    self.assertEqual(self.file_decision(tool, path), (0, "deny"))

    def test_asks_before_editing_governance_rules(self):
        for path in ("AGENTS.md", "packages/api/AGENTS.md", "CLAUDE.md", ".agent/CONSTRAINTS.md",
                     ".cursor/rules/agents.mdc", ".github/CODEOWNERS", ".pre-commit-config.yaml"):
            with self.subTest(path=path):
                self.assertEqual(self.file_decision("Edit", path), (0, "ask"))

    def test_governance_files_stay_readable_and_memory_stays_writable(self):
        for path in ("AGENTS.md", ".agent/SECURITY.md", ".claude/settings.json"):
            with self.subTest(read=path):
                self.assertEqual(self.file_decision("Read", path), (0, ""))
        memory = os.path.join(os.path.expanduser("~"), ".claude/projects/x/memory/notes.md")
        self.assertEqual(self.file_decision("Write", memory), (0, ""))
        self.assertEqual(self.file_decision("Write", "src/app.py"), (0, ""))

    def test_home_paths_outside_project(self):
        def decide(path, cwd, home):
            payload = {"tool_name": "Write", "cwd": cwd, "tool_input": {"file_path": path}}
            return run("protect-files.sh", payload, self.cwd, home=home)[1]
        for home in ("/home/tester", "/Users/tester"):
            proj = home + "/proj"
            with self.subTest(home=home):
                self.assertEqual(decide(home + "/.claude/projects/p/memory/notes.md", proj, home), "")
                self.assertEqual(decide(home + "/.claude/plugins/c/hooks/scripts/guard-bash.py", proj, home), "deny")
                self.assertEqual(decide(home + "/.claude/settings.json", proj, home), "deny")
                self.assertEqual(decide(home + "/other/file.txt", proj, home), "deny")
                self.assertEqual(decide(proj + "/src/app.py", proj, home), "")
                # PR #5 security review: the .claude/ exemption was wider than memory.
                for planted in ("/.claude/agents/evil.md", "/.claude/skills/x/SKILL.md",
                                "/.claude/commands/x.md", "/.claude/CLAUDE.md"):
                    self.assertEqual(decide(home + planted, proj, home), "deny", planted)
                self.assertEqual(decide("/home/other/proj2/.claude/commands/x.md", proj, home), "deny")
                self.assertEqual(decide("/home/other/.claude/projects/p/memory/x.md", proj, home), "deny")

    def test_equivalent_spellings_of_guardrail_paths(self):
        # PR #5 security review: raw-string matching let these through.
        for path in (".claude/./settings.json", ".claude//settings.json", ".git/hooks/./pre-commit",
                     ".claude/Settings.json", ".claude/HOOKS/x.sh", "sub/../.claude/settings.json",
                     "./.claude/settings.local.json"):
            with self.subTest(path=path):
                self.assertEqual(self.file_decision("Write", path), (0, "deny"))
        for path in ("Agents.md", ".AGENT/SECURITY.md", ".claude/skills/x/SKILL.md"):
            with self.subTest(path=path):
                self.assertEqual(self.file_decision("Edit", path), (0, "ask"))

    def test_symlinked_path_to_a_guardrail(self):
        os.makedirs(os.path.join(self.cwd, ".claude"))
        os.symlink(os.path.join(self.cwd, ".claude"), os.path.join(self.cwd, "innocent"))
        self.assertEqual(self.file_decision("Write", "innocent/settings.json"), (0, "deny"))

    def test_allows_reading_project_files(self):
        payload = {"tool_name": "Read", "cwd": self.cwd,
                   "tool_input": {"file_path": os.path.join(self.cwd, "README.md")}}
        self.assertEqual(run("protect-files.sh", payload, self.cwd), (0, ""))


if __name__ == "__main__":
    unittest.main()
