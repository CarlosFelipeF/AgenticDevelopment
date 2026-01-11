# CONVENTIONS.md

> Code Style, Patterns & Naming Conventions  
> *For AI agents: Read this before writing code.*

---

## Quick Reference

| Category | Convention |
|----------|------------|
| **Indentation** | [Spaces/Tabs] × [Number] |
| **Line length** | [Max chars] |
| **Quotes** | [Single/Double] |
| **Semicolons** | [Yes/No] |
| **Trailing commas** | [Yes/No] |
| **File naming** | [kebab-case / camelCase / PascalCase] |

---

## Naming Conventions

### Files & Directories

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Utilities | camelCase | `formatDate.ts` |
| Constants | SCREAMING_SNAKE | `constants/API_ROUTES.ts` |
| Types | PascalCase | `types/User.ts` |
| Tests | Same as source + `.test` | `UserProfile.test.tsx` |
| Styles | Same as component | `UserProfile.module.css` |

### Variables & Functions

| Type | Convention | Example |
|------|------------|---------|
| Variables | camelCase | `const userName = ...` |
| Constants | SCREAMING_SNAKE | `const MAX_RETRIES = 3` |
| Functions | camelCase + verb | `getUserById()` |
| Boolean vars | is/has/should prefix | `isLoading`, `hasError` |
| Event handlers | handle + Event | `handleClick()`, `handleSubmit()` |
| Async functions | Descriptive, often get/fetch | `fetchUserData()` |

### Classes & Types

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `class UserService` |
| Interfaces | PascalCase (no I prefix) | `interface User` |
| Type aliases | PascalCase | `type UserId = string` |
| Enums | PascalCase + SCREAMING values | `enum Status { ACTIVE, INACTIVE }` |
| Generics | Single uppercase or descriptive | `T`, `TData`, `TError` |

---

## Code Style

### Imports

Order imports in this sequence:
1. External packages (node_modules)
2. Internal absolute paths
3. Relative paths (parent first, then siblings)
4. Type imports

```typescript
// 1. External
import React from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Internal absolute
import { api } from '@/lib/api';
import { Button } from '@/components/ui';

// 3. Relative
import { UserCard } from '../UserCard';
import { formatName } from './utils';

// 4. Types
import type { User } from '@/types';
```

### Exports

- Prefer named exports over default exports
- Exception: Page/Route components may use default exports
- Group related exports in index files

```typescript
// Preferred
export function UserProfile() { ... }
export const USER_DEFAULTS = { ... };

// Acceptable for pages
export default function HomePage() { ... }
```

### Functions

- Use arrow functions for callbacks and inline functions
- Use regular functions for top-level declarations
- Extract complex logic into named functions

```typescript
// Top-level: regular function
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Callback: arrow function
const filtered = items.filter((item) => item.active);

// Avoid anonymous complex logic
// ❌ Bad
onClick={() => {
  const data = transform(input);
  api.save(data);
  notify('Saved');
}}

// ✅ Good
const handleSave = () => {
  const data = transform(input);
  api.save(data);
  notify('Saved');
};
onClick={handleSave}
```

### Error Handling

```typescript
// Always catch and handle errors appropriately
try {
  const result = await riskyOperation();
  return result;
} catch (error) {
  // Log with context
  logger.error('Operation failed', { error, context });
  
  // Re-throw or return fallback based on criticality
  throw new AppError('OPERATION_FAILED', { cause: error });
}

// Use Result types for recoverable errors
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };
```

---

## Component Patterns

### React Components

```typescript
// Props interface above component
interface UserCardProps {
  user: User;
  onEdit?: (user: User) => void;
  className?: string;
}

// Destructure props with defaults
export function UserCard({ 
  user, 
  onEdit, 
  className = '' 
}: UserCardProps) {
  // Hooks at the top
  const [isEditing, setIsEditing] = useState(false);
  const { data, isLoading } = useUserData(user.id);

  // Derived state
  const displayName = user.firstName + ' ' + user.lastName;

  // Handlers
  const handleEditClick = () => {
    setIsEditing(true);
    onEdit?.(user);
  };

  // Early returns for loading/error states
  if (isLoading) return <Skeleton />;

  // Main render
  return (
    <div className={`user-card ${className}`}>
      {/* ... */}
    </div>
  );
}
```

### Hooks

```typescript
// Custom hooks start with 'use'
function useUserData(userId: string) {
  // Implementation
}

// Return object for multiple values
function useForm<T>(initial: T) {
  const [values, setValues] = useState(initial);
  const [errors, setErrors] = useState({});
  
  return {
    values,
    errors,
    setValue: (key, value) => { ... },
    reset: () => { ... },
  };
}
```

---

## API & Data Patterns

### API Calls

```typescript
// Centralize API calls in service modules
// src/services/userService.ts

export const userService = {
  async getById(id: string): Promise<User> {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  async create(data: CreateUserDto): Promise<User> {
    const response = await api.post('/users', data);
    return response.data;
  },
};
```

### Data Transformation

```typescript
// Keep API types separate from UI types
// Transform at the boundary

interface ApiUser {
  user_id: string;
  first_name: string;
  created_at: string;
}

interface User {
  id: string;
  firstName: string;
  createdAt: Date;
}

function toUser(apiUser: ApiUser): User {
  return {
    id: apiUser.user_id,
    firstName: apiUser.first_name,
    createdAt: new Date(apiUser.created_at),
  };
}
```

---

## Testing Conventions

### Test Structure

```typescript
describe('UserService', () => {
  describe('getById', () => {
    it('returns user when found', async () => {
      // Arrange
      const userId = 'user-123';
      mockApi.get.mockResolvedValue({ data: mockUser });

      // Act
      const result = await userService.getById(userId);

      // Assert
      expect(result).toEqual(mockUser);
      expect(mockApi.get).toHaveBeenCalledWith('/users/user-123');
    });

    it('throws NotFoundError when user does not exist', async () => {
      // Arrange
      mockApi.get.mockRejectedValue(new Error('Not found'));

      // Act & Assert
      await expect(userService.getById('invalid'))
        .rejects.toThrow(NotFoundError);
    });
  });
});
```

### Test Naming

```
// Pattern: should [expected behavior] when [condition]
it('should return empty array when no users match filter')
it('should throw ValidationError when email is invalid')
it('should update user and emit event when save succeeds')
```

---

## Comments & Documentation

### When to Comment

```typescript
// ✅ Comment: Explain WHY, not WHAT
// Rate limit to prevent API abuse (max 100 requests/minute per user)
const RATE_LIMIT = 100;

// ✅ Comment: Document non-obvious behavior
// Returns null instead of throwing to allow optional chaining
function findUser(id: string): User | null { ... }

// ❌ Don't: State the obvious
// Increment the counter
count++;
```

### JSDoc for Public APIs

```typescript
/**
 * Calculates the total price including tax and discounts.
 * 
 * @param items - Cart items to calculate
 * @param taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @returns Total price in cents
 * 
 * @example
 * const total = calculateTotal(cartItems, 0.08);
 */
function calculateTotal(items: CartItem[], taxRate: number): number {
  // ...
}
```

---

## Git Conventions

### Commit Messages

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `security`

**Examples**:
```
feat(auth): add OAuth2 login flow
fix(cart): prevent negative quantities
docs(readme): add deployment instructions
refactor(api): extract validation middleware
security(deps): update vulnerable package
```

### Branch Names

```
<type>/<issue-id>-<brief-description>

Examples:
feat/123-user-profile-page
fix/456-cart-total-calculation
refactor/789-extract-validation
```

---

## Project-Specific Conventions

<!-- Add project-specific conventions here -->

### [Category]

[Convention details]

---

## Tooling Configuration

### Formatter

Tool: [Prettier / Black / rustfmt / etc.]

```bash
# Format all files
npm run format

# Check formatting
npm run format:check
```

### Linter

Tool: [ESLint / Ruff / Clippy / etc.]

```bash
# Run linter
npm run lint

# Auto-fix issues
npm run lint:fix
```

### Type Checker

Tool: [TypeScript / mypy / etc.]

```bash
# Type check
npm run typecheck
```

---

## Related Documentation

- `AGENTS.md` — AI agent guidelines
- `ARCHITECTURE.md` — System design
- `TESTING.md` — Testing strategy
- `.editorconfig` — Editor settings
- `prettier.config.js` — Formatter config
- `eslint.config.js` — Linter config

---

**Last Updated**: YYYY-MM-DD  
**Owner**: [Team/Person]
