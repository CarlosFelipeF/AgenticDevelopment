#!/usr/bin/env python3
"""guard-bash — Claude Code PreToolUse hook for the Bash tool.

Enforces the "Never" rules in .agent/CONSTRAINTS.md that an instruction file alone
cannot: running downloaded code, skipping git hooks, force or main-branch pushes,
reading or sending secrets, dangerous deletes, privilege escalation, and an agent
editing its own governance or guardrail files.

It tokenises commands like a shell does (quotes, pipes, ;, &&, $(...), heredocs),
so it does not trip on words inside commit messages and is harder to dodge with
quoting tricks.

Defence in depth, NOT a sandbox. It cannot see what a script does once written to
disk, or what inline Python/Node code does at run time. Pair it with the permission
deny-list in settings.json, branch protection, CI and a sandboxed environment.

Install : copy with pathpolicy.py to .claude/hooks/ (see examples/README.md)
Test    : python3 -m unittest discover -s tests
Exit 2  : block; the reason on stderr is shown to the agent.
Exit 0  : no objection; Claude Code's normal permission rules then apply.
Needs   : Python 3.8+, standard library only.
"""
import glob
import json
import os
import re
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True  # never write caches into the plugin or .claude/hooks folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pathpolicy  # noqa: E402  (shared with protect-files.py)

MAX_DEPTH = 6

SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish", "ash"}
INTERPRETERS_RE = re.compile(r"^(python[0-9.]*|node|nodejs|deno|bun|perl|ruby|php)$")
FETCHERS = {"curl", "wget", "fetch", "aria2c", "http", "https", "xh", "iwr", "irm"}
WRAPPERS = {"command", "builtin", "exec", "nohup", "time", "nice", "ionice", "stdbuf",
            "timeout", "caffeinate", "unbuffer", "env", "xargs"}
PRIV_ESC = {"sudo", "doas", "pkexec", "su", "runas"}
RAW_NET = {"nc", "ncat", "netcat", "socat", "telnet"}

READERS = {"cat", "tac", "less", "more", "head", "tail", "bat", "batcat", "nl", "od",
           "xxd", "hexdump", "strings", "base64", "base32", "grep", "egrep", "fgrep",
           "rg", "ag", "ack", "sed", "awk", "gawk", "cut", "sort", "uniq", "diff",
           "cmp", "source", ".", "openssl", "gpg", "zip", "tar", "7z", "jq", "yq",
           "vim", "vi", "nvim", "nano", "emacs", "code", "open", "xdg-open",
           "pbcopy", "xclip", "xsel", "dotenv", "curl", "wget", "http", "https"}
COPIERS = {"cp", "mv", "rsync", "scp", "install", "ln"}  # last argument is the destination

SECRET_RE = re.compile(
    r"(^|/)\.env(\.[A-Za-z0-9_.-]+)?$"
    r"|(^|/)(id_rsa|id_dsa|id_ecdsa|id_ed25519)$"
    r"|\.(pem|key|p12|pfx|jks|keystore|kdbx)$"
    r"|(^|/)\.aws/(credentials|config)$"
    r"|(^|/)\.ssh(/|$)"
    r"|(^|/)\.(netrc|git-credentials|pgpass)$"
    r"|(^|/)\.docker/config\.json$"
    r"|(^|/)\.kube/config$"
    r"|(^|/)\.config/gcloud(/|$)"
    r"|^/proc/[^/]+/environ$"
)
SAFE_SECRET_SUFFIXES = (".example", ".sample", ".template", ".dist", ".defaults")

GOVERNANCE_RE = re.compile(
    r"(^|/)(AGENTS\.md|CLAUDE\.md|CLAUDE\.local\.md|GEMINI\.md|\.cursorrules"
    r"|copilot-instructions\.md|CODEOWNERS|\.pre-commit-config\.ya?ml|lefthook\.ya?ml)$"
    r"|(^|/)\.(agent|claude|cursor|gemini|husky)(/|$)"
    r"|(^|/)\.git/hooks(/|$)"
    r"|(^|/)\.github/(workflows|instructions)(/|$)"
)
SECRET_VAR_RE = re.compile(
    r"\$\{?[A-Za-z0-9_]*(TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY|PRIVATE_KEY|CREDENTIAL|ACCESS_KEY)",
    re.IGNORECASE,
)
HOOK_SKIP_ENV_RE = re.compile(
    r"^(SKIP|PRE_COMMIT_ALLOW_NO_CONFIG|LEFTHOOK_EXCLUDE|GIT_CONFIG_PARAMETERS"
    r"|GIT_CONFIG_COUNT|GIT_CONFIG_KEY_\d+|GIT_CONFIG_VALUE_\d+)=|^(HUSKY|LEFTHOOK)=0$"
)
SYSTEM_DIR_RE = re.compile(
    r"^/(bin|boot|dev|etc|home|lib|lib64|opt|root|sbin|srv|sys|usr|var|Users|System|Library|Applications)/?\*?$"
)
BARE_VAR_RE = re.compile(r"^\$\{?[A-Za-z_][A-Za-z0-9_]*\}?/?\*?$")
ASSIGN_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", re.S)
HEREDOC_RE = re.compile(r"(?<!<)<<(?!<)-?\s*([\"']?)([A-Za-z_][A-Za-z0-9_]*)\1")
PROTECTED_BRANCHES = {"main", "master"}


class Blocked(Exception):
    pass


def deny(reason):
    raise Blocked(reason)


# --------------------------------------------------------------------------- parsing

def strip_heredocs(text):
    """Return (shell_text, inline_code_snippets).

    Heredoc bodies fed to a shell are kept as commands. Bodies fed to an interpreter
    are returned for heuristic checks. Bodies fed to anything else (cat, git commit -F -)
    are data and are dropped, so commit messages cannot cause false positives.
    """
    out, code, lines, i = [], [], text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for m in HEREDOC_RE.finditer(line):
            word = m.group(2)
            before = re.split(r"[;&|(`]|\$\(", line[: m.start()])[-1].split()
            prog = os.path.basename(before[0]) if before else ""
            body = []
            while i < len(lines) and lines[i].strip("\t ") != word:
                body.append(lines[i])
                i += 1
            i += 1  # skip the terminator line
            if prog in SHELLS:
                out.extend(body)
            elif INTERPRETERS_RE.match(prog):
                code.append("\n".join(body))
    return "\n".join(out), code


def tokenize(text):
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()<>\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:  # unbalanced quotes: fall back to a rough split
        return text.replace('"', " ").replace("'", " ").split()


def group_substitutions(tokens):
    """Fold unquoted `$ ( ... )` and `< ( ... )` token runs into single tokens."""
    out, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        opener = None
        if tok in ("$", "<", ">") and i + 1 < len(tokens) and tokens[i + 1] == "(":
            opener, start = tok, i + 2
        elif tok in ("<(", ">("):  # the tokeniser glues these together
            opener, start = tok[0], i + 1
        if opener:
            depth, j, inner = 1, start, []
            while j < len(tokens) and depth:
                if tokens[j] == "(":
                    depth += 1
                elif tokens[j] == ")":
                    depth -= 1
                if depth:
                    inner.append(tokens[j])
                j += 1
            out.append(opener + "(" + " ".join(inner) + ")")
            i = j
        else:
            out.append(tok)
            i += 1
    return out


def substitutions(token):
    """Contents of $(...), <(...), >(...) and `...` inside a token."""
    found, i = [], 0
    while i < len(token):
        if token[i] in "$<>" and token[i + 1:i + 2] == "(":
            depth, j = 1, i + 2
            while j < len(token) and depth:
                depth += {"(": 1, ")": -1}.get(token[j], 0)
                j += 1
            found.append(token[i + 2:j - 1])
            i = j
        elif token[i] == "`":
            j = token.find("`", i + 1)
            if j == -1:
                break
            found.append(token[i + 1:j])
            i = j + 1
        else:
            i += 1
    return found


def split_segments(tokens):
    """Yield (words, redirects, piped_in) for each simple command."""
    seps = {";", "&&", "||", "|", "|&", "&", "\n", "(", ")", ";;", "&;"}
    words, redirects, piped, i = [], [], False, 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in seps:
            if words or redirects:
                yield words, redirects, piped
            words, redirects = [], []
            piped = tok in ("|", "|&")
        elif re.fullmatch(r"[<>&]*[<>][<>&|]*", tok):
            target = tokens[i + 1] if i + 1 < len(tokens) else ""
            if words and words[-1].isdigit():  # the "2" in 2>file
                words.pop()
            redirects.append((tok, target))
            i += 1
        else:
            words.append(tok)
        i += 1
    if words or redirects:
        yield words, redirects, piped


def expand_vars(word, env):
    def repl(m):
        name = m.group(1) or m.group(2)
        return env.get(name, m.group(0))
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)", repl, word)


def expand_paths(word, cwd):
    """Candidate paths a word could refer to: itself, brace and glob expansions."""
    candidates = [word]
    m = re.search(r"\{([^{}]*,[^{}]*)\}", word)
    if m:
        candidates += [word[: m.start()] + part + word[m.end():] for part in m.group(1).split(",")]
    for cand in list(candidates):
        if any(ch in cand for ch in "*?[") and cwd:
            try:
                base = os.path.expanduser(cand)
                pattern = base if os.path.isabs(base) else os.path.join(cwd, base)
                # Like bash, glob() only matches dotfiles when the pattern starts with a dot.
                for hit in glob.glob(pattern, recursive=False)[:200]:
                    candidates.append(os.path.relpath(hit, cwd) if not os.path.isabs(base) else hit)
            except (OSError, ValueError, re.error):
                pass
    return candidates


def is_secret(word, cwd=""):
    for cand in expand_paths(word, cwd):
        cand = re.sub(r"^[A-Za-z0-9_.-]*=?@", "", cand).lstrip("<")  # curl's -d @file, name=@file
        if cand.endswith(SAFE_SECRET_SUFFIXES):
            continue
        if SECRET_RE.search(cand):
            return True
    return False


def is_governance(word, cwd=""):
    """Guardrail or governance file? The regex catches the common spellings; pathpolicy adds
    canonical matching (case, ".", "//", symlinks) and .git/config, shared with protect-files."""
    for cand in expand_paths(word, cwd):
        if GOVERNANCE_RE.search(cand):
            return True
        if cand and not cand.startswith(("$", "~")) and pathpolicy.is_governance_target(cand, cwd or os.getcwd()):
            return True
    return False


def is_flag(word):
    return word.startswith("-") and word != "-"


def short_cluster(word):
    return word[1:] if word.startswith("-") and not word.startswith("--") and len(word) > 1 else ""


def current_branch(cwd):
    if not cwd:
        return ""
    try:
        res = subprocess.run(["git", "-C", cwd, "symbolic-ref", "--short", "-q", "HEAD"],
                             capture_output=True, text=True, timeout=3)
        return res.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


# --------------------------------------------------------------------------- secret scan

def load_secret_pattern():
    """Read SECRET_PATTERN from secret-patterns.sh (the single source shared with the
    bash hooks) and convert POSIX classes to Python syntax."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secret-patterns.sh")
    try:
        with open(path) as fh:
            for line in fh:
                if line.startswith('SECRET_PATTERN="'):
                    raw = line.strip()[len('SECRET_PATTERN="'):-1].replace('\\"', '"')
                    return re.compile(raw.replace("[:space:]", r"\s"))
    except (OSError, re.error):
        pass
    return None


SECRET_IN_COMMIT = ("the changes this commit would record appear to contain a secret "
                    "(API key, private key, password or connection string). Use an environment "
                    "variable or secret manager, then retry")
MAX_UNTRACKED_FILES, MAX_FILE_BYTES = 2000, 2 * 1024 * 1024


def _git(repo, args):
    try:
        res = subprocess.run(["git", "-C", repo] + args, capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        deny("cannot scan the changes this commit would record")
    if res.returncode != 0:
        deny("cannot scan the changes this commit would record (git %s failed in %s)" % (args[0], repo))
    return res.stdout


def scan_commit_for_secrets(repo, worktree, pending_adds=()):
    """Block a commit whose added lines contain a secret.

    Reads the whole diff (no early-exit pipe), scans only added lines (so removing a
    leaked secret is allowed), and fails closed if the changes cannot be scanned.

    `pending_adds` are (pathspecs, force, tracked_only) from `git add` earlier in the SAME
    command. The hook runs before the command, so those files aren't staged yet: their tracked
    changes and any untracked files they would add are scanned now, read straight from disk.
    `git add -u` only updates tracked files, so its untracked files are not scanned.
    """
    pattern = load_secret_pattern()
    if pattern is None:
        deny("cannot load secret patterns (hooks/scripts/secret-patterns.sh) to scan this commit")
    diffs = [["diff", "--cached"]] + ([["diff"]] if worktree else [])
    for specs, _force, _tracked_only in pending_adds:
        diffs.append(["diff", "--"] + specs)
    for extra in diffs:
        cmd = extra[:1] + ["--no-color", "--no-ext-diff", "-U0"] + extra[1:]
        for line in _git(repo, cmd).decode("utf-8", "replace").splitlines():
            if line.startswith("+") and not line.startswith("+++") and pattern.search(line):
                deny(SECRET_IN_COMMIT)
    for specs, force, tracked_only in pending_adds:
        if tracked_only:
            continue
        listing = ["ls-files", "-z", "--others"] + ([] if force else ["--exclude-standard"]) + ["--"] + specs
        names = [n for n in _git(repo, listing).decode("utf-8", "replace").split("\0") if n]
        if len(names) > MAX_UNTRACKED_FILES:
            deny("too many untracked files to scan before this commit; stage them in smaller steps")
        for name in names:
            path = os.path.join(repo, name)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue  # large files are almost never source; gitleaks in CI still scans them
                with open(path, "rb") as fh:
                    text = fh.read().decode("utf-8", "replace")
            except OSError:
                continue
            if pattern.search(text):
                deny(SECRET_IN_COMMIT)


# --------------------------------------------------------------------------- checks

def check_inline_code(code):
    """Heuristics for python -c / node -e / interpreter heredocs."""
    for path in re.findall(r"[~\w./$-]+", code):
        if is_secret(path):
            deny("reading a secret file from inline code")
    writes = re.search(r"open\([^)]*['\"][wa]|write|unlink|remove|rename|rmtree|replace\(", code)
    if writes and any(GOVERNANCE_RE.search(p) for p in re.findall(r"[\w./-]+", code)):
        deny("modifying governance or guardrail files from inline code")


def check_git(args, ctx):
    i, sub, repo = 0, "", ctx["cwd"]
    while i < len(args):
        a = args[i]
        if a in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"):
            if a == "-c" and i + 1 < len(args) and args[i + 1].lower().startswith("core.hookspath"):
                deny("disabling git hooks (core.hooksPath)")
            if a == "-C" and i + 1 < len(args):  # -C may repeat; each is relative to the last
                repo = os.path.join(repo, os.path.expanduser(args[i + 1]))
            i += 2
            continue
        if a.lower().startswith(("--config-env", "-ccore.hookspath")):
            deny("disabling git hooks (core.hooksPath)")
        if is_flag(a):
            i += 1
            continue
        sub = a
        break
    rest = args[i + 1:]

    if "--no-verify" in rest:
        deny("skipping git hooks (--no-verify)")
    if sub == "config" and any("hookspath" in r.lower() for r in rest):
        deny("changing core.hooksPath")
    if sub in ("filter-branch", "filter-repo"):
        deny("rewriting git history")

    if sub in ("commit", "merge"):
        # Options that take the NEXT word as their value (-s/--signoff and -S<key> do not).
        value_opts = {"-m", "-F", "-C", "-c", "-t", "--author", "--date", "--message", "--file",
                      "--template", "--fixup", "--squash", "--trailer", "--cleanup",
                      "--reuse-message", "--reedit-message", "--pathspec-from-file"}
        worktree, j = False, 0
        while j < len(rest):
            r = rest[j]
            if r in value_opts:
                j += 2
                continue
            if r == "--":
                worktree = worktree or j + 1 < len(rest)
                break
            cluster = short_cluster(r)
            if cluster:
                head = re.split(r"[mFCct]", cluster, maxsplit=1)[0]  # letters before a value-taking flag
                if "n" in head:
                    deny("skipping git hooks (-n)")
                if re.search(r"[aio]", head):  # -a/--all, -i/--include, -o/--only
                    worktree = True
            elif r in ("--all", "--include", "--only") or r.startswith("--pathspec-from-file="):
                worktree = True
            elif not is_flag(r):
                worktree = True  # a pathspec: commits working-tree content
            j += 1
        if sub == "commit":
            pending = [(specs, force, tracked) for r, specs, force, tracked in ctx["pending_adds"] if r == repo]
            scan_commit_for_secrets(repo, worktree, pending)

    if sub == "add":
        # Remember what this command is about to stage, for a commit later in the same command.
        value_opts = {"--chmod", "--pathspec-from-file"}
        specs, force, all_files, update_only, j = [], False, False, False, 0
        while j < len(rest):
            r = rest[j]
            if r in value_opts:
                j += 2
                continue
            if r in ("-f", "--force") or "f" in short_cluster(r):
                force = True
            cluster = set(short_cluster(r))
            if r in ("-A", "--all", "--no-ignore-removal") or "A" in cluster:
                all_files = True
            if r in ("-u", "--update") or "u" in cluster:
                update_only = True
            if r == "--":
                specs.extend(rest[j + 1:])
                break
            if not is_flag(r):
                specs.append(r)
            j += 1
        if all_files or (update_only and not specs) or not specs:
            specs = ["."]
        # -u stages tracked files only (unless -A is also given, which includes everything).
        ctx["pending_adds"].append((repo, specs, force, update_only and not all_files))

    if sub == "push":
        value_opts = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
        positional, j = [], 0
        while j < len(rest):
            r = rest[j]
            if r in value_opts:
                j += 2
                continue
            if r.startswith("--force") or r in ("--mirror", "--all", "--prune"):
                deny("force-pushing or bulk-pushing refs (%s)" % r)
            if r == "--delete":
                deny("deleting a remote branch")
            cluster = short_cluster(r)
            if cluster and "f" in cluster:
                deny("force-pushing (-f)")
            if cluster and "d" in cluster:
                deny("deleting a remote branch (-d)")
            if not is_flag(r):
                positional.append(r)
            j += 1
        for ref in positional[1:]:
            if ref.startswith("+"):
                deny("force-pushing (+refspec)")
            if ref.startswith(":"):
                deny("deleting a remote branch (:refspec)")
            dest = ref.split(":")[-1]
            dest = dest[len("refs/heads/"):] if dest.startswith("refs/heads/") else dest
            if dest in PROTECTED_BRANCHES:
                deny("pushing directly to %s" % dest)
        if len(positional) <= 1 and ctx["branch"] in PROTECTED_BRANCHES:
            deny("pushing while on %s" % ctx["branch"])

    if sub == "reset" and "--hard" in rest:
        deny("discarding work with git reset --hard")
    if sub == "clean" and any("f" in short_cluster(r) or r == "--force" for r in rest):
        deny("deleting untracked files with git clean")
    if sub == "branch" and any(r in ("--delete", "-D") or "d" in short_cluster(r).lower() for r in rest):
        deny("deleting a branch")


def check_rm(args, ctx):
    recursive = any(r in ("-r", "-R", "--recursive") or "r" in short_cluster(r).lower() for r in args)
    targets, after_ddash = [], False
    for a in args:
        if a == "--":
            after_ddash = True
        elif after_ddash or not is_flag(a):
            targets.append(a)
    always = {"/", "/*", "~", "~/", "~/*", "*", ".", "./", "./*", "..", "../", "../*",
              "$HOME", "${HOME}", "$HOME/", "${HOME}/", "$HOME/*", "${HOME}/*"}
    for t in targets:
        if t in always or SYSTEM_DIR_RE.match(t) or re.match(r"^~[A-Za-z0-9_-]+/?$", t):
            deny("deleting root, home, parent, system or whole-project paths (%s)" % t)
        if recursive and (BARE_VAR_RE.match(t) or t.rstrip("/") in (".git", "./.git")):
            deny("recursive delete of an unchecked variable or .git (%s)" % t)


def check_segment(words, redirects, piped, ctx, depth):
    env = ctx["env"]
    words = [expand_vars(w, env) for w in words]
    redirects = [(op, expand_vars(t, env)) for op, t in redirects]

    for w in words:
        for inner in substitutions(w):
            check_command(inner, ctx, depth + 1)

    # Leading NAME=value assignments.
    k = 0
    while k < len(words) and ASSIGN_RE.match(words[k]):
        if HOOK_SKIP_ENV_RE.match(words[k]):
            deny("disabling git hooks via %s" % words[k].split("=")[0])
        k += 1
    if k == len(words):  # assignments only: remember them for later segments
        for w in words:
            name, value = ASSIGN_RE.match(w).groups()
            env[name] = value
    # Wrappers such as env, xargs, timeout, nohup.
    while k < len(words):
        base = os.path.basename(words[k])
        if base in PRIV_ESC:
            deny("privilege escalation (%s)" % base)
        if base not in WRAPPERS:
            break
        if base == "env" and all(ASSIGN_RE.match(w) or is_flag(w) for w in words[k + 1:]):
            deny("dumping environment variables")
        k += 1
        while k < len(words) and (is_flag(words[k]) or ASSIGN_RE.match(words[k])
                                  or (base == "timeout" and re.match(r"^\d", words[k]))):
            if HOOK_SKIP_ENV_RE.match(words[k]):
                deny("disabling git hooks via %s" % words[k].split("=")[0])
            k += 1

    cwd = ctx["cwd"]
    for op, target in redirects:
        if op in ("<", "<>") and is_secret(target, cwd):
            deny("reading a secret file (%s)" % target)
        if ">" in op and target and not target.startswith("&") and is_governance(target, cwd):
            deny("modifying governance or guardrail files (%s)" % target)

    if k >= len(words):
        return
    prog, args = os.path.basename(words[k]), words[k + 1:]

    if prog == "cd" and args and not is_flag(args[-1]):
        ctx["cwd"] = os.path.normpath(os.path.join(ctx["cwd"], os.path.expanduser(args[-1])))

    if prog in ("export", "declare", "typeset", "readonly", "local"):
        for a in args:
            m = ASSIGN_RE.match(a)
            if m:
                if HOOK_SKIP_ENV_RE.match(a):
                    deny("disabling git hooks via %s" % m.group(1))
                env[m.group(1)] = m.group(2)

    # Running downloaded or piped code (ASI05).
    if piped and prog in SHELLS and not any(a in ("-c",) for a in args):
        deny("piping content into a shell")
    if piped and INTERPRETERS_RE.match(prog):
        code_flags = {"-c", "-m", "-e", "-E", "--eval", "-p", "--print", "-r"}
        if not any(a in code_flags for a in args) and all(a == "-" or is_flag(a) for a in args):
            deny("piping content into an interpreter")
    if prog in SHELLS | {"eval", "source", "."} or INTERPRETERS_RE.match(prog):
        for a in args:
            if any(re.search(r"(^|[\s;&|(])(%s)(\s|$)" % "|".join(FETCHERS), s) for s in substitutions(a)):
                deny("executing downloaded content")
    if prog in SHELLS:
        for idx, a in enumerate(args):
            if a == "-c" and idx + 1 < len(args):
                check_command(args[idx + 1], ctx, depth + 1)
    if prog == "eval":
        check_command(" ".join(args), ctx, depth + 1)
    if INTERPRETERS_RE.match(prog):
        for idx, a in enumerate(args):
            if a in ("-c", "-e", "-E", "--eval", "-p", "-r") and idx + 1 < len(args):
                check_inline_code(args[idx + 1])

    # Environment dumps and secret variables (ASI03).
    if prog in ("printenv",) and (not args or any(SECRET_VAR_RE.search("$" + a) for a in args)):
        deny("printing environment variables or secrets")
    if prog in ("export", "declare", "set", "typeset") and (not args or args in (["-p"], ["-x"], ["-px"])):
        deny("dumping environment variables")
    if prog in {"echo", "printf", "tee", "logger"} | FETCHERS | RAW_NET or INTERPRETERS_RE.match(prog):
        if any(SECRET_VAR_RE.search(w) for w in args):
            deny("printing or sending a secret environment variable")

    # Secret files.
    if prog in READERS or INTERPRETERS_RE.match(prog):
        for a in args:
            if not is_flag(a) and is_secret(a, cwd):
                deny("reading a secret file (%s)" % a)
            if a.startswith("--") and "=" in a and is_secret(a.split("=", 1)[1], cwd):
                deny("reading a secret file (%s)" % a)
    if prog in COPIERS:
        files = [a for a in args if not is_flag(a)]
        for a in files[:-1]:
            if is_secret(a, cwd):
                deny("copying a secret file (%s)" % a)

    # Exfiltration channels.
    if prog in RAW_NET:
        deny("raw network tools (%s)" % prog)
    if prog == "curl":
        for idx, a in enumerate(args):
            nxt = args[idx + 1] if idx + 1 < len(args) else ""
            if a in ("-T", "--upload-file") or a.startswith("--upload-file="):
                deny("uploading a local file")
            if a in ("-d", "--data", "--data-binary", "--data-raw", "--data-urlencode", "-F", "--form", "--json") \
                    and re.match(r"^([A-Za-z0-9_.-]+=)?[@<]", nxt):
                deny("uploading a local file")
            if re.match(r"^--(data[a-z-]*|form|json)=([A-Za-z0-9_.-]+=)?[@<]", a):
                deny("uploading a local file")
    if prog == "wget" and any(a.startswith(("--post-file", "--body-file")) for a in args):
        deny("uploading a local file")
    if prog in ("scp", "rsync") and any(re.match(r"^[^/\s]*[A-Za-z0-9]:", a) for a in args if not is_flag(a)):
        deny("copying files to a remote host")

    # Git safety.
    if prog == "git":
        check_git(args, ctx)

    # Destructive commands.
    if prog in ("rm", "rmdir", "unlink", "shred"):
        check_rm(args, ctx)
    if prog == "find" and any(a in ("-delete",) for a in args):
        starts = [a for a in args if not is_flag(a)][:1]
        if starts and (starts[0] in ("/", "~", "~/", "..", "$HOME") or SYSTEM_DIR_RE.match(starts[0])):
            deny("mass delete with find")
    if prog.startswith("mkfs") or (prog == "dd" and any(a.startswith("of=/dev/") for a in args)):
        deny("overwriting a disk or device")
    if prog == "chmod" and any(re.match(r"^0?[0-7]?777$|^a\+rwx$|^o\+w", a) for a in args):
        deny("making files world-writable")

    # Agents must not change their own rules or guardrails (ASI10).
    targets = [a for a in args if not is_flag(a)]
    writes_all = {"tee", "truncate", "touch", "rm", "rmdir", "unlink", "shred", "chmod", "chown", "mv"}
    in_place = (prog == "sed" and any(a.startswith("--in-place") or "i" in short_cluster(a) for a in args)) or \
               (prog == "perl" and any("i" in short_cluster(a) for a in args))
    if prog in writes_all or in_place:
        hits = [t for t in targets if is_governance(t, cwd)]
    elif prog in COPIERS and targets:
        hits = [targets[-1]] if is_governance(targets[-1], cwd) else []
    elif prog == "dd":
        hits = [a for a in args if a.startswith("of=") and is_governance(a[3:], cwd)]
    else:
        hits = []
    if hits:
        deny("modifying governance or guardrail files (%s)" % hits[0])


def check_command(text, ctx, depth=0):
    if depth > MAX_DEPTH:
        deny("command nesting too deep to analyse")
    text = text.replace("\\\n", " ")
    text, code_snippets = strip_heredocs(text)
    for code in code_snippets:
        check_inline_code(code)
    tokens = group_substitutions(tokenize(text))
    for words, redirects, piped in split_segments(tokens):
        check_segment(words, redirects, piped, ctx, depth)


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input") or {}
        command = tool_input.get("command") or ""
        cwd = data.get("cwd") or os.getcwd()
        if not isinstance(command, str):
            raise ValueError("tool_input.command is not a string")
    except Exception as exc:  # malformed input: fail closed
        print("guard-bash: cannot read hook input (%s); blocking to fail secure." % exc, file=sys.stderr)
        return 2
    if not command.strip():
        return 0
    ctx = {"cwd": cwd, "env": {}, "branch": current_branch(cwd), "pending_adds": []}
    try:
        check_command(command, ctx)
    except Blocked as blocked:
        print("Blocked by guard-bash: %s.\n"
              "See .agent/CONSTRAINTS.md. If this is truly needed, explain why and ask the "
              "human to run it or approve it." % blocked, file=sys.stderr)
        return 2
    except Exception as exc:  # a bug in this hook must not open the gate
        print("guard-bash: internal error (%s); blocking to fail secure." % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
