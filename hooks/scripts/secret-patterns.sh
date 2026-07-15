#!/usr/bin/env bash
# Shared secret-detection patterns for block-secret-commit.sh and block-secret-write.sh.
# Kept in sync with the "Never commit" list in .agent/SECURITY.md.
#
# The password pattern requires a quoted literal on purpose: `password = os.getenv(...)`
# and `password = None` are ordinary code, not hardcoded secrets. Provider key classes
# allow - and _ where the providers use them (Anthropic keys are sk-ant-...).
SECRET_PATTERN="BEGIN [A-Z ]*PRIVATE KEY|password[[:space:]]*=[[:space:]]*[\"'][^\"']+[\"']|(mongodb(\+srv)?|postgres(ql)?|mysql)://[^@[:space:]]+@|sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}"
