# GLOSSARY.md

> Domain Terminology & Definitions  
> *For AI agents: Consult when encountering unfamiliar terms.*

---

## How to Use This Document

This glossary defines domain-specific terms, acronyms, and concepts used in this project. When you encounter an unfamiliar term in code, comments, or documentation, check here first.

**Format**:
```
**Term** — Definition. [Context/Usage]
```

---

## Business Domain

<!-- Add your domain-specific terms here -->

**[Term 1]** — Definition of the term. [Where/how it's used in the codebase]

**[Term 2]** — Definition of the term. [Where/how it's used in the codebase]

---

## Technical Terms

### Architecture

**Bounded Context** — A logical boundary within which a particular domain model is defined and applicable. Different bounded contexts may have different meanings for the same term.

**Aggregate** — A cluster of domain objects treated as a single unit for data changes. Has a root entity that controls access.

**Event Sourcing** — Storing the state of an entity as a sequence of events rather than current state.

**CQRS** — Command Query Responsibility Segregation. Separating read and write operations into different models.

### API

**Endpoint** — A specific URL path that accepts requests (e.g., `/api/users/:id`).

**DTO** — Data Transfer Object. A plain object used to transfer data between layers.

**Middleware** — Code that runs between receiving a request and sending a response.

**Rate Limiting** — Restricting the number of requests a client can make in a time period.

### Database

**Migration** — A versioned change to the database schema.

**Seed Data** — Initial data loaded into the database for development/testing.

**Transaction** — A sequence of operations treated as a single atomic unit.

**Index** — A database structure that improves query performance on specific columns.

### Testing

**Fixture** — Predefined test data used across multiple tests.

**Mock** — A simulated object that mimics the behavior of a real object.

**Stub** — A minimal implementation that returns predefined responses.

**Snapshot** — A recorded output used to detect unexpected changes.

### DevOps

**CI/CD** — Continuous Integration / Continuous Deployment. Automated build, test, and deploy pipeline.

**Container** — An isolated environment for running applications (e.g., Docker).

**Environment Variable** — Configuration value set outside the application code.

**Rollback** — Reverting to a previous version after a failed deployment.

---

## Project-Specific Terms

<!-- Add terms unique to this project -->

### [Category 1]

**[Term]** — Definition. [Context]

### [Category 2]

**[Term]** — Definition. [Context]

---

## Acronyms

| Acronym | Full Form | Meaning |
|---------|-----------|---------|
| API | Application Programming Interface | A way for applications to communicate |
| CRUD | Create, Read, Update, Delete | Basic data operations |
| DRY | Don't Repeat Yourself | Principle to avoid code duplication |
| JWT | JSON Web Token | Token format for authentication |
| ORM | Object-Relational Mapping | Maps database tables to code objects |
| REST | Representational State Transfer | API design pattern using HTTP methods |
| SDK | Software Development Kit | Libraries for interacting with a service |
| SPA | Single Page Application | Web app that loads once and updates dynamically |
| SSO | Single Sign-On | One login for multiple applications |
| TDD | Test-Driven Development | Write tests before implementation |
| UUID | Universally Unique Identifier | A 128-bit identifier |

---

## Code Patterns

### Naming Prefixes

| Prefix | Meaning | Example |
|--------|---------|---------|
| `is` | Boolean state | `isLoading`, `isValid` |
| `has` | Boolean possession | `hasPermission`, `hasChildren` |
| `should` | Boolean recommendation | `shouldUpdate`, `shouldRetry` |
| `on` | Event handler (prop) | `onClick`, `onSubmit` |
| `handle` | Event handler (internal) | `handleClick`, `handleSubmit` |
| `get` | Retrieve value | `getUserById`, `getConfig` |
| `set` | Assign value | `setUser`, `setConfig` |
| `create` | Instantiate new | `createUser`, `createOrder` |
| `update` | Modify existing | `updateUser`, `updateOrder` |
| `delete` | Remove | `deleteUser`, `deleteOrder` |
| `fetch` | Async data retrieval | `fetchUsers`, `fetchData` |
| `use` | React hook | `useUser`, `useAuth` |

### Common Suffixes

| Suffix | Meaning | Example |
|--------|---------|---------|
| `List` | Array of items | `userList`, `orderList` |
| `Map` | Key-value collection | `userMap`, `configMap` |
| `Set` | Unique collection | `tagSet`, `idSet` |
| `Count` | Numeric count | `userCount`, `itemCount` |
| `Id` | Identifier | `userId`, `orderId` |
| `Dto` | Data transfer object | `UserDto`, `OrderDto` |
| `Entity` | Database entity | `UserEntity`, `OrderEntity` |
| `Service` | Business logic class | `UserService`, `EmailService` |
| `Controller` | Request handler | `UserController`, `AuthController` |
| `Repository` | Data access layer | `UserRepository`, `OrderRepository` |
| `Provider` | React context provider | `AuthProvider`, `ThemeProvider` |
| `Context` | React context | `AuthContext`, `ThemeContext` |
| `Hook` | Custom hook | `useUserHook` (rarely used, just `useUser`) |

---

## Status Values

### Common Status Enums

| Status | Meaning | Typical Flow |
|--------|---------|--------------|
| `PENDING` | Awaiting processing | Initial state |
| `PROCESSING` | Currently being handled | After pending |
| `COMPLETED` | Successfully finished | Terminal success |
| `FAILED` | Encountered error | Terminal failure |
| `CANCELLED` | User cancelled | Terminal user action |
| `EXPIRED` | Time limit exceeded | Terminal timeout |

### Order/Transaction States

| Status | Meaning |
|--------|---------|
| `DRAFT` | Not yet submitted |
| `SUBMITTED` | Awaiting approval |
| `APPROVED` | Ready for processing |
| `IN_PROGRESS` | Being fulfilled |
| `SHIPPED` | Sent to customer |
| `DELIVERED` | Received by customer |
| `REFUNDED` | Payment returned |

---

## Error Codes

| Code | Meaning | HTTP Status |
|------|---------|-------------|
| `NOT_FOUND` | Resource doesn't exist | 404 |
| `UNAUTHORIZED` | Not logged in | 401 |
| `FORBIDDEN` | Logged in but not permitted | 403 |
| `VALIDATION_ERROR` | Invalid input | 400 |
| `CONFLICT` | Resource already exists | 409 |
| `RATE_LIMITED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |

---

## External Service Terms

<!-- Add terms from third-party services you integrate with -->

### [Service Name]

**[Term]** — Definition in context of this service.

---

## Adding New Terms

When adding a new term:

1. Place it in the appropriate category
2. Use the format: `**Term** — Definition. [Context]`
3. Include examples if helpful
4. Link to related terms if applicable
5. Update the table of contents if adding a new category

---

## Related Documentation

- `ARCHITECTURE.md` — System design context
- `CONVENTIONS.md` — Naming conventions
- `README.md` — Project overview
- External: [Link to domain documentation]

---

**Last Updated**: YYYY-MM-DD  
**Owner**: [Team/Person]
