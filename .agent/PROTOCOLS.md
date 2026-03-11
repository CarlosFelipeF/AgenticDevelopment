# PROTOCOLS.md — Slash Commands

> Quick commands for common development workflows. 
> These are conventions, not executable scripts.

## Planning Commands

### `/plan`

Create a structured implementation plan before coding.

**Usage:** `/plan <task description>`

**Output structure:**
```markdown
## Implementation Plan: <Task>

### Objective
What we're trying to achieve.

### Approach
High-level strategy.

### Steps
1. [ ] Step 1 — Description
2. [ ] Step 2 — Description
3. [ ] Step 3 — Description

### Files to Modify
- `path/to/file.ts` — What changes

### Dependencies
- New packages needed: none | list

### Risks
- Potential issues to watch for

### Questions
- Any clarifications needed before starting?
```

### `/design`

Create a technical design document for complex features.

**Usage:** `/design <feature name>`

**Output structure:**
```markdown
## Technical Design: <Feature>

### Overview
What and why.

### Architecture
- Components involved
- Data flow diagram (if applicable)

### API Changes
- New endpoints or modifications

### Data Model
- Schema changes

### Security Considerations
- Auth, permissions, data protection

### Testing Strategy
- Unit tests, integration tests, E2E

### Rollout Plan
- Feature flags, gradual rollout
```

## Code Review Commands

### `/review`

Perform a structured code review on recent changes.

**Usage:** `/review` (reviews staged changes or specified files)

**Review checklist:**
- [ ] **Correctness:** Does the code do what it's supposed to?
- [ ] **Tests:** Are there adequate tests?
- [ ] **Security:** Any vulnerabilities introduced?
- [ ] **Performance:** Any obvious inefficiencies?
- [ ] **Readability:** Is the code clear and well-documented?
- [ ] **Conventions:** Does it follow project standards?

**Output format:**
```markdown
## Code Review: <scope>

### Summary
Overall assessment.

### Issues Found
1. **[severity]** file:line — Description

### Suggestions
- Optional improvements

### Approval Status
✅ Ready to merge | ⚠️ Changes requested | 🚫 Needs rework
```

### `/security-review`

Focused security review of changes.

**Usage:** `/security-review`

**Check for:**
- Hardcoded secrets or credentials
- SQL injection vulnerabilities
- XSS vulnerabilities
- Path traversal issues
- Insecure dependencies
- Missing input validation
- Improper error handling (information disclosure)

## Git Commands

### `/commit`

Create a well-formatted commit with staged changes.

**Usage:** `/commit` (analyzes staged changes and proposes commit message)

**Process:**
1. Analyze `git diff --staged`
2. Determine appropriate commit type
3. Propose commit message following conventions
4. Ask for approval before committing

### `/branch`

Create a properly named feature branch.

**Usage:** `/branch <ticket> <description>`

**Example:**
```
/branch PROJ-123 user authentication

Creates: feature/PROJ-123-user-authentication
```

### `/pr`

Prepare a pull request description.

**Usage:** `/pr`

**Output:**
```markdown
## Summary
Brief description of changes.

## Changes
- Change 1
- Change 2

## Testing
How to verify the changes.

## Screenshots
(if applicable)

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Self-reviewed
```

## Testing Commands

### `/test`

Run appropriate tests for current changes.

**Usage:** `/test [scope]`

**Behavior:**
- No scope: Run tests related to modified files
- With scope: Run specified test suite

### `/coverage`

Check test coverage for modified code.

**Usage:** `/coverage`

**Output:**
- Coverage percentage for modified files
- Uncovered lines/branches
- Suggestions for additional tests

## Documentation Commands

### `/doc`

Generate or update documentation for code.

**Usage:** `/doc <file or function>`

**For functions:** Generate/update JSDoc or docstring
**For files:** Generate/update module documentation
**For APIs:** Generate/update API documentation

### `/changelog`

Prepare changelog entry for current changes.

**Usage:** `/changelog`

**Output format:**
```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description
```

## Debugging Commands

### `/debug`

Analyze an error or unexpected behavior.

**Usage:** `/debug <error message or description>`

**Process:**
1. Identify error source
2. Trace execution path
3. Identify root cause
4. Propose fix

### `/trace`

Trace data flow through the system.

**Usage:** `/trace <starting point>`

**Output:**
Step-by-step data flow with relevant code references.

## Refactoring Commands

### `/refactor`

Plan a refactoring operation.

**Usage:** `/refactor <target> <goal>`

**Example:** `/refactor UserService extract authentication logic`

**Output:**
- Current structure analysis
- Proposed changes
- Step-by-step refactoring plan
- Test verification strategy

### `/cleanup`

Identify and fix code smells in a file or module.

**Usage:** `/cleanup <target>`

**Checks:**
- Unused imports/variables
- Dead code
- Duplicate code
- Overly complex functions
- Inconsistent formatting

## Status Commands

### `/status`

Get current session status.

**Usage:** `/status`

**Output:**
- Current branch
- Modified files
- Test status
- Task progress

### `/recap`

Summarize work done in current session.

**Usage:** `/recap`

**Output:**
- Commits made
- Files modified
- Tests added/updated
- Remaining work

---

*Commands can be extended in `.agent/PROJECT.md` for project-specific workflows.*
