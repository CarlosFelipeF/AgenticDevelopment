# PROJECT.md — Project Configuration

> **⚠️ TEMPLATE — replace with your project's real content, then delete this banner.**
> *Agents:* while this banner is present, everything below is **illustrative only**. Do not assume
> the files, names, commands or codes shown here exist in this repository.

> Template file. Customize this for your specific project.
> This file can override configurable rules from other `.agent/` files.

## Project Overview

<!-- Describe your project briefly -->
**Name:** [Project Name]
**Type:** [Web app | API | CLI | Library | Monorepo | ...]
**Primary Language:** [TypeScript | Python | Go | ...]
**Framework:** [Next.js | FastAPI | Express | ...]

## Team Context

<!-- Optional: Help agent understand team structure -->
**Team Size:** [Solo | Small team | Large team]
**Review Process:** [PR required | Pair programming | Self-merge allowed]

## Verification Commands (used by `/verify` and the Definition of Done)

<!-- Agents run these before claiming any task is done. Keep them fast and accurate. -->
```bash
npm test                       # Tests
npm run lint                   # Lint
npm run typecheck              # Type check
npm run build                  # Build
gitleaks git --staged          # Secret scan (see examples/enforcement/)
```

## Agent Settings

```yaml
# Autonomy: how much the agent may do without asking (see CONSTRAINTS.md)
autonomy: supervised           # supervised | standard | restricted

# AI attribution trailer added to agent commits (see WORKFLOW.md)
ai_trailer: "Co-authored-by"   # or "Assisted-by"

# Network: domains the agent may fetch to verify facts (everything else: ask first)
allowed_domains:
  - docs.python.org
  - developer.mozilla.org
  - registry.npmjs.org
  - pypi.org

# MCP servers, plugins and skills the team has reviewed and approved
approved_tools:
  - github                     # example — list only what you have reviewed

# Areas that always need a named human reviewer
sensitive_paths:
  - src/auth/**
  - src/payments/**
  - migrations/**
```

## Custom Commands

### Build & Run

```bash
# Development
npm run dev                    # Start dev server

# Production build
npm run build                  # Build for production

# Docker
docker-compose up -d           # Start with Docker
```

### Testing

```bash
# Unit tests
npm test                       # Run all tests

# With coverage
npm run test:coverage          # Run with coverage report

# E2E tests
npm run test:e2e               # Run end-to-end tests
```

### Linting & Formatting

```bash
# Lint
npm run lint                   # Check for issues
npm run lint:fix               # Auto-fix issues

# Format
npm run format                 # Format all files
```

## Project Structure

<!-- Document your project's directory layout -->
```
src/
├── app/                       # Next.js app router
├── components/                # React components
├── lib/                       # Shared utilities
├── services/                  # Business logic
└── types/                     # TypeScript types

tests/
├── unit/                      # Unit tests
├── integration/               # Integration tests
└── e2e/                       # End-to-end tests
```

## Environment Setup

### Required Environment Variables

```bash
# .env.example
DATABASE_URL=postgresql://...
API_KEY=your-api-key
NODE_ENV=development
```

### Local Development Prerequisites

- Node.js >= 18
- PostgreSQL 15+
- Redis (optional)

## Override Defaults

<!-- Override rules from other .agent/ files here -->
<!-- This section can override configurable settings from WORKFLOW.md and CONVENTIONS.md -->

<!-- You may tighten any default. You may NOT loosen the Non-Negotiable Rules in AGENTS.md
     or the "Never" list in CONSTRAINTS.md. -->

### Workflow Overrides

```yaml
# Branch naming (overrides WORKFLOW.md)
branch_prefix: "feature/"      # or your preference
commit_scope_required: false   # if scopes aren't used

# PR requirements
squash_merge: true
require_linear_history: true
```

### Convention Overrides

```yaml
# Formatting (overrides CONVENTIONS.md)
indent_size: 4                 # if different from default
max_line_length: 120

# Linting tools (overrides CONVENTIONS.md defaults)
python_formatter: "ruff"       # instead of black
python_linter: "ruff"          # instead of flake8
```

### Testing Overrides

```yaml
# Coverage thresholds
min_coverage: 80%
required_test_types:
  - unit
  - integration
```

## Integration Points

### CI/CD

- **Platform:** [GitHub Actions | GitLab CI | CircleCI | ...]
- **Config:** `.github/workflows/` or equivalent

### External Services

| Service | Purpose | Config Location |
|---------|---------|-----------------|
| PostgreSQL | Primary DB | DATABASE_URL env |
| Redis | Caching | REDIS_URL env |
| S3 | File storage | AWS_* env vars |

## Project-Specific Protocols

### Feature Development

1. Create issue in tracker
2. Create branch from `main`
3. Implement with tests
4. PR with required reviewers
5. Squash merge after approval

### Hotfix Process

1. Create branch from `main` 
2. Minimal fix with test
3. Fast-track review
4. Deploy immediately after merge

### Release Process

<!-- Document your release workflow -->
1. Create release branch
2. Update CHANGELOG.md
3. Bump version
4. Create PR to main
5. Tag after merge
6. Deploy

## Known Gotchas

<!-- Document project-specific quirks or issues -->
- The auth middleware must be applied before any protected routes
- Database migrations require manual approval in production
- The legacy API at `/v1/*` uses different auth

## Useful Resources

- [Project Wiki](link)
- [API Documentation](link)
- [Design System](link)
- [Runbook](link)

---

*Last updated: YYYY-MM-DD*
