---
description: Use to create a well-formatted commit from staged changes, following the project's commit message conventions.
invoke-by: both
---

# /commit — Create Commit

**Usage:** `/commit` (analyzes staged changes and proposes commit message)

**Process:**
1. Analyze `git diff --staged`
2. Determine appropriate commit type (see `.agent/WORKFLOW.md`)
3. Propose commit message following conventions
4. Ask for approval before committing

Note: staged changes are also scanned for secrets by `hooks/scripts/block-secret-commit.sh` before the commit is allowed to run.
