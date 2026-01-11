# TESTING.md

> Testing Strategy & Guidelines  
> *For AI agents: Read this before submitting PRs.*

---

## Quick Reference

| Action | Command | Approval Needed |
|--------|---------|-----------------|
| Run single test | `npm test -- path/to/file.test.ts` | No |
| Run component tests | `npm test -- --filter=ComponentName` | No |
| Run all tests | `npm test` | Ask first (may be slow) |
| Run with coverage | `npm test -- --coverage` | Ask first |
| Update snapshots | `npm test -- -u` | Ask first |

---

## Testing Philosophy

### Principles

1. **Test behavior, not implementation** — Tests should verify what the code does, not how it does it
2. **Fast feedback** — Unit tests should run in milliseconds, integration tests in seconds
3. **Reliable** — Tests should not be flaky; if a test fails intermittently, fix or remove it
4. **Maintainable** — Tests are code too; they should be readable and refactorable
5. **Meaningful** — Every test should catch real bugs; delete tests that don't

### Testing Pyramid

```
         /\
        /  \        E2E Tests (Few)
       /----\       - User journeys
      /      \      - Critical paths only
     /--------\     Integration Tests (Some)
    /          \    - API endpoints
   /            \   - Database operations
  /--------------\  Unit Tests (Many)
 /                \ - Functions
/                  \- Components
```

---

## Test Types

### Unit Tests

**Purpose**: Test individual functions, components, or modules in isolation.

**Location**: `src/**/__tests__/` or `src/**/*.test.ts`

**Characteristics**:
- No external dependencies (database, network, filesystem)
- Fast (< 100ms per test)
- Deterministic (same input → same output)
- Mocked dependencies

**Example**:
```typescript
describe('formatCurrency', () => {
  it('formats positive amounts correctly', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
  });

  it('handles zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('formats negative amounts with parentheses', () => {
    expect(formatCurrency(-100)).toBe('($100.00)');
  });
});
```

### Integration Tests

**Purpose**: Test interactions between components or with external systems.

**Location**: `tests/integration/` or `src/**/*.integration.test.ts`

**Characteristics**:
- May use real database (test instance)
- May make real HTTP calls (to test server)
- Slower (seconds per test)
- Tests API contracts

**Example**:
```typescript
describe('POST /api/users', () => {
  beforeEach(async () => {
    await db.clear('users');
  });

  it('creates user and returns 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test' });

    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'test@example.com',
    });
  });
});
```

### End-to-End (E2E) Tests

**Purpose**: Test complete user flows through the application.

**Location**: `tests/e2e/` or `e2e/`

**Characteristics**:
- Uses real browser (Playwright, Cypress)
- Tests actual user experience
- Slowest (seconds to minutes)
- Most realistic but most brittle

**Example**:
```typescript
test('user can complete checkout', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('#email', 'user@example.com');
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL(/\/confirmation/);
  await expect(page.locator('.order-number')).toBeVisible();
});
```

---

## Test Requirements by Change Type

| Change Type | Required Tests | Coverage Target |
|-------------|----------------|-----------------|
| New feature | Unit + Integration | 80%+ for new code |
| Bug fix | Regression test that fails without fix | N/A |
| Refactor | Existing tests must pass | No decrease |
| Performance | Benchmark tests | N/A |
| Security fix | Security-specific tests | N/A |

---

## Writing Good Tests

### Structure (AAA Pattern)

```typescript
it('description of expected behavior', () => {
  // Arrange - Set up test data and conditions
  const user = createTestUser({ role: 'admin' });
  const resource = createTestResource({ ownerId: 'other-user' });

  // Act - Perform the action being tested
  const result = checkPermission(user, resource, 'delete');

  // Assert - Verify the expected outcome
  expect(result).toBe(true);
});
```

### Test Naming

Use descriptive names that explain what is being tested:

```typescript
// ✅ Good - Clear behavior description
it('returns empty array when no items match filter')
it('throws ValidationError when email format is invalid')
it('sends notification email after successful registration')

// ❌ Bad - Vague or implementation-focused
it('works correctly')
it('calls the function')
it('test case 1')
```

### Assertions

```typescript
// ✅ Prefer specific assertions
expect(user.name).toBe('Alice');
expect(items).toHaveLength(3);
expect(response.status).toBe(200);

// ❌ Avoid vague assertions
expect(user).toBeTruthy();
expect(items.length > 0).toBe(true);
```

### Test Data

```typescript
// Use factories for consistent test data
const user = createUser({ 
  name: 'Test User',
  email: 'test@example.com' 
});

// Use meaningful values that relate to the test
it('rejects users under 18', () => {
  const minor = createUser({ birthDate: '2010-01-01' }); // Clearly under 18
  expect(validateAge(minor)).toBe(false);
});
```

---

## Mocking

### When to Mock

| Mock When | Don't Mock When |
|-----------|-----------------|
| External APIs | Testing the actual integration |
| Databases (unit tests) | Integration tests |
| Time/Date | Time is irrelevant to test |
| Random values | Randomness is the feature |
| Slow operations | Performance is being tested |

### Mocking Patterns

```typescript
// Mock external service
jest.mock('@/services/emailService', () => ({
  sendEmail: jest.fn().mockResolvedValue({ success: true }),
}));

// Mock with implementation
const mockFetch = jest.fn().mockImplementation((url) => {
  if (url.includes('/users')) {
    return Promise.resolve({ json: () => mockUsers });
  }
  return Promise.reject(new Error('Not found'));
});

// Restore mocks between tests
afterEach(() => {
  jest.restoreAllMocks();
});
```

---

## Snapshot Testing

### When to Use

- UI component output
- Serializable data structures
- Error messages
- API responses (carefully)

### When NOT to Use

- Large objects that change frequently
- Dates or timestamps
- Random values
- Implementation details

### Workflow

```bash
# Generate or update snapshots
npm test -- -u

# Review changes carefully before committing
git diff **/__snapshots__/*

# In PR review, verify snapshot changes are intentional
```

### Best Practices

```typescript
// ✅ Small, focused snapshots
expect(component.toJSON()).toMatchSnapshot();

// ✅ Inline snapshots for small values
expect(formatError(error)).toMatchInlineSnapshot(`
  "Error: Invalid input
    at line 5, column 10"
`);

// ❌ Avoid huge snapshots
expect(entirePageHtml).toMatchSnapshot(); // Too big, hard to review
```

---

## Coverage

### Targets

| Category | Target | Enforced |
|----------|--------|----------|
| Statements | 80% | Yes |
| Branches | 75% | Yes |
| Functions | 80% | Yes |
| Lines | 80% | Yes |

### Running Coverage

```bash
# Generate coverage report
npm test -- --coverage

# View HTML report
open coverage/lcov-report/index.html
```

### What to Cover

- ✅ Business logic
- ✅ Edge cases
- ✅ Error paths
- ✅ Public API
- ❌ Third-party code
- ❌ Configuration files
- ❌ Type definitions

---

## CI/CD Integration

### Pipeline Stages

1. **Lint** — Code style checks
2. **Type Check** — Static type analysis
3. **Unit Tests** — Fast, isolated tests
4. **Integration Tests** — API and database tests
5. **E2E Tests** — Browser-based tests (optional per PR)

### PR Requirements

- [ ] All tests pass
- [ ] No decrease in coverage
- [ ] New features have tests
- [ ] Bug fixes have regression tests

---

## Debugging Tests

### Common Issues

| Problem | Solution |
|---------|----------|
| Test passes alone, fails in suite | Check for shared state, missing cleanup |
| Flaky tests | Remove time dependencies, improve assertions |
| Slow tests | Mock external calls, reduce setup |
| Snapshot failures | Review changes, update intentionally |

### Debug Commands

```bash
# Run single test file
npm test -- path/to/file.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="user creation"

# Run with verbose output
npm test -- --verbose

# Debug in watch mode
npm test -- --watch
```

---

## Test Data Management

### Fixtures

```typescript
// tests/fixtures/users.ts
export const testUsers = {
  admin: { id: 'admin-1', role: 'admin', email: 'admin@test.com' },
  member: { id: 'member-1', role: 'member', email: 'member@test.com' },
  guest: { id: 'guest-1', role: 'guest', email: null },
};
```

### Factories

```typescript
// tests/factories/userFactory.ts
export function createUser(overrides: Partial<User> = {}): User {
  return {
    id: `user-${Math.random().toString(36).slice(2)}`,
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date(),
    ...overrides,
  };
}
```

### Database Seeding

```typescript
// tests/setup/seed.ts
export async function seedDatabase() {
  await db.users.createMany({ data: testUsers });
  await db.products.createMany({ data: testProducts });
}

export async function cleanDatabase() {
  await db.users.deleteMany();
  await db.products.deleteMany();
}
```

---

## Related Documentation

- `AGENTS.md` — AI agent guidelines
- `CONVENTIONS.md` — Code style
- `ARCHITECTURE.md` — System design
- `jest.config.js` — Test configuration
- `tests/README.md` — Test-specific setup

---

**Last Updated**: YYYY-MM-DD  
**Owner**: [Team/Person]
