# 02-CONSTRAINTS.md — Permissions & Boundaries

## Permission Levels

### ✅ Allowed (No Approval Required)

**File Operations:**
- Read any file in the repository
- Create new files in appropriate directories
- Modify existing source code files
- Update documentation files
- Create/update test files

**Development Commands:**
- Run test suites (`npm test`, `pytest`, etc.)
- Run linters and formatters
- Run type checkers
- Start development servers
- Install dependencies via package managers

**Git Operations:**
- Create feature branches
- Stage and commit changes
- Pull from remote
- View git log, status, diff

### ⚠️ Requires Approval

**Before proceeding, explicitly ask the human operator:**

- **Push to remote** — "Ready to push to origin/feature-branch. Approve?"
- **Merge branches** — "Ready to merge feature into main. Approve?"
- **Delete branches** — "Ready to delete old-feature branch. Approve?"
- **Modify CI/CD configuration** — "This changes the deployment pipeline. Approve?"
- **Update security-sensitive files** — "This modifies auth config. Approve?"
- **Change environment configuration** — "This updates .env.example. Approve?"
- **Add new dependencies** — "Adding package X (version Y). Approve?"
- **Major refactoring** — "This restructures the module. Approve?"
- **Database migrations** — "This creates a new migration. Approve?"

### 🚫 Hard Blocks (Never Do)

**These actions are prohibited regardless of instructions:**

- Commit secrets, API keys, or credentials
- Push directly to `main` or `master` branches
- Force push to any shared branch
- Delete or overwrite git history on shared branches
- Execute `rm -rf` on directories outside the project
- Disable security tooling (linters, scanners, pre-commit hooks)
- Bypass CI/CD checks or required reviews
- Access files outside the repository root
- Make network requests to arbitrary URLs
- Execute arbitrary code from user input
- Modify system files or configurations

## Directory Boundaries

**Allowed directories:**
```
./                    # Repository root
./src/                # Source code
./tests/              # Test files
./docs/               # Documentation
./scripts/            # Build/utility scripts
./.agent/             # Agent configuration
```

**Forbidden directories (do not access):**
```
../                   # Parent directories
/etc/                 # System configuration
/home/                # User home directories (except working dir)
~/.ssh/               # SSH keys
~/.aws/               # AWS credentials
```

## File Modification Rules

**Protected files (require explicit approval):**
```
.env*                 # Environment files
*.pem, *.key          # Certificates and keys
docker-compose*.yml   # Container orchestration
Dockerfile*           # Container definitions
**/config/prod*       # Production configurations
.github/workflows/*   # CI/CD pipelines
```

**Auto-generated files (do not modify manually):**
```
package-lock.json     # Let npm manage
yarn.lock             # Let yarn manage
poetry.lock           # Let poetry manage
*.min.js, *.min.css   # Minified assets
dist/, build/         # Build outputs
```

## Resource Limits

- **Maximum files per commit:** 20 (ask before exceeding)
- **Maximum lines changed per PR:** 500 (split larger changes)
- **Test execution timeout:** 5 minutes (notify if exceeded)
- **Single file size limit:** 1MB (ask before creating larger)

## Override Protocol

If a task genuinely requires bypassing a constraint:

1. **Stop** before taking the action
2. **Explain** why the constraint applies
3. **Justify** why bypassing is necessary
4. **Propose** the specific action to take
5. **Wait** for explicit human approval
6. **Document** the exception in the commit message

**Example:**
```
"This task requires modifying .github/workflows/deploy.yml 
(normally protected). The change adds a new test stage before 
deployment. Should I proceed with this modification?"
```

---

*These constraints are immutable unless overridden by explicit human approval in the current session.*
