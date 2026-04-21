---
name: draft-cli-dev
description: >
  Use the repo-local Draft CLI for development and testing with an isolated development port. Trigger this skill whenever the task is to work on Draft CLI itself, test local Draft CLI changes from this repository, run a development Draft daemon, verify repo-local Draft behavior, or avoid conflicts with another installed/global Draft CLI workflow such as OpenClaw on the same machine.
---

# Draft CLI Dev

Use this skill when the task is about developing or testing Draft CLI from this repository rather than using the installed global `draft` binary.

This skill exists to isolate the Draft CLI development lane from other Draft workflows on the same machine.

## Use This Skill When

- working on `products/notion-editor/cli`
- testing Draft CLI changes from the repo
- starting a local Draft daemon for CLI development
- opening workspace files through the repo-local CLI
- avoiding conflicts with OpenClaw or another account using a different Draft daemon

## Do Not Use This Skill When

- the user wants the installed global `draft` CLI on PATH
- the task is normal Draft page automation unrelated to CLI development
- the task is headless page automation for CI or remote agents; use `draft-headless-pages` instead

## Development Contract

- Prefer the repo-local CLI under `products/notion-editor/cli`.
- Do not use the global `draft` binary unless the user explicitly asks for it.
- Use the development port `31414` by default.
- Respect an explicit user override if they intentionally provide `--port`.

## Entry Point

Use the bundled wrapper script:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh <draft-args...>
```

What the wrapper does:

- resolves the repository root
- targets `products/notion-editor/cli/bin/draft.js`
- builds the local CLI when `dist/index.js` is missing or when sources are newer than the build output
- injects `--port 31414` unless the command already specifies `--port` or `-p`
- prints the resolved CLI path and active port to stderr for clarity

## Connection-First Workflow

For repo-local CLI development, start from status and then choose the runtime that matches the lane you are testing:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh status --json
skills/draft-cli-dev/scripts/run-local-draft.sh start-server --mode workspace --workspace "$PWD"
skills/draft-cli-dev/scripts/run-local-draft.sh status --json
```

If status reports `DAEMON_OFFLINE`, start the daemon on the dev port.

- default/current CLI lane: `skills/draft-cli-dev/scripts/run-local-draft.sh start-server`
- explicit workspace lane: `skills/draft-cli-dev/scripts/run-local-draft.sh start-server --mode workspace --workspace "$PWD"`
- legacy browser-backed compatibility lane: `skills/draft-cli-dev/scripts/run-local-draft.sh start-server --runtime v1_DEPRECATED`

If status reports `BROWSER_NOT_CONNECTED`, run:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh daemon
```

Treat `daemon` as the browser pair/retarget command, not as the general startup path.

Proceed only once `status --json` reports `READY` for the dev port.

## Common Commands

Check status:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh status --json
```

Start local mode:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh start-server
```

Start legacy browser-backed compatibility mode:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh start-server --runtime v1_DEPRECATED
```

Start workspace mode:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh start-server --mode workspace --workspace "$PWD"
```

Open a workspace file:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh workspace open docs/sessions/<session>/task.md
```

Stop the dev daemon:

```bash
skills/draft-cli-dev/scripts/run-local-draft.sh stop-server
```

## Coexistence Rules

This skill is the development lane.

Normal Draft skills or OpenClaw usage should stay on their own binary path and port.

Recommended split:

- `draft-cli-dev`: repo-local CLI on `31414`
- normal Draft/OpenClaw workflow: installed CLI on a separate explicit port

This prevents the most common development conflict on a shared Mac where the dev workflow and the automation workflow accidentally attach to the same daemon.

## Failure Handling

- If the local CLI build is missing or stale, let the wrapper rebuild it.
- If the dev daemon is offline, start it through the wrapper instead of using the global `draft`.
- If the test case explicitly needs browser-backed behavior, start it with `--runtime v1_DEPRECATED`.
- If the wrong daemon is active, stop the dev daemon through the wrapper and restart it on the dev port.
- If another workflow is already using `31414`, either stop that conflicting process or rerun with an explicit `--port`.

## Notes

- The wrapper honors `DRAFT_CLI_DEV_PORT` if you need to change the default development port for a specific session.
- Set `DRAFT_CLI_DEV_SKIP_BUILD=1` only when you intentionally want to skip the local rebuild check.
