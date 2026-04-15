---
name: draft-cli
description: >
  Manage and interact with "Draft" pages and documents using the @innosage/draft-cli.
  Use this skill whenever the user explicitly asks to read, create, list, patch, or append content to a "Draft page", "Draft doc", or their "Draft workspace" (e.g., "my draft page named 'Founder Sync'", "all the pages I have in my draft workspace", "Draft CLI").
  This connects to the Draft PWA (draft.innosage.co) via a local daemon to read or modify living documents.
  DO NOT use this skill for generalized writing tasks where "draft" is used as a verb (e.g., "draft an email", "draft a response") or when referring to local markdown/text files with "draft" in the name (e.g., "draft.md", "investor_update_draft.md"). Only use when interacting with the actual InnoSage Draft web application or Draft CLI tool.
  When triggered, ALWAYS follow the "Connection First" operational pattern: check status before any other command, and start the background server if it is not running.
metadata: {"clawdbot":{"emoji":"📝","requires":{"bins":["draft"]},"install":[{"id":"npm","kind":"node","package":"@innosage/draft-cli","bins":["draft"],"label":"Install draft-cli (npm)"}]}}
---

# Draft CLI Skill

Use the `draft` CLI to run Draft transport and operational commands from the terminal.

## Safety and Permissions

This skill requires specific permissions to interact with the Draft PWA and your local filesystem.

| Scope | Capability | Rationale |
| :--- | :--- | :--- |
| **Network** | `https://draft.innosage.co` | Required for the daemon to communicate with the Draft PWA. |
| **Filesystem** | Local `.md` files | Only accessed in `workspace` mode for direct repo-backed editing. |
| **Processes** | `draft` binary | Used to manage the local daemon and execute operational commands. |

## Setup and Connection

Before running Draft CLI commands, ensure `draft` is available on your PATH (see Install panel).

### Operational Pattern: Always Check Connection First

To ensure a stable session, you MUST follow this sequence before executing any functional Draft command (like `ls`, `cat`, `create`, etc.):

1.  **Check Status**: Start with `draft status --json` unless the user explicitly wants human-readable output.
2.  **Handle Daemon Offline**: If status reports `DAEMON_OFFLINE`, run `draft start-server --mode local` (or `--mode workspace --workspace <root>` ONLY if you have a local file path and are co-located).
3.  **Handle Browser Missing**: If status reports `BROWSER_NOT_CONNECTED`, run `draft daemon [url]` (the currently implemented pairing/retarget command) to re-open or re-pair the browser tab.
4.  **Verify**: Run `draft status --json` again and only proceed once the state is `READY`.
5.  **Respect Environment URLs**: The `--app <url>` argument defaults to production (`https://draft.innosage.co/`). Only pass a staging or development URL when the user explicitly asks for that environment.
6.  **Reject the Wrong Origin**: If the user explicitly asks for staging or another environment, inspect `clients[].origin` from `draft status --json`. A `READY` session connected to the wrong origin is not good enough. Run `draft stop-server`, reconnect with the requested URL, then verify that `clients[].origin` matches before you continue.

```bash
# 1. Start with machine-readable status
draft status --json

# 2a. If the daemon is offline, start it. Choose mode based on environment:
# - REMOTE/OPENCLAW: always use --mode local
# - LOCAL/REPO: use --mode workspace --workspace $(pwd)
draft start-server --mode local

# 2b. If the daemon is running but the browser is missing, pair a tab
draft daemon

# 3. Confirm the live path is ready
draft status --json
```

> [!IMPORTANT]
> The Draft CLI uses one daemon and one active browser-backed session at a time. `draft start-server` starts the daemon, but it does not by itself prove that the browser paired successfully. Always trust `draft status` over startup copy before issuing read/write commands.
> For agent lifecycle control, prefer `draft start-server` and `draft stop-server`. Keep `draft daemon` as the active pairing/retarget command when status shows no browser or when you need to retarget the connected tab.

### Agent-Friendly Structured Output

When the task is being executed by an agent or automation, prefer machine-readable output for operational commands and mutations:

```bash
draft status --json
draft page ls --json
draft open path/to/file.md --json
draft page create "My New Page Title" --json
draft workspace comments path/to/file.md --json
draft page append <id> "More content" --json
draft page replace <id> --heading "Status" --json
draft page patch <id> --json
draft page publish <id> --json
```

Use `draft page cat <id>` when you want the page content in plain markdown for human review. Use `draft page cat <id> --format json` only when you need the raw structured document data for parsing or automation. Use `draft page cat <id> --json` when you want a small structured envelope with page metadata plus content.

Prefer the JSON workflow for branching and retries:

- Use `state`, `server_running`, `browser_connected`, and `read_write_ready` from `draft status --json` to decide what to do next.
- Use JSON mutation responses to capture created page IDs and publish URLs without scraping terminal prose.
- Keep human-readable commands for manual inspection or when the user explicitly wants prose output.

### Workspace-Backed Open

For **local co-located agents** working on repo-backed markdown, prefer the workspace-backed flow over manual page-ID discovery:

```bash
draft status --json
draft open path/to/file.md --json
```

Use `draft open <path> --json` as the canonical entrypoint for file-backed review work. It binds or reuses a durable document/page mapping, opens the Draft review surface for that file, and is the preferred `EDITOR_NOT_READY` recovery when the task starts from a local file path.

> [!TIP]
> **When to use workspace mode**: Only when the agent is co-located on the same machine as the user AND the task starts from a local `.md` file path. This unlocks `draft open <path>` for file-bound review tasks.

> [!CAUTION]
> **Remote/OpenClaw agents**: Do NOT use workspace mode. It requires a shared filesystem. In remote environments, workspace mode blocks `draft page publish` and may require user intervention to recover. Use `--mode local` instead.

In workspace mode, the local markdown file is the source of truth. The Draft page is the review surface, and persisted comment artifacts are the durable review/control layer.

### Troubleshooting

Treat `draft status` as the authoritative diagnosis step before retrying a failed command.

- `DAEMON_OFFLINE`: the local daemon is not running.
  Run `draft start-server --mode local`, then re-run `draft status`.
- `BROWSER_NOT_CONNECTED`: the daemon is running, but no Draft browser tab is paired.
  Run `draft daemon` (pairing/retarget), then re-run `draft status`.
- `REQUEST_TIMEOUT`: the connected browser session did not respond in time.
  Run `draft status` to confirm the session is still connected before retrying.
- `EDITOR_NOT_READY`: a browser tab is connected, but no writable editor is mounted.
  If the task starts from a local file path, run `draft open <path> --json`, then re-run `draft status --json`.
  If `draft open <path> --json` succeeds and `draft status --json` shows the connected `clients[].route` correctly retargeted to `/#/local?file=...` but the state is still `EDITOR_NOT_READY`, treat that as an app-side editor mount failure rather than a daemon pairing failure.
  In that case, inspect the browser UI for workspace render errors such as `Page Not Found`, confirm the app actually mounted a writable editor, and avoid looping `draft start-server` or `draft daemon` blindly.
  If you are in a legacy page-centric flow and already have a target page ID, mount a real page route in the connected tab (`https://draft.innosage.co/#/page/<id>`) and re-run `draft status --json`.
  If you do not have a page ID yet in a legacy flow, run `draft page ls --json` first, then mount the page route and re-run `draft status --json`.
- `PAGE_NOT_FOUND`: the provided page ID does not exist in the connected workspace.
  For example, running `draft page comments does-not-exist-9999 --json` will return a `PAGE_NOT_FOUND` error because the ID `does-not-exist-9999` was **not found** in the workspace.
  Run `draft page ls --json` to confirm the correct page ID.
- `UNBOUND_DOCUMENT`: the requested path or `document_id` is not currently bound in the active workspace.
  Run `draft open <path> --json`, then retry `draft workspace comments <path> --json`.
- Workspace-scope/input rejection: the requested path resolves outside the daemon's active workspace root.
  Re-run the command from the correct workspace root and use a path under that root. Do not assume `/tmp` or another directory is valid unless the daemon was started there.

Preferred recovery sequence:

- If `draft status` says `DAEMON_OFFLINE`, run `draft start-server --mode local`, then re-check `draft status`.
  (Use `--mode workspace --workspace <root>` only for co-located file-bound review tasks)
- If `draft status` says `BROWSER_NOT_CONNECTED`, run `draft daemon` to re-open or re-pair the browser tab, then re-check `draft status`.
- If a live command returns `REQUEST_TIMEOUT`, do not retry blindly. Run `draft status` first.
- If `draft status` or a mutation error indicates `EDITOR_NOT_READY` for a local file workflow, run `draft open <path> --json`, then re-run `draft status --json` before retrying reads or writes.
- If `draft open <path> --json` succeeded and `draft status --json` shows the expected `clients[].route` for that file but still reports `EDITOR_NOT_READY`, stop treating this as a daemon reconnection problem.
  Diagnose the app surface instead:
  confirm the GUI is on `/#/local?file=...`, check whether the page shows `Page Not Found` or another workspace load error, and restart the local app if the running build may be stale.
- If `draft status` or a mutation error indicates `EDITOR_NOT_READY` in a legacy page-centric flow, mount a real page route in the connected tab (`https://draft.innosage.co/#/page/<id>`), then re-run `draft status --json` before retrying writes.
  If needed, use `draft page ls --json` to discover the page ID before route-mounting.
- Do not treat `draft page create` as the primary `EDITOR_NOT_READY` fix. Recover editor readiness first, then run the intended command.
- If `draft workspace comments <path|document_id|page_id> --json` returns `UNBOUND_DOCUMENT`, bind the file first with `draft open <path> --json`.
- If a workspace command fails because the path is outside the active workspace root, correct the working directory or path before retrying.
- If the daemon looks stuck or the wrong tab is attached, run `draft stop-server`, then restart with `draft start-server --mode local`.
- If the user explicitly wants staging or another environment, reuse the same URL consistently for both `draft start-server --app [url]` and `draft daemon [url]`.
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
draft page ls
```
Output includes the page `id`, `title`, and `parentId`. You need the `id` to read or modify a page.

To read the content of a specific page:

```bash
# Returns the page in rich Markdown format (default)
draft page cat <id>

# Other available formats if you need raw data:
draft page cat <id>
draft page cat <id> --format raw
```

### Persisted Comment Artifacts

For workspace-backed files, prefer the persisted artifact read path:

```bash
draft workspace comments <path|document_id|page_id> --json
```

This is the preferred machine-readable read path for human comments on workspace-bound files. The JSON payload includes top-level metadata like `document_id`, `page_id`, `source_path`, and `comments[]`. Each comment record can include fields like `comment_id`, `body`, `status`, `author`, `created_at`, `anchor`, and `anchor_status`.

Use this flow when the user starts from a repo file path or a workspace-bound document and you want to read review feedback without switching your source of truth away from local markdown.

### Legacy Page Annotations

> [!NOTE]
> "Comments" in Draft are annotation highlights attached to text spans. The CLI exposes them as
> read-only records via two scoped commands. Use these commands to discover user feedback efficiently
> instead of rereading the entire page. This is the legacy page-centric path; keep using it when the task starts from a known `page_id` or an existing annotation workflow.

To list all comments (annotations) on a page in compact discovery mode:

```bash
draft page comments <page_id> --json
```

Output includes `comment_id`, `anchor_text` (the highlighted span), `note` (the comment body), and `position_hint` (character offset). Use this for quick triage — identify which comment IDs need deeper inspection.

To inspect a single comment with bounded context (±100 chars before/after the anchor):

```bash
draft page comment <comment_id> <page_id> --json
```

Output includes `note`, `anchor_text`, and a `bounded_context` object with `before` and `after` fields. Use `bounded_context.before + anchor_text + bounded_context.after` to locate the exact edit site before patching.

### Creating Annotations (Comments)

Use `draft workspace annotate` to create a new comment on a selected text span. In workspace mode, you can pass the workspace file path instead of the page ID.

```bash
# Basic annotation (Workspace mode - preferred)
draft workspace annotate path/to/file.md --anchor "scalable infrastructure" --note "Specify AWS or GCP" --json

# Basic annotation (Legacy local mode)
draft page annotate <page_id> --anchor "scalable infrastructure" --note "Specify AWS or GCP" --json
```

When the anchor text appears more than once, disambiguate with surrounding context so the CLI can target the correct occurrence.

```bash
# Disambiguate repeated anchors with nearby prefix/suffix context
draft workspace annotate path/to/file.md --anchor "status" --before "The current " --note "Needs update" --json
draft workspace annotate path/to/file.md --anchor "status" --after " is blocked" --note "Needs update" --json
```

Use `--before` and/or `--after` whenever the anchor is ambiguous or repeated in the same page.

### Creating, Modifying, and Publishing

To create a brand new page:

```bash
draft page create "My New Page Title"
```

To publish a page to the web:

```bash
# This will make the page publicly accessible via a unique URL.
# NOTE: For free beta testing, you MUST provide an invite code.
# You can use the --invite-code flag (RECOMMENDED):
draft page publish <id> --invite-code innosage

# OR set the environment variable:
# GLOBAL_INVITE_CODE=innosage draft page publish <id>
```

To append content to the END of a page. You can pass the content as a string, but for multiline Markdown, it is usually safer and much more robust to pipe it via `stdin`:

```bash
# Simple append
draft page append <id> "This is a new line at the bottom."

# Multiline append via stdin (RECOMMENDED)
cat << 'EOF' | draft page append <id>
## New Section
- Item 1
- Item 2
EOF
```

To replace the content underneath a specific heading (up until the next heading of the same or higher level). The matched heading itself is preserved, and only that section body is replaced. This is useful for updating specific sections like "Status" or "Action Items" without overwriting the whole document.

```bash
cat << 'EOF' | draft page replace <id> --heading "Status"
This is the new status content. The 'Status' heading is preserved, and everything previously under it is replaced by this text.
EOF
```

To apply a precise unified diff to a page. This is best for surgical edits to existing paragraphs.

```bash
cat patch.diff | draft page patch <id>
```

> [!CAUTION]
> **Always generate the diff from `draft page cat <id>` output — never from a locally authored file.**
>
> Draft's tiptap editor stores multi-line text blocks as a **single paragraph node**. When serialized by `draft page cat`, this appears as one continuous space-joined line, not multiple lines. If you generate a diff against a multi-line file you wrote yourself, the patch engine will return `PATCH_MISMATCH` even though `ok:true` was returned by a previous write.
>
> **Safe patch workflow:**
> ```bash
> # 1. Capture live content and strip the 4-line metadata envelope (Title:, ID:, ---, blank line)
> #    and the trailing --- delimiter. draft page cat wraps body content in this envelope.
> #    The patch engine operates on body-only content; including any envelope line causes PATCH_MISMATCH.
> draft page cat <id> | sed '1,4d' | sed '$d' > /tmp/before.md
>
> # 2. Copy and edit — do NOT reformat or reflow the body text.
> #    The live serialization is the ground truth. Even a single trailing newline
> #    difference between your edited file and the live before.md will cause a mismatch.
> cp /tmp/before.md /tmp/after.md
> # (make your text edits to /tmp/after.md using sed or similar)
>
> # 3. Generate diff from live content.
> #    IMPORTANT: `diff` exits with code 1 when files differ (not an error — that is expected).
> #    Use `;` (not `&&`) so the patch command always runs regardless of diff's exit code.
> diff -u /tmp/before.md /tmp/after.md > /tmp/patch.diff ; cat /tmp/patch.diff | draft page patch <id> --json
>
> # 4. Verify — wait 2-3 seconds after mutation before reading back.
> #    Draft CLI relays mutations to a live TipTap editor asynchronously. A read immediately
> #    after a write may return stale or empty content. Add a short sleep for reliable verification.
> sleep 2 && draft page cat <id>
> ```
>
> If you receive `PATCH_MISMATCH`, re-run `draft page cat <id> | sed '1,4d' | sed '$d'` and regenerate the diff — do not retry with the same diff file.

> [!NOTE]
> **Annotated pages:** `draft page cat` output for pages with comments includes inline markers like ` [:: User Note: A :] `. These markers cause `PATCH_MISMATCH` if left in your diff. Always add a marker-strip step when patching annotated pages:
> ```bash
> draft page cat <id> | sed '1,4d' | sed '$d' | sed 's/ \[:: User Note: [^:]* :\]//g' > /tmp/before.md
> ```

## Common Workflows

**1. The Edit Cycle (Read, Modify, Verify)**
Always follow the connection-first pattern, then read the page before modifying it.
```bash
# 1. Check/Start Connection
draft status --json
# (if needed: draft start-server && draft status --json)
# (if browser missing: draft daemon && draft status --json)

# 2. Read
draft page ls --json
draft page cat abc-123-def

# 3. Modify
cat << 'EOF' | draft page append abc-123-def --json
New content...
EOF

# 4. Verify
draft page cat abc-123-def
```

**2. The Safe Patch Cycle (Surgical Line Edit)**
Use `draft page patch` for precise edits to existing text. Always anchor the diff to the live markdown.
```bash
# 1. Check/Start Connection
draft status --json

# 2. Capture live content and strip the 4-line metadata envelope + trailing delimiter.
#    `draft page cat` wraps body content in: Title: / ID: / --- / (blank) ... (body) ... ---
#    The patch engine expects body-only content. Use sed '1,4d' | sed '$d' to strip.
draft page cat <id> | sed '1,4d' | sed '$d' > /tmp/before.md

# 3. Edit a copy — do NOT reformat or reflow the body.
#    The content from before.md is the only valid anchor.
cp /tmp/before.md /tmp/after.md
# (edit /tmp/after.md — sed, your editor, etc.)

# 4. Generate the diff from live content.
#    Use `;` not `&&` — diff exits 1 when files differ, which would silently
#    break `&&` chains before the patch command runs.
diff -u /tmp/before.md /tmp/after.md > /tmp/patch.diff ; cat /tmp/patch.diff | draft page patch <id> --json

# 5. Verify the change landed — wait 2-3 seconds first.
#    Mutations are relayed asynchronously to the TipTap editor. Reading immediately
#    after a write may return stale content. Always add a short sleep before verifying.
sleep 2 && draft page cat <id>

# If PATCH_MISMATCH: re-read with `draft page cat <id> | sed '1,4d' | sed '$d'` and regenerate — do NOT retry with the same diff
```

**3. The Comment Discovery Cycle (Review → Locate → Patch)**
Use `draft page comments` and `draft page comment` to efficiently action user annotations without rereading
entire pages.

```bash
# 1. Check connection
draft status --json

# 2. Discover all comments on a page (compact)
draft page comments <page_id> --json

# 3. Inspect the specific comment you intend to address (bounded context)
draft page comment <comment_id> <page_id> --json

# 4. Use anchor + bounded_context to generate a precise diff, then patch
# Note: We strip comment markers [:: User Note: ... :] to prevent PATCH_MISMATCH
draft page cat <page_id> | sed '1,4d' | sed '$d' | sed 's/ \[:: User Note: [^:]* :\]//g' > /tmp/before.md
# (edit /tmp/after.md with the fix informed by the bounded_context)
diff -u /tmp/before.md /tmp/after.md > /tmp/patch.diff ; cat /tmp/patch.diff | draft page patch <page_id> --json
```

**4. Switching Tabs/Context**
The Draft daemon is intentionally single-session. If you need to connect to a different browser tab or recover from a stale pairing:
  1. Stop the running server with `draft stop-server`.
  2. Run `draft start-server` again to generate a new token and open a new locked tab.

**5. Using Staging or Another Environment**
Only do this when the user explicitly asks for a non-production Draft environment.

```bash
draft status --json
draft stop-server
draft start-server --mode local --app https://markdown-editor-staging.web.app/
draft status --json
draft daemon https://markdown-editor-staging.web.app/
draft status --json
```

**6. Publishing a Page**

Always use `--mode local` when the primary goal is to publish a page. Workspace mode blocks reachability to the publish endpoint.

```bash
# 1. Stop any existing server to ensure a clean start in local mode
draft stop-server

# 2. Connect in local mode (safest for publish)
draft start-server --mode local
draft daemon
draft status --json # Verify READY state before proceeding

# 3. Find the page ID
draft page ls --json

# 4. Publish
draft page publish <id> --invite-code innosage --json
```
