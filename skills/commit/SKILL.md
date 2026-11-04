---
description: Use to create a well-formatted commit from staged changes, following the project's commit message conventions.
---

# /commit — Create Commit

**Usage:** `/commit` (analyzes staged changes and proposes commit message)

**Process:**
1. Stage specific paths only (`git add <path>`) — never `git add .` or `git add -A`
2. Analyse `git diff --staged` and run the secret scanner on it
3. Determine the commit type and write the message following `.agent/WORKFLOW.md`,
   including the AI attribution trailer
4. Show the message and file list, then commit on the working branch
   (with `autonomy: supervised`, wait for approval first; pushing always needs approval)

Note: staged changes are also scanned for secrets by `hooks/scripts/block-secret-commit.sh` before the commit is allowed to run.
