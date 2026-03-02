---
name: draft-cli
description: >
  Interact with Draft pages using the Draft CLI to list, read, create,
  and edit documents. Supports appending content, replacing sections by
  heading, and applying unified diffs. Use when the user asks to manage
  Draft content from the command line or integrate Draft with development
  workflows. Also use when the user mentions Draft pages, document editing,
  content management, or wants a CLI-based writing workflow.
compatibility: >
  Requires Node.js >= 18 and @innosage/draft-cli (npm install -g @innosage/draft-cli).
  The Draft PWA (draft.innosage.co) must be open in a browser for the daemon to connect.
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

The Draft CLI operates by connecting to an active tab of the Draft PWA running in the user's browser. To start this connection, you MUST start the daemon first:

```bash
# Starts the background localhost:1414 daemon and listens for connections
draft daemon
```

> [!IMPORTANT]
> If a command fails with `ECONNREFUSED` or "PWA is not connected", instruct the user to run `draft daemon` and open `https://draft.innosage.co` in their browser.

To verify the connection is active and stable, use:

```bash
draft status
```

## Command Reference

The Draft CLI uses conventional command structures.

### Listing and Reading

To see all available pages in the user's Draft workspace:

```bash
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

### Creating and Modifying

To create a brand new page:

```bash
draft create "My New Page Title"
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
ALWAYS read the page first before modifying it so you know exactly what is there.
```bash
# 1. Read
draft cat abc-123-def

# 2. Modify
cat << 'EOF' | draft append abc-123-def
New content...
EOF

# 3. Verify
draft cat abc-123-def
```

**2. Multi-tab conflicts**
If the user has multiple Draft tabs open, the daemon won't know which one to send commands to and your commands will fail with "Error: Multiple Draft PWA tabs are connected". To resolve this:
  1. Run `draft status` to see the list of active PWA connection IDs.
  2. Pick *any* of the active tab IDs.
  3. Append the `--client <tab-id>` global flag to **all** your subsequent commands to target that specific tab.
```bash
draft ls --client <tab-id>
draft cat <page-id> --client <tab-id>
```
