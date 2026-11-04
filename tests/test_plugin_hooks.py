"""Tests for the plugin's shell hooks in hooks/scripts/ (secret commit/write, protected files).

Run:  python3 -m unittest discover -s tests -v
Needs: bash, git, jq (the hooks use jq to read their JSON input).
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "hooks", "scripts")
FAKE_KEY = "sk-" + "a" * 24  # matches the provider-key pattern; not a real key


def run(script, payload, cwd):
    res = subprocess.run(["bash", os.path.join(SCRIPTS, script)], input=json.dumps(payload),
                         capture_output=True, text=True, cwd=cwd, timeout=30,
                         env={**os.environ, "CLAUDE_PLUGIN_ROOT": ROOT})
    decision = ""
    if res.stdout.strip():
        decision = json.loads(res.stdout)["hookSpecificOutput"]["permissionDecision"]
    return res.returncode, decision


@unittest.skipUnless(shutil.which("jq"), "jq is required by the plugin hooks")
class SecretCommitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        subprocess.run(["git", "init", "-q", "-b", "feat", self.repo], check=True)
        with open(os.path.join(self.repo, "cfg.py"), "w") as fh:
            fh.write('key = "%s"\n' % FAKE_KEY)
        subprocess.run(["git", "-C", self.repo, "add", "cfg.py"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def decide(self, command):
        return run("block-secret-commit.sh", {"tool_input": {"command": command}, "cwd": self.repo}, self.repo)

    def test_blocks_commit_of_staged_secret(self):
        for cmd in ("git commit -m x", "cd . && git commit -m x",
                    "git -C %s commit -m x" % self.repo, "git status; git commit -am x"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.decide(cmd), (0, "deny"))

    def test_ignores_non_commit_commands(self):
        for cmd in ("git status", "git log --oneline", "echo commit"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.decide(cmd), (0, ""))

    def test_allows_clean_commit(self):
        with open(os.path.join(self.repo, "cfg.py"), "w") as fh:
            fh.write('key = os.environ["API_KEY"]\n')
        subprocess.run(["git", "-C", self.repo, "add", "cfg.py"], check=True)
        self.assertEqual(self.decide("git commit -m x"), (0, ""))


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

    def test_allows_reading_project_files(self):
        payload = {"tool_name": "Read", "cwd": self.cwd,
                   "tool_input": {"file_path": os.path.join(self.cwd, "README.md")}}
        self.assertEqual(run("protect-files.sh", payload, self.cwd), (0, ""))


if __name__ == "__main__":
    unittest.main()
