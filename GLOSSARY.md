# Glossary

> Domain terminology and project-specific definitions.
> Helps agents and new team members understand the codebase vocabulary.

## Domain Terms

<!-- Define business/domain terms used in your codebase -->

### User
A registered individual who can authenticate and interact with the system.
- **Code reference:** `src/models/User.ts`
- **Related:** Account, Profile, Session

### Account
The billing entity associated with one or more Users.
- **Code reference:** `src/models/Account.ts`
- **Related:** User, Subscription, Invoice

### Workspace
A collaborative space where team members share resources.
- **Code reference:** `src/models/Workspace.ts`
- **Related:** Team, Project, Resource

## Technical Terms

<!-- Define technical terms specific to your project -->

### Repository Pattern
Our data access abstraction layer. All database operations go through repositories.
- **Location:** `src/repositories/`
- **Pattern:** One repository per aggregate root

### Service Layer
Business logic layer that orchestrates domain operations.
- **Location:** `src/services/`
- **Naming:** `[Entity]Service.ts`

### DTO (Data Transfer Object)
Objects used for API request/response payloads.
- **Location:** `src/dtos/`
- **Naming:** `[Entity][Create|Update|Response]Dto.ts`

## Status Enums

### UserStatus
| Value | Description |
|-------|-------------|
| `PENDING` | Awaiting email verification |
| `ACTIVE` | Normal active state |
| `SUSPENDED` | Temporarily disabled |
| `DELETED` | Soft-deleted |

### OrderStatus
| Value | Description |
|-------|-------------|
| `DRAFT` | Not yet submitted |
| `PENDING` | Awaiting processing |
| `PROCESSING` | Being fulfilled |
| `COMPLETED` | Successfully fulfilled |
| `CANCELLED` | Cancelled by user or system |

## Abbreviations

| Abbreviation | Full Term | Context |
|--------------|-----------|---------|
| API | Application Programming Interface | Web services |
| DTO | Data Transfer Object | Request/Response objects |
| E2E | End-to-End | Testing |
| FK | Foreign Key | Database |
| IAM | Identity and Access Management | Security |
| JWT | JSON Web Token | Authentication |
| MFA | Multi-Factor Authentication | Security |
| PII | Personally Identifiable Information | Data privacy |
| PK | Primary Key | Database |
| RBAC | Role-Based Access Control | Authorization |
| SSO | Single Sign-On | Authentication |

## Code Naming Conventions

### Prefixes

| Prefix | Meaning | Example |
|--------|---------|---------|
| `is` | Boolean flag | `isActive`, `isValid` |
| `has` | Ownership check | `hasPermission` |
| `can` | Capability check | `canEdit` |
| `get` | Retrieval | `getUser` |
| `set` | Mutation | `setStatus` |
| `create` | Instantiation | `createOrder` |
| `update` | Modification | `updateProfile` |
| `delete` | Removal | `deleteAccount` |
| `find` | Search (may return null) | `findByEmail` |
| `fetch` | External retrieval | `fetchFromAPI` |

### Suffixes

| Suffix | Meaning | Example |
|--------|---------|---------|
| `Dto` | Data transfer object | `UserDto` |
| `Entity` | Database entity | `UserEntity` |
| `Repository` | Data access | `UserRepository` |
| `Service` | Business logic | `UserService` |
| `Controller` | HTTP handler | `UserController` |
| `Middleware` | Request interceptor | `AuthMiddleware` |
| `Guard` | Access control | `RoleGuard` |
| `Validator` | Input validation | `EmailValidator` |

## Feature Flags

| Flag | Description | Default |
|------|-------------|---------|
| `FEATURE_NEW_CHECKOUT` | New checkout flow | off |
| `FEATURE_DARK_MODE` | Dark mode UI | on |
| `FEATURE_AI_ASSIST` | AI assistance features | off |

## Error Codes

| Code | Category | Description |
|------|----------|-------------|
| `E1001` | Auth | Invalid credentials |
| `E1002` | Auth | Token expired |
| `E1003` | Auth | Insufficient permissions |
| `E2001` | Validation | Invalid input format |
| `E2002` | Validation | Required field missing |
| `E3001` | Business | Resource not found |
| `E3002` | Business | Operation not allowed |
| `E4001` | External | Third-party service error |

## Event Types

| Event | Description | Payload |
|-------|-------------|---------|
| `user.created` | New user registered | `{ userId, email }` |
| `user.updated` | User profile changed | `{ userId, changes }` |
| `order.placed` | New order created | `{ orderId, userId, total }` |
| `order.completed` | Order fulfilled | `{ orderId, deliveredAt }` |

---

*Last updated: YYYY-MM-DD*
