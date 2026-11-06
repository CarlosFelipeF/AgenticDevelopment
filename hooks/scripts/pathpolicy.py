"""pathpolicy — shared file-path rules for the plugin hooks.

Used by protect-files.py (Read/Write/Edit/NotebookEdit) and guard-bash.py (shell writes).
One implementation, one test suite: tests/test_plugin_hooks.py and tests/test_guard_bash.py.

Every check runs on canonical paths, never the raw string:
- resolved (`real`): made absolute against the working directory, "." and "//" collapsed,
  symlinks resolved. Used for "what file is this really?" (guardrail and governance rules).
- normalised (`norm`): absolute and collapsed, symlinks kept. Used for "where does this sit?"
  (macOS links /home to /System/Volumes/Data/home, so prefix checks need the written form).
Both are lowercased: macOS disks are case-insensitive, so ".claude/Settings.json" is the same
file. On Linux that can only add an approval prompt, never remove a block.

Python 3.8+, standard library only.
"""
import os
import re
import subprocess

ALLOW, ASK, DENY = "", "ask", "deny"

GOVERNANCE_BASENAMES = {
    "agents.md", "claude.md", "claude.local.md", "gemini.md", ".cursorrules",
    "copilot-instructions.md", "codeowners", ".pre-commit-config.yaml", ".pre-commit-config.yml",
}
GOVERNANCE_DIRS = (".agent", ".cursor/rules", ".github/instructions", ".claude-plugin")
INSTRUCTION_DIRS = (".claude/agents", ".claude/skills", ".claude/commands", ".claude/rules",
                    ".claude/output-styles")
HOME_ROOTS = ("/home", "/users", "/system/volumes/data/home", "/system/volumes/data/users")


class Paths:
    """Canonical forms of one file path, its working directory and $HOME (all lowercased)."""

    def __init__(self, file_path, cwd, home):
        base = cwd or os.getcwd()
        self.raw = file_path
        self.real = _canon(file_path, base, resolve=True)
        self.norm = _canon(file_path, base, resolve=False)
        self.cwd_real = _canon(cwd, "/", resolve=True) if cwd else ""
        self.cwd_norm = _canon(cwd, "/", resolve=False) if cwd else ""
        self.home_real = _canon(home, "/", resolve=True) if home else ""
        self.home_norm = _canon(home, "/", resolve=False) if home else ""
        self.basename = os.path.basename(self.real)


def _canon(path, base, resolve):
    p = os.path.expanduser(path)
    if not os.path.isabs(p):
        p = os.path.join(base, p)
    return (os.path.realpath(p) if resolve else os.path.normpath(p)).lower()


def _under(path, base):
    return bool(base) and path.startswith(base.rstrip("/") + "/")


def _in_dir(path, rel_dir):
    """True if `path` is inside a folder named `rel_dir` (e.g. ".claude/hooks") at any depth."""
    return "/" + rel_dir + "/" in path


def _is_dir_or_inside(path, name):
    return path.endswith("/" + name) or ("/" + name + "/") in path


# --------------------------------------------------------------------------- classification

def guardrail_reason(p):
    """Deny reason if `p.real` is one of the controls that watch the agent (ASI10), else None."""
    real = p.real
    if real.endswith("/.claude/settings.json") or real.endswith("/.claude/settings.local.json"):
        return "agents may not change their own permission or hook settings"
    if _in_dir(real, ".claude/hooks") or _in_dir(real, ".claude/plugins"):
        return "agents may not change the hooks or plugins that enforce their rules"
    if _in_dir(real, ".git/hooks"):
        return "agents may not change git hooks"
    if real.endswith("/.git/config") or _in_dir(real, ".git/info"):
        # core.hooksPath turns off pre-commit checks; core.fsmonitor, aliases or sshCommand
        # run commands the next time a human uses git, outside any sandbox.
        return "agents may not change git configuration"
    return None


def governance_reason(p):
    """Ask reason if `p.real` holds rules or instructions for agents (rule 8), else None."""
    real = p.real
    if p.basename in GOVERNANCE_BASENAMES or any(_in_dir(real, d) for d in GOVERNANCE_DIRS):
        return "governance and guardrail files change only when the human asked"
    if any(_in_dir(real, d) for d in INSTRUCTION_DIRS):
        # Agent, skill, command and rule files carry instructions (and can declare hooks),
        # so planting one is a persistent prompt injection.
        return "agent, skill, command and rule files carry instructions"
    return None


def protected_file_reason(p):
    """Ask reason for files .agent/CONSTRAINTS.md lists as protected, else None."""
    name, real = p.basename, p.real
    if name.startswith(".env"):
        return "environment files are protected"
    if name.endswith((".pem", ".key")):
        return "certificate/key files are protected"
    if (name.startswith("docker-compose") and name.endswith(".yml")) or name.startswith("dockerfile"):
        return "container orchestration files are protected"
    if "/config/prod" in real:
        return "production configuration is protected"
    if _in_dir(real, ".github/workflows"):
        return "CI/CD pipeline files are protected"
    return None


def project_memory_names(cwd):
    """Possible <project> folder names for this project's Claude Code auto memory.

    Per the Claude Code docs, ~/.claude/projects/<project>/memory/ is derived from the git
    repository root (shared by subfolders and worktrees), the working directory outside a
    repo, or CLAUDE_CODE_PROJECT_DIR_NAME. The exact encoding isn't documented ("/" becomes
    "-"), so both likely encodings are returned, for this project only.
    """
    root = cwd
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--git-common-dir"],
                             capture_output=True, text=True, timeout=3)
        if out.returncode == 0 and out.stdout.strip():
            d = os.path.normpath(os.path.join(cwd, out.stdout.strip()))
            root = os.path.dirname(d) if os.path.basename(d) == ".git" else d
    except (OSError, subprocess.SubprocessError):
        pass
    names = set()
    if os.environ.get("CLAUDE_CODE_PROJECT_DIR_NAME"):
        names.add(os.environ["CLAUDE_CODE_PROJECT_DIR_NAME"])
    for r in {root, os.path.realpath(root)}:
        names.add(re.sub(r"[^A-Za-z0-9]", "-", r))
        names.add(r.replace("/", "-"))
    return {n.lower() for n in names if n and "/" not in n and n not in (".", "..")}


def _in_homes(path, p):
    if any(_under(path, root) for root in HOME_ROOTS):
        return True
    return _under(path, p.home_real) or _under(path, p.home_norm)  # your own home, wherever it is


def _own_memory(p, cwd):
    if not p.home_real:
        return False
    return any(p.real.startswith("%s/.claude/projects/%s/memory/" % (p.home_real, name))
               for name in project_memory_names(cwd or os.getcwd()))


def decide(tool_name, file_path, cwd, home):
    """Return (decision, reason) for a file tool call. decision is ALLOW, ASK or DENY."""
    if not file_path:
        return ALLOW, ""
    p = Paths(file_path, cwd, home)

    # Credential folders: denied for every tool, reads included.
    if _is_dir_or_inside(p.real, ".ssh") or _is_dir_or_inside(p.norm, ".ssh"):
        return DENY, "SSH key directories are forbidden"
    if _is_dir_or_inside(p.real, ".aws") or _is_dir_or_inside(p.norm, ".aws"):
        return DENY, "AWS credential directories are forbidden"

    if tool_name == "Read":  # everything below guards modifications only
        return ALLOW, ""

    raw = file_path.replace("\\", "/")
    if raw.startswith("../") or "/../" in raw or raw == "..":
        return DENY, "path traverses outside the repository root"
    if any(p.real == d or _under(p.real, d) for d in ("/etc", "/private/etc")):
        return DENY, "/etc/ is a forbidden directory"

    # Home folders outside the project, including other projects' .claude/ folders. A path is
    # outside if EITHER form is: a repo symlink (docs/notes -> ~/.bashrc) is inside as written
    # but outside once resolved. Resolved is compared with resolved, written with written, so
    # a project under a symlinked folder (macOS /home) still counts as inside.
    outside = not _under(p.real, p.cwd_real) or not _under(p.norm, p.cwd_norm)
    if p.cwd_real and outside and (_in_homes(p.norm, p) or _in_homes(p.real, p)):
        if not _own_memory(p, cwd):  # memory is loaded into later sessions of its project
            return DENY, "file is outside the current working directory, or a link inside it points outside"

    reason = guardrail_reason(p)
    if reason:
        return DENY, reason + ". Ask the human to edit this file"
    reason = governance_reason(p)
    if reason:
        return ASK, reason
    reason = protected_file_reason(p)
    if reason:
        return ASK, reason
    return ALLOW, ""


def is_governance_target(path, cwd, home=None):
    """For shell writes (guard-bash.py): is this a guardrail or governance file?"""
    p = Paths(path, cwd, home if home is not None else os.environ.get("HOME", ""))
    return bool(guardrail_reason(p) or governance_reason(p))
