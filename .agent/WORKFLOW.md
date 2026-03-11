# WORKFLOW.md — Git & Development Workflow

## Branch Strategy

### Branch Naming Convention

```
<type>/<ticket>-<short-description>

Examples:
feature/PROJ-123-user-authentication
bugfix/PROJ-456-fix-login-redirect
refactor/PROJ-789-extract-auth-module
docs/PROJ-012-update-api-docs
chore/PROJ-345-update-dependencies
```

**Type prefixes:**
| Prefix | Purpose |
|--------|---------|
| `feature/` | New functionality |
| `bugfix/` | Bug fixes |
| `hotfix/` | Urgent production fixes |
| `refactor/` | Code restructuring |
| `docs/` | Documentation only |
| `chore/` | Maintenance tasks |
| `test/` | Test additions/modifications |

### Branch Rules

- **Never commit directly to `main` or `master`**
- Create feature branches from the latest `main`
- Keep branches focused on a single concern
- Delete branches after merging

## Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Example:**
```
feat(auth): implement OAuth2 login flow

- Add OAuth2 provider configuration
- Create login callback handler
- Store tokens securely in session

Closes #123
```

### Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, missing semicolons, etc. |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependencies, tooling |
| `perf` | Performance improvements |
| `ci` | CI/CD changes |
| `revert` | Reverting previous commits |

### Commit Best Practices

1. **Atomic commits:** One logical change per commit
2. **Present tense:** "Add feature" not "Added feature"
3. **Imperative mood:** "Fix bug" not "Fixes bug"
4. **No period** at end of subject line
5. **Subject line:** 50 characters max
6. **Body:** Wrap at 72 characters

## Pull Request Workflow

### Before Creating a PR

1. Ensure all tests pass locally
2. Run linter and fix any issues
3. Update documentation if needed
4. Rebase on latest `main` if diverged significantly

### PR Title Format

Same as commit message format:
```
feat(auth): implement OAuth2 login flow
```

### PR Description Template

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No new warnings
```

### PR Review Process

1. **Self-review:** Check diff before requesting review
2. **CI checks:** Wait for all checks to pass
3. **Address feedback:** Respond to all comments
4. **Squash if needed:** Clean up commit history before merge

## Task Tracking Integration

### Linking Commits to Issues

Include issue references in commit messages:
```
feat(api): add user profile endpoint

Implements the user profile retrieval API.

Refs #123
Closes #124
```

### Issue Lifecycle

```
Open → In Progress → Review → Done
```

**When starting work:**
1. Verify issue exists and is assigned
2. Create appropriately named branch
3. Reference issue in commits

**When completing work:**
1. Include `Closes #<issue>` in final commit
2. Verify issue auto-closes on merge
3. Delete feature branch

## Merge Strategy

### Standard Merge

For most feature work:
```bash
git checkout main
git pull origin main
git merge --no-ff feature/branch
```

### Squash Merge

For small changes or messy history:
```bash
git merge --squash feature/branch
git commit -m "feat(scope): description"
```

### Rebase (with caution)

Only for local cleanup before push:
```bash
git rebase -i main  # Interactive rebase
```

**Never rebase shared branches.**

## Conflict Resolution

1. **Pull latest main** before starting resolution
2. **Understand both changes** before deciding
3. **Test after resolution** to ensure nothing broke
4. **Commit with clear message** explaining resolution

```bash
git checkout main
git pull origin main
git checkout feature/branch
git rebase main
# Resolve conflicts
git add .
git rebase --continue
```

---

*These workflow standards can be customized in `.agent/PROJECT.md` for project-specific needs.*
