---
name: draft-cli
description: >
  Manage and interact with "Draft" pages and documents using the @innosage/draft-cli.
  Use this skill whenever the user explicitly asks to read, create, list, patch, or append content to a "Draft page", "Draft doc", or their "Draft workspace" (e.g., "my draft page named 'Founder Sync'", "all the pages I have in my draft workspace", "Draft CLI").
  This connects to the Draft PWA (draft.innosage.co) via a local daemon to read or modify living documents.
  DO NOT use this skill for generalized writing tasks where "draft" is used as a verb (e.g., "draft an email", "draft a response") or when referring to local markdown/text files with "draft" in the name (e.g., "draft.md", "investor_update_draft.md"). Only use when interacting with the actual InnoSage Draft web application or Draft CLI tool.
  When triggered, ALWAYS follow the "Connection First" operational pattern: check status before any other command, and start the background server if it is not running.
compatibility: >
  Requires Node.js >= 18 and @innosage/draft-cli (npm install -g @innosage/draft-cli).
  Running `draft start-server` starts the local daemon in the background and can request a browser pairing tab, but agents must still verify readiness with `draft status`.
metadata:
  author: innosage-llc
  version: "1.1"
---

# Draft CLI Skill

Use the `draft` CLI to manage Draft pages directly from the command line. This allows you to work with Draft documents seamlessly without leaving your terminal workflow.

## Setup and Connection

Before running Draft CLI commands, you must ensure the Draft CLI package is globally installed:

```bash
npm install -g @innosage/draft-cli
```

### Operational Pattern: Always Check Connection First

To ensure a stable session, you MUST follow this sequence before executing any functional Draft command (like `ls`, `cat`, `create`, etc.):

1.  **Check Status**: Start with `draft status --json` unless the user explicitly wants human-readable output.
2.  **Handle Daemon Offline**: If status reports `DAEMON_OFFLINE`, run `draft start-server [url]`.
3.  **Handle Browser Missing**: If status reports `BROWSER_NOT_CONNECTED`, run `draft daemon [url]` to re-open or re-pair the browser tab.
4.  **Verify**: Run `draft status --json` again and only proceed once the state is `READY`.
5.  **Respect Environment URLs**: The optional `[url]` positional defaults to production (`https://draft.innosage.co/`). Only pass a staging or development URL when the user explicitly asks for that environment.
6.  **Reject the Wrong Origin**: If the user explicitly asks for staging or another environment, inspect `clients[].origin` from `draft status --json`. A `READY` session connected to the wrong origin is not good enough. Run `draft stop-server`, reconnect with the requested URL, then verify that `clients[].origin` matches before you continue.

```bash
# 1. Start with machine-readable status
draft status --json

# 2a. If the daemon is offline, start it
draft start-server

# 2b. If the daemon is running but the browser is missing, pair a tab
draft daemon

# 3. Confirm the live path is ready
draft status --json
```

> [!IMPORTANT]
> The Draft CLI uses one daemon and one active browser-backed session at a time. `draft start-server` starts the daemon, but it does not by itself prove that the browser paired successfully. Always trust `draft status` over startup copy before issuing read/write commands.

### Agent-Friendly Structured Output

When the task is being executed by an agent or automation, prefer machine-readable output for operational commands and mutations:

```bash
draft status --json
draft ls --json
draft create "My New Page Title" --json
draft append <id> "More content" --json
draft replace <id> --heading "Status" --json
draft patch <id> --json
draft publish <id> --json
```

Use `draft cat <id>` when you want the page content in plain markdown for human review. Use `draft cat <id> --format json` only when you need the raw structured document data for parsing or automation. Use `draft cat <id> --json` when you want a small structured envelope with page metadata plus content.

Prefer the JSON workflow for branching and retries:

- Use `state`, `server_running`, `browser_connected`, and `read_write_ready` from `draft status --json` to decide what to do next.
- Use JSON mutation responses to capture created page IDs and publish URLs without scraping terminal prose.
- Keep human-readable commands for manual inspection or when the user explicitly wants prose output.

### Troubleshooting

Treat `draft status` as the authoritative diagnosis step before retrying a failed command.

- `DAEMON_OFFLINE`: the local daemon is not running.
  Run `draft start-server`, then re-run `draft status`.
- `BROWSER_NOT_CONNECTED`: the daemon is running, but no Draft browser tab is paired.
  Run `draft daemon`, then re-run `draft status`.
- `REQUEST_TIMEOUT`: the connected browser session did not respond in time.
  Run `draft status` to confirm the session is still connected before retrying.
- `PAGE_NOT_FOUND`: the provided page ID does not exist in the connected workspace.
  Run `draft ls --json` to confirm the correct page ID.

Preferred recovery sequence:

- If `draft status` says `DAEMON_OFFLINE`, run `draft start-server`, then re-check `draft status`.
- If `draft status` says `BROWSER_NOT_CONNECTED`, run `draft daemon` to re-open or re-pair the browser tab, then re-check `draft status`.
- If a live command returns `REQUEST_TIMEOUT`, do not retry blindly. Run `draft status` first.
- If the daemon looks stuck or the wrong tab is attached, run `draft stop-server`, then restart with `draft start-server`.
- If the user explicitly wants staging or another environment, reuse the same URL consistently for both `draft start-server [url]` and `draft daemon [url]`.
- If `draft status --json` shows `READY` but the connected `clients[].origin` does not match the requested environment, stop the server and reconnect to the requested URL before making changes.
- In CI or headless sessions, browser auto-launch may be skipped. Treat that as a diagnosis cue, then pair from a desktop session and verify with `draft status --json`.

### What Humans Should See

When the browser tab is connected to the Draft CLI daemon, the GUI shows a small `CLI Connected` badge in the sidebar header while the local-mode session is active.

## Command Reference

The Draft CLI uses conventional command structures.

### Listing and Reading

To see all available pages in the user's Draft workspace:

```bash
# Requires active connection
draft ls
```
Output includes the page `id`, `title`, and `parentId`. You need the `id` to read or modify a page.

To read the content of a specific page:

```bash
# Returns the page in rich Markdown format (default)
draft cat <id>

# Other available formats if you need raw data:
draft cat <id>
draft cat <id> --format raw
```

### Creating, Modifying, and Publishing

To create a brand new page:

```bash
draft create "My New Page Title"
```

To publish a page to the web:

```bash
# This will make the page publicly accessible via a unique URL.
# NOTE: For free beta testing, you MUST set the environment variable
# GLOBAL_PUBLISH_PASSWORD=innosage before running this command.
# This requirement is subject to change in the future.
GLOBAL_PUBLISH_PASSWORD=innosage draft publish <id>
```

To append content to the END of a page. You can pass the content as a string, but for multiline Markdown, it is usually safer and much more robust to pipe it via `stdin`:

```bash
# Simple append
draft append <id> "This is a new line at the bottom."

# Multiline append via stdin (RECOMMENDED)
cat << 'EOF' | draft append <id>
## New Section
- Item 1
- Item 2
EOF
```

To replace the content underneath a specific heading (up until the next heading of the same or higher level). This is incredibly useful for updating specific sections like "Status" or "Action Items" without overwriting the whole document.

```bash
cat << 'EOF' | draft replace <id> --heading "Status"
This is the new status content. Everything previously under the 'Status' heading was replaced by this text.
EOF
```

To apply a precise unified diff to a page. This is best for surgical edits to existing paragraphs.

```bash
cat patch.diff | draft patch <id>
```

## Common Workflows

**1. The Edit Cycle (Read, Modify, Verify)**
Always follow the connection-first pattern, then read the page before modifying it.
```bash
# 1. Check/Start Connection
draft status --json
# (if needed: draft start-server && draft status --json)
# (if browser missing: draft daemon && draft status --json)

# 2. Read
draft ls --json
draft cat abc-123-def

# 3. Modify
cat << 'EOF' | draft append abc-123-def --json
New content...
EOF

# 4. Verify
draft cat abc-123-def
```

**2. Switching Tabs/Context**
The Draft daemon is intentionally single-session. If you need to connect to a different browser tab or recover from a stale pairing:
  1. Stop the running server with `draft stop-server`.
  2. Run `draft start-server` again to generate a new token and open a new locked tab.

**3. Using Staging or Another Environment**
Only do this when the user explicitly asks for a non-production Draft environment.

```bash
draft status --json
draft stop-server
draft start-server https://markdown-editor-staging.web.app/
draft status --json
draft daemon https://markdown-editor-staging.web.app/
draft status --json
```
