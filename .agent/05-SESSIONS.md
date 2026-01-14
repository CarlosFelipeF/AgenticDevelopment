# 05-SESSIONS.md — Session Management

## Session Start Protocol

### Initial Context Loading

When starting a new session:

1. **Load governance files** (in order specified in `AGENTS.md`)
2. **Scan repository structure** to understand the codebase
3. **Check for active work:**
   - Uncommitted changes (`git status`)
   - Open branches (`git branch`)
   - TODO/FIXME markers in recent files
4. **Identify the task** from conversation context

### State Assessment

Before beginning work, assess:

```bash
# Check git state
git status
git branch --show-current
git log --oneline -5

# Check for pending work
grep -r "TODO\|FIXME\|HACK" src/ --include="*.ts" --include="*.py" | head -20

# Check test state
npm test -- --passWithNoTests 2>/dev/null || echo "Tests need investigation"
```

### Starting Checklist

- [ ] Understand the task objective
- [ ] Identify affected files/components
- [ ] Review related existing code
- [ ] Check for relevant tests
- [ ] Confirm any blocking questions

## During Session

### Progress Tracking

**Maintain awareness of:**
- Files modified since session start
- Tests passing/failing
- Open questions or blockers
- Time spent on current task

**Periodic self-checks:**
- Am I still working toward the original objective?
- Are there simpler approaches I'm missing?
- Should I ask for clarification?
- Is this change growing too large? Should I split it?

### Context Preservation

For complex tasks, leave breadcrumbs:

```javascript
// TODO(session): Implementing user auth - next: add token refresh
// See related: src/auth/token-manager.ts
```

## Session End Protocol

### Before Ending

1. **Commit all meaningful work** (even partial progress)
2. **Run tests** to verify nothing is broken
3. **Document stopping point** in commit message or TODO

### Handoff Commit Message

When stopping mid-task:

```
wip(auth): implement OAuth flow - token validation pending

Progress:
- Added OAuth provider config
- Created login redirect handler
- Token validation logic started

Next steps:
- Complete validateToken() function
- Add refresh token rotation
- Write integration tests

Refs #123
```

### State Documentation

Leave context for the next session (or another agent):

```markdown
## Session Handoff — 2026-01-15

### Completed
- User login endpoint functional
- Session storage implemented

### In Progress
- Token refresh mechanism (see `src/auth/refresh.ts:45`)

### Blockers
- Need clarification on refresh token lifetime policy

### Next Steps
1. Complete `rotateRefreshToken()` function
2. Add rate limiting to auth endpoints
3. Write E2E tests for login flow

### Files Modified
- src/auth/login.ts
- src/auth/refresh.ts (incomplete)
- tests/auth/login.test.ts
```

## Multi-Agent Handoffs

### Passing Work to Another Agent

When handing off to another agent instance:

1. **Commit current state** with detailed WIP message
2. **Document context** in a structured format
3. **Specify clear next actions**
4. **List any discovered blockers or questions**

### Receiving Work from Another Agent

When receiving a handoff:

1. **Read handoff documentation** thoroughly
2. **Review recent commits** from previous agent
3. **Run tests** to verify current state
4. **Check for uncommitted changes** in working directory
5. **Confirm understanding** before proceeding

### Handoff Document Structure

```markdown
# Agent Handoff: [Task Name]

## Context
Brief description of the overall task and its purpose.

## Current State
- What has been completed
- What is in progress
- Current branch: `feature/xyz`

## Key Decisions Made
- Decision 1: Why this approach was chosen
- Decision 2: Trade-offs considered

## Open Questions
- Question 1: Waiting for human input
- Question 2: Technical uncertainty

## Next Actions
1. Specific action 1
2. Specific action 2
3. Specific action 3

## File Map
- `src/module/file.ts` - Main implementation
- `src/module/types.ts` - Type definitions
- `tests/module/file.test.ts` - Tests (need completion)

## Risks/Concerns
- Potential issue 1
- Potential issue 2
```

## Context Recovery

### When Resuming Interrupted Work

1. **Find the last handoff document** or WIP commit
2. **Check git log** for recent activity
3. **Run `git status`** for uncommitted changes
4. **Run tests** to establish baseline
5. **Review changed files** to understand current state

### Lost Context Recovery

If context is unclear:

```bash
# What was recently changed?
git log --oneline -10
git diff HEAD~5 --stat

# What branches exist?
git branch -a

# What's the current state?
git status
npm test 2>&1 | tail -20
```

---

*Session protocols ensure continuity across sessions and agents.*
