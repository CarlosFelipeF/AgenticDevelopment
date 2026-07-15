# PROTOCOLS.md — Moved

The slash-command catalogue that used to live here has moved to `skills/` (one
`SKILL.md` per command: `plan`, `design`, `review`, `security-review`, `commit`,
`branch`, `pr`, `test`, `coverage`, `doc`, `changelog`, `debug`, `trace`,
`refactor`, `cleanup`, `status`, `recap`).

Prose commands in a markdown file were never executable — they only worked if
a model happened to read and follow them. Skills are loaded and can be
invoked the same way (`/plan`, `/review`, ...), but they also carry a
`description` the model uses to decide when to invoke them on its own.

Custom commands can still be extended per-project by adding a directory
under `skills/` — see `.agent/PROJECT.md`.
