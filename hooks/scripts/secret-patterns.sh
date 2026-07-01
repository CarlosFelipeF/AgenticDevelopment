#!/usr/bin/env bash
# Shared secret-detection patterns for block-secret-commit.sh and block-secret-write.sh.
# Kept in sync with the "Detection patterns to watch for" list in .agent/SECURITY.md.
SECRET_PATTERN='BEGIN [A-Z ]*PRIVATE KEY|password[[:space:]]*=[[:space:]]*[^[:space:]]+|(mongodb(\+srv)?|postgres(ql)?|mysql)://[^@[:space:]]+@|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}'
