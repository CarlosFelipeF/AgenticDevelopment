# Testing Strategy

> Document your project's testing approach here.
> This file should describe YOUR specific testing practices.

## Test Philosophy

<!-- Your team's approach to testing -->
- Write tests for behavior, not implementation
- Prefer integration tests for critical paths
- Unit tests for complex logic
- E2E tests for user journeys

## Test Structure

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── services/
│   └── utils/
├── integration/               # Component interaction tests
│   ├── api/
│   └── database/
├── e2e/                       # Full user journey tests
│   └── flows/
└── fixtures/                  # Shared test data
    ├── users.json
    └── orders.json
```

## Running Tests

### Quick Reference

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific suite
npm test -- --grep "UserService"

# Run in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e
```

### Test Commands by Type

| Command | Type | Duration | When to Run |
|---------|------|----------|-------------|
| `npm test` | Unit | ~10s | Every commit |
| `npm run test:integration` | Integration | ~60s | Before PR |
| `npm run test:e2e` | E2E | ~5min | Before deploy |

## Coverage Requirements

### Thresholds

```json
{
  "branches": 80,
  "functions": 85,
  "lines": 85,
  "statements": 85
}
```

### Critical Paths (100% coverage required)
- Authentication flows
- Payment processing
- Data validation

### Exceptions (documented)
- Third-party integration wrappers
- Generated code
- Development utilities

## Writing Tests

### Unit Test Pattern

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Arrange
      const userData = { email: 'test@example.com', name: 'Test' };
      
      // Act
      const user = await userService.createUser(userData);
      
      // Assert
      expect(user.id).toBeDefined();
      expect(user.email).toBe(userData.email);
    });

    it('should throw ValidationError for invalid email', async () => {
      // Arrange
      const userData = { email: 'invalid', name: 'Test' };
      
      // Act & Assert
      await expect(userService.createUser(userData))
        .rejects.toThrow(ValidationError);
    });
  });
});
```

### Integration Test Pattern

```typescript
describe('POST /api/users', () => {
  beforeEach(async () => {
    await db.clean();
    await db.seed('users');
  });

  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'new@example.com', name: 'New User' });
    
    expect(response.status).toBe(201);
    expect(response.body.user.id).toBeDefined();
  });
});
```

### E2E Test Pattern

```typescript
describe('User Registration Flow', () => {
  it('should complete registration successfully', async () => {
    await page.goto('/register');
    
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.welcome-message')).toBeVisible();
  });
});
```

## Test Data

### Fixtures

Located in `tests/fixtures/`:
- `users.json` - Standard user test data
- `orders.json` - Order test data
- `products.json` - Product catalog data

### Factories

```typescript
// tests/factories/user.ts
export const createUser = (overrides = {}) => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  name: faker.person.fullName(),
  createdAt: new Date(),
  ...overrides
});
```

### Database Seeding

```bash
# Seed test database
npm run db:seed:test

# Reset test database
npm run db:reset:test
```

## Mocking & Stubbing

### External Services

```typescript
// Mock external API
jest.mock('../services/stripe', () => ({
  createCharge: jest.fn().mockResolvedValue({ id: 'ch_test' })
}));
```

### Time-Dependent Tests

```typescript
beforeEach(() => {
  jest.useFakeTimers();
  jest.setSystemTime(new Date('2026-01-15'));
});

afterEach(() => {
  jest.useRealTimers();
});
```

## CI/CD Integration

### Pipeline Configuration

```yaml
test:
  stage: test
  script:
    - npm ci
    - npm run test:coverage
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
```

### Required Checks

- [ ] All tests pass
- [ ] Coverage thresholds met
- [ ] No new test warnings

## Debugging Tests

### Common Issues

**Flaky Tests:**
- Ensure proper test isolation
- Use explicit waits in E2E tests
- Check for timing dependencies

**Slow Tests:**
- Mock heavy dependencies
- Use test database transactions
- Run expensive tests separately

### Debug Commands

```bash
# Run single test with verbose output
npm test -- --verbose UserService.test.ts

# Debug in VS Code
# Add breakpoint, then F5 with Jest debug config
```

## Test Maintenance

### Review Schedule
- Weekly: Review flaky tests
- Monthly: Audit coverage gaps
- Quarterly: Review test strategy

### Deprecation Policy
- Mark deprecated tests with TODO comment
- Remove after 2 sprints if unused
- Document removal in changelog

---

*Last updated: YYYY-MM-DD*
