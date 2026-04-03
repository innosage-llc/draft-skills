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
  Running `draft start-server` will start the local server, launch the Draft PWA, and securely lock the connection.
metadata:
  author: innosage-llc
  version: "1.0"
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

1.  **Check Status**: Always start by running `draft status`.
2.  **Handle Disconnection**: If `draft status` reports that the server is not running or the browser is not connected, you MUST attempt to connect.
3.  **Start Server**: Run `draft start-server [url]`.
    *   The `[url]` parameter is optional and defaults to the production environment (https://draft.innosage.co). 
    *   Only specify a `[url]` if the user explicitly instructs you to use a specific staging or development environment.
4.  **Verify**: After starting the server, run `draft status` again to confirm the "Locked Connection" is established.

```bash
# 1. ALWAYS start with status
draft status

# 2. If the server is not running or the browser is not connected, start the server
draft start-server

# 3. Confirm connection is stable
draft status
```

> [!IMPORTANT]
> The Draft CLI operates by establishing a 1:1 secure "Locked Connection" with a single Draft PWA tab. Starting the background server will automatically launch a securely trusted tab. If you encounter a connection error later in the session, repeat this status-check-and-server-start sequence.

### Agent-Friendly Structured Output

When the task is being executed by an agent or automation, prefer machine-readable output for operational commands:

```bash
draft status --json
draft ls --json
draft create "My New Page Title" --json
draft append <id> "More content" --json
draft replace <id> --heading "Status" --json
draft patch <id> --json
draft publish <id> --json
```

Use `draft cat <id> --format json` when you want the lean raw document content only. Use `draft cat <id> --json` when you want a small structured envelope with page metadata plus content.

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
draft cat <id> --format json
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
ALWAYS follow the "Connection First" pattern, then read the page before modifying it.
```bash
# 1. Check/Start Connection
draft status --json
# (if needed: draft start-server && draft status --json)

# 2. Read
draft ls --json
draft cat abc-123-def --format json

# 3. Modify
cat << 'EOF' | draft append abc-123-def --json
New content...
EOF

# 4. Verify
draft cat abc-123-def --format json
```

**2. Switching Tabs/Context (Locked Connection)**
The Draft daemon secures a strict 1:1 lock with the tab it opened. Multi-tab conflicts are eliminated because second tabs cannot connect to a locked daemon.
If you need to connect to a new document session:
  1. Stop the running server with `draft stop-server`.
  2. Run `draft start-server` again to generate a new token and open a new locked tab.
