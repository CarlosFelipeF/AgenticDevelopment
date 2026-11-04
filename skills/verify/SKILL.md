---
description: Use before saying any task is done, to run the project's checks and report results with evidence. Required by the Definition of Done in AGENTS.md.
---

# /verify — Prove the Change Works

**Usage:** `/verify`

**Process:**
1. Run the project's checks from `.agent/PROJECT.md` (tests, lint, type check, build)
2. Run the secret scanner on the diff
3. Check the diff for scope creep, debug code, and removed, skipped or weakened tests
4. Report with evidence — never report a pass you did not see

**Output format:**
```markdown
## Verification: <change>

| Check | Command | Result |
|-------|---------|--------|
| Tests | `npm test` | ✅ 142 passed |
| Lint | `npm run lint` | ✅ clean |
| Types | `npm run typecheck` | ❌ 2 errors (see below) |
| Secrets | `gitleaks git --staged` | ✅ none found |

### Not verified
- Anything you could not run, and why

### Verdict
✅ Done | ⚠️ Done with caveats | ❌ Not done
```
