# Agentic Development

A framework for governing AI coding agents, ensuring secure, consistent, and predictable behavior in software development workflows.

## Repository Structure

```
.
├── agent-governance-framework-v2/   # Agent behavioral rules and governance
│   ├── .agent/                      # Core protocol files (loaded by agents)
│   ├── AGENTS.md                    # Main entry point for agents
│   ├── ARCHITECTURE.md              # System design template
│   ├── TESTING.md                   # Test strategy documentation
│   ├── GLOSSARY.md                  # Domain terminology
│   └── AGENTIC-SECURITY-CHECKLIST.md # Security checklist for humans
│
└── Slash_Commands/                  # Reusable slash command definitions
    └── mvp-slash-command.md         # MVP planning command
```

---

## Slash_Commands/

**Purpose:** A library of reusable slash commands that can be used with AI coding assistants (Claude, Cursor, etc.) to standardize common development workflows.

### Available Commands

| Command | Description |
|---------|-------------|
| `/mvp [file]` | Tracer bullet MVP planning from a product spec |

### How to Use

Copy the contents of a slash command file and use it as a prompt prefix or custom instruction. Example:

```
/mvp prd.md
```

This triggers a structured MVP planning process that:
- Identifies critical path features
- Uses TDD methodology
- Creates modular documentation
- Outputs a phased implementation plan

---

## agent-governance-framework-v2/

**Purpose:** A comprehensive governance framework for AI coding agents, aligned with [OWASP Agentic Security Initiative](https://owasp.org/www-project-agentic-security/).

### For AI Agents

Start by loading `AGENTS.md`, which instructs agents to load governance files in order:

| File | Purpose |
|------|---------|
| `.agent/01-SECURITY.md` | Security behaviors (OWASP ASI01-10 aligned) |
| `.agent/02-CONSTRAINTS.md` | Permissions and boundaries |
| `.agent/03-WORKFLOW.md` | Git workflows, commits, branches |
| `.agent/04-CONVENTIONS.md` | Code style and patterns |
| `.agent/05-SESSIONS.md` | Session management protocols |
| `.agent/06-PROTOCOLS.md` | Slash command definitions |
| `.agent/07-PROJECT.md` | Project-specific overrides |

### For Human Developers

- **`AGENTIC-SECURITY-CHECKLIST.md`** — Platform and infrastructure security controls
- **`ARCHITECTURE.md`** — Template for documenting system architecture
- **`TESTING.md`** — Test strategy and commands
- **`GLOSSARY.md`** — Domain terminology definitions

### Key Features

- **Immutable Security Rules** — Agents cannot override core security constraints
- **Configurable Conventions** — Project-specific rules in `07-PROJECT.md`
- **OWASP Alignment** — Mapped to ASI01-10 threat categories
- **Social Engineering Protection** — Agents reject manipulation attempts

### Quick Start

1. Copy `agent-governance-framework-v2/` to your project root
2. Customize `.agent/07-PROJECT.md` for your project
3. Update `ARCHITECTURE.md`, `TESTING.md`, and `GLOSSARY.md`
4. Reference `AGENTS.md` in your AI assistant's context

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the framework.

## License

MIT License - see [LICENSE](LICENSE) for details.
