---
name: draft-cli-dev
description: >
  Use the repo-local Draft CLI for development and testing with an isolated development port.
  Trigger this skill when working on `products/notion-editor/cli`, testing local Draft CLI changes,
  or avoiding collisions with an installed/global Draft CLI.
---

# Draft CLI Dev

Use this skill when developing or testing Draft CLI from this repository rather than using the
installed global `draft` binary.

## Contract

- Prefer the repo-local CLI under `products/notion-editor/cli`.
- Use development port `31414` by default.
- The only live-page runtime is headless v2.
- Do not use `draft daemon`, `--runtime v1_DEPRECATED`, `--mode workspace`, `draft open`, or `draft workspace ...`.

## Entry Point

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh <draft-args...>
```

The wrapper:

- resolves the repository root
- targets `products/notion-editor/cli/bin/draft.js`
- builds the local CLI when `dist/index.js` is missing or stale
- injects `--port 31414` unless the command already specifies `--port` or `-p`

## Common Commands

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh status --json
skills/draft-cli-dev/scripts/run-local-draft.sh start-server
skills/draft-cli-dev/scripts/run-local-draft.sh page ls --json
skills/draft-cli-dev/scripts/run-local-draft.sh stop-server
```

If status reports `DAEMON_OFFLINE`, run `start-server` and then re-check status. A `READY` state is
enough for headless page commands.
