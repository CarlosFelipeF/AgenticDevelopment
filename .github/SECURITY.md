# Security Policy

This framework shapes how AI agents behave in other people's repositories, so a weakness here
can spread. Thank you for reporting responsibly.

## What to report

- A command that gets past `hooks/scripts/guard-bash.py` and breaks a "Never"
  rule in `.agent/CONSTRAINTS.md`
- A rule, example or default that leads agents or adopters into an unsafe setup
- Unsafe CI, hook or permission examples (for example script injection or over-broad permissions)
- Wrong or misleading security guidance

## How to report

**Please do not open a public issue for a security problem.**

Use GitHub's private vulnerability reporting: go to the repository's **Security** tab and choose
**Report a vulnerability**. Include:

- What you found and why it matters
- Steps or a command to reproduce it
- The framework version (see `AGENTS.md`) and the AI tool you used

## What happens next

- We aim to acknowledge reports within 7 days.
- We fix confirmed issues, add a regression test where possible, and credit you in
  `CHANGELOG.md` unless you prefer otherwise.

## Supported versions

Only the latest release receives security fixes.
