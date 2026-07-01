---
description: Use for complex features that need a technical design document covering architecture, API changes, data model, security, and rollout before implementation begins.
invoke-by: both
---

# /design — Technical Design Document

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
