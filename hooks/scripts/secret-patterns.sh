#!/usr/bin/env bash
# Shared secret-detection patterns for block-secret-commit.sh and block-secret-write.sh.
# Kept in sync with the high-signal patterns in .agent/SECURITY.md (JWTs are left out:
# test fixtures use them constantly).
#
# The password pattern requires a quoted literal on purpose: `password = os.getenv(...)`
# and `password = None` are ordinary code, not hardcoded secrets. Provider key classes
# allow - and _ where the providers use them (Anthropic keys are sk-ant-...).
# shellcheck disable=SC2034  # used by the hooks that source this file
SECRET_PATTERN="BEGIN [A-Z ]*PRIVATE KEY|password[[:space:]]*=[[:space:]]*[\"'][^\"']+[\"']|(mongodb(\+srv)?|postgres(ql)?|mysql)://[^@[:space:]]+@|sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|glpat-[A-Za-z0-9_-]{20,}|(sk|rk)_live_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35}|xox[baprs]-[A-Za-z0-9-]{10,}"
