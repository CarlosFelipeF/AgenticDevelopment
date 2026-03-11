# CONVENTIONS.md — Code Style & Patterns

## General Principles

1. **Consistency over preference:** Follow existing project patterns
2. **Clarity over cleverness:** Readable code beats clever code
3. **Explicit over implicit:** Make behavior obvious
4. **Small functions:** Single responsibility, easy to test
5. **Meaningful names:** Intent-revealing identifiers

## Formatting Standards

### Automated Formatting

**Always run formatters before committing.** Check project for configured tools:

| Language | Formatters |
|----------|------------|
| JavaScript/TypeScript | Prettier, ESLint |
| Python | Ruff (recommended), or Black + isort |
| Go | gofmt, goimports |
| Rust | rustfmt |
| Java | google-java-format |
| CSS/SCSS | Prettier, Stylelint |

> **Note:** Ruff can replace both Black (formatting) and isort (import sorting) with better performance.

**Check for config files:**
```
.prettierrc, .eslintrc, pyproject.toml, ruff.toml, .editorconfig
```

### Indentation & Whitespace

- Follow project's `.editorconfig` if present
- Default: 2 spaces for JS/TS/JSON, 4 spaces for Python
- No trailing whitespace
- Single newline at end of file

## Naming Conventions

### Files & Directories

```
# Components (React/Vue)
UserProfile.tsx
user-profile.vue

# Modules
auth-service.ts
user_repository.py

# Tests
UserProfile.test.tsx
test_user_repository.py

# Styles
user-profile.module.css
_variables.scss
```

### Variables & Functions

```javascript
// JavaScript/TypeScript
const userName = 'value';          // camelCase for variables
function getUserById(id) {}        // camelCase for functions
const MAX_RETRY_COUNT = 3;         // SCREAMING_SNAKE for constants
class UserService {}               // PascalCase for classes
interface UserData {}              // PascalCase for interfaces
type UserId = string;              // PascalCase for types
```

```python
# Python
user_name = 'value'                # snake_case for variables
def get_user_by_id(id):            # snake_case for functions
MAX_RETRY_COUNT = 3                # SCREAMING_SNAKE for constants
class UserService:                 # PascalCase for classes
```

### Boolean Variables

Use prefixes that read as questions:
```javascript
isActive, hasPermission, canEdit, shouldRefresh, willUpdate
```

## Code Organization

### Module Structure

```
src/
├── components/          # UI components
├── services/            # Business logic
├── repositories/        # Data access
├── utils/               # Shared utilities
├── types/               # Type definitions
├── constants/           # Configuration constants
└── hooks/               # Custom hooks (React)
```

### File Structure Pattern

```typescript
// 1. Imports (grouped and sorted)
import { external } from 'external-package';

import { internal } from '@/internal';
import { local } from './local';

// 2. Types/Interfaces
interface Props {
  // ...
}

// 3. Constants
const DEFAULT_VALUE = 10;

// 4. Main export
export function Component({ prop }: Props) {
  // ...
}

// 5. Helper functions (if not extracted)
function helperFunction() {
  // ...
}
```

## Error Handling

### Error Messages

Write actionable error messages:
```javascript
// Bad
throw new Error('Invalid input');

// Good
throw new Error(
  `User ID must be a positive integer, received: ${userId}`
);
```

### Try-Catch Patterns

```javascript
// Catch specific errors when possible
try {
  await saveUser(user);
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle validation specifically
  } else if (error instanceof NetworkError) {
    // Handle network issues
  } else {
    // Re-throw unexpected errors
    throw error;
  }
}
```

## Documentation Standards

### Code Comments

```javascript
// Single-line: Explain WHY, not WHAT
// Rate limit to prevent API throttling
await delay(100);

/*
 * Multi-line for complex explanations:
 * - Point one
 * - Point two
 */

/**
 * JSDoc for public APIs:
 * @param userId - The unique user identifier
 * @returns The user object or null if not found
 * @throws {NotFoundError} When user doesn't exist
 */
function getUser(userId: string): User | null {
```

### When to Comment

- **Do comment:** Non-obvious business logic, workarounds, performance optimizations
- **Don't comment:** Obvious code, redundant descriptions, outdated information

## Type Safety

### TypeScript/Type Hints

```typescript
// Prefer explicit types for function signatures
function processUser(user: User): ProcessedUser {
  // Return type inference is fine for simple cases
  return { ...user, processed: true };
}

// Use strict null checks
function findUser(id: string): User | null {
  // ...
}

// Avoid `any` - use `unknown` if type is truly unknown
function parseInput(data: unknown): ParsedData {
  // Validate and narrow type
}
```

### Python Type Hints

```python
from typing import Optional, List

def get_user(user_id: str) -> Optional[User]:
    """Fetch user by ID."""
    pass

def process_users(users: List[User]) -> List[ProcessedUser]:
    """Process a list of users."""
    pass
```

## Anti-Patterns to Avoid

### Code Smells

- **God objects:** Classes doing too much
- **Deep nesting:** More than 3 levels of indentation
- **Magic numbers:** Unexplained numeric literals
- **Copy-paste code:** Duplicate logic not extracted
- **Long parameter lists:** More than 4 parameters

### Refactoring Triggers

When you see these, consider refactoring:
```javascript
// Long conditional chains → Strategy pattern or map
if (type === 'a') { } else if (type === 'b') { } else if ...

// Nested callbacks → async/await or promises
getData((data) => {
  process(data, (result) => {
    save(result, (saved) => { ...

// Feature envy → Move method to appropriate class
user.address.city.getTimeZone()
```

## Testing Conventions

### Test Naming

```javascript
// Describe what is being tested and expected outcome
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', () => {});
    it('should throw ValidationError for invalid email', () => {});
    it('should hash password before saving', () => {});
  });
});
```

### Test Structure (AAA)

```javascript
it('should calculate total with discount', () => {
  // Arrange
  const cart = new Cart();
  cart.addItem({ price: 100 });
  
  // Act
  const total = cart.calculateTotal(0.1); // 10% discount
  
  // Assert
  expect(total).toBe(90);
});
```

---

*Project-specific conventions should be documented in `.agent/PROJECT.md`.*
