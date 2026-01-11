# ARCHITECTURE.md

> System Design & Architecture Documentation  
> *For AI agents: Read this before making major changes.*

---

## Overview

<!-- Brief description of what this system does -->

**Purpose**: [One-line description of the system's purpose]

**Type**: [Web app / API service / CLI tool / Library / Monorepo / etc.]

**Primary Users**: [Who uses this system]

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        [System Name]                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│  │  Client  │────▶│   API    │────▶│ Database │               │
│  │  (Web)   │     │  Server  │     │ (Postgres)│               │
│  └──────────┘     └──────────┘     └──────────┘               │
│                         │                                       │
│                         ▼                                       │
│                   ┌──────────┐                                 │
│                   │ External │                                 │
│                   │ Services │                                 │
│                   └──────────┘                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

<!-- Replace with actual architecture diagram using ASCII, Mermaid, or link to image -->

---

## Directory Structure

```
/
├── src/
│   ├── components/     # [Description]
│   ├── lib/            # [Description]
│   ├── pages/          # [Description]
│   ├── api/            # [Description]
│   └── types/          # [Description]
├── tests/
│   ├── unit/           # [Description]
│   └── integration/    # [Description]
├── docs/               # [Description]
├── scripts/            # [Description]
└── config/             # [Description]
```

---

## Core Components

### Component 1: [Name]

**Location**: `src/[path]`

**Purpose**: [What this component does]

**Dependencies**: [What it depends on]

**Depended on by**: [What depends on it]

**Key files**:
- `file1.ts` — [Purpose]
- `file2.ts` — [Purpose]

---

### Component 2: [Name]

**Location**: `src/[path]`

**Purpose**: [What this component does]

**Dependencies**: [What it depends on]

**Depended on by**: [What depends on it]

---

## Data Flow

### Request Lifecycle

1. **Client** sends request to [endpoint]
2. **Middleware** handles [auth/validation/etc.]
3. **Controller** processes and validates
4. **Service** executes business logic
5. **Repository** accesses data store
6. **Response** returns to client

### State Management

- **Server state**: [How server state is managed]
- **Client state**: [How client state is managed]
- **Cache**: [Caching strategy]

---

## External Dependencies

### Services

| Service | Purpose | Env Var | Criticality |
|---------|---------|---------|-------------|
| PostgreSQL | Primary database | `DATABASE_URL` | Critical |
| Redis | Caching/sessions | `REDIS_URL` | High |
| S3 | File storage | `AWS_*` | Medium |
| [Service] | [Purpose] | [Env var] | [Level] |

### Third-Party APIs

| API | Purpose | Rate Limits | Fallback |
|-----|---------|-------------|----------|
| [API name] | [Purpose] | [Limits] | [Fallback strategy] |

---

## Key Patterns

### Pattern 1: [Name]

**Used in**: [Where this pattern is used]

**Description**: [How the pattern works]

**Example**:
```typescript
// Example code showing the pattern
```

---

### Pattern 2: [Name]

**Used in**: [Where this pattern is used]

**Description**: [How the pattern works]

---

## Security Architecture

### Authentication

- **Method**: [JWT / Session / OAuth / etc.]
- **Implementation**: [Location/approach]
- **Token storage**: [Where tokens are stored]

### Authorization

- **Model**: [RBAC / ABAC / etc.]
- **Roles**: [List of roles]
- **Permission checks**: [How/where checked]

### Data Protection

- **Encryption at rest**: [Yes/No, method]
- **Encryption in transit**: [TLS version]
- **PII handling**: [How PII is handled]

---

## Performance Considerations

### Known Bottlenecks

1. [Bottleneck 1] — [Mitigation]
2. [Bottleneck 2] — [Mitigation]

### Scaling Strategy

- **Horizontal**: [How the system scales horizontally]
- **Vertical**: [Vertical scaling limits]
- **Caching**: [Cache strategy]

---

## Error Handling

### Error Categories

| Category | HTTP Code | Handling |
|----------|-----------|----------|
| Validation | 400 | Return field-level errors |
| Auth | 401/403 | Redirect to login |
| Not Found | 404 | Standard error page |
| Server | 500 | Log, alert, generic message |

### Logging

- **Location**: [Where logs go]
- **Levels**: [What levels are used]
- **Sensitive data**: [How sensitive data is handled in logs]

---

## Deployment Architecture

### Environments

| Environment | URL | Purpose |
|-------------|-----|---------|
| Development | localhost:3000 | Local development |
| Staging | staging.example.com | Pre-production testing |
| Production | example.com | Live system |

### CI/CD Pipeline

1. **Trigger**: [Push / PR / Manual]
2. **Build**: [Build steps]
3. **Test**: [Test stages]
4. **Deploy**: [Deployment method]

---

## Decision Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| YYYY-MM-DD | [Decision] | [Why] | [What else was considered] |

---

## Related Documentation

- `README.md` — Getting started
- `CONVENTIONS.md` — Code style and patterns
- `TESTING.md` — Testing strategy
- `AGENTS.md` — AI agent guidelines
- `API.md` — API documentation (if applicable)

---

**Last Updated**: YYYY-MM-DD  
**Owner**: [Team/Person]
