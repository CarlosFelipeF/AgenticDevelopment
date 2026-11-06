#!/usr/bin/env python3
"""protect-files — Claude Code PreToolUse hook for Read, Write, Edit and NotebookEdit.

Enforces .agent/CONSTRAINTS.md for the file tools:
- deny: credential folders (reads too), /etc, writes outside the project into home folders
  (except this project's own Claude Code memory), and the guardrails that watch the agent
  (.claude settings, hooks and plugins, .git/hooks, .git/config) — ASI10 Rogue Agents
- ask:  governance and instruction files (AGENTS.md, .agent/, skills, ...), .env, keys,
  container, production and CI files

The rules live in pathpolicy.py, shared with guard-bash.py and tested in tests/.
Any error denies the call (fail closed). Python 3.8+, standard library only.
"""
import json
import os
import sys

sys.dont_write_bytecode = True  # never write caches into the plugin or .claude/hooks folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def respond(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))


def main():
    try:
        import pathpolicy

        data = json.load(sys.stdin)
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if not isinstance(file_path, str):
            raise ValueError("file_path is not a string")
        decision, reason = pathpolicy.decide(data.get("tool_name") or "", file_path,
                                             data.get("cwd") or "", os.environ.get("HOME", ""))
    except Exception as exc:  # a bug or bad input must not open the gate
        respond("deny", "Blocked: protect-files could not check this path safely (%s)." % exc)
        return 0
    if decision == pathpolicy.DENY:
        respond("deny", "Blocked by .agent/CONSTRAINTS.md: %s." % reason)
    elif decision == pathpolicy.ASK:
        respond("ask", "Requires approval per .agent/CONSTRAINTS.md and AGENTS.md rule 8: %s." % reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
