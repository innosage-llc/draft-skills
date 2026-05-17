---
name: draft-cli
version: "1.7.0"
description: >
  Manage Draft CLI authentication, status checks, and read-only Draft inspection using @innosage/draft-cli.
  Use this skill when the user asks about Draft CLI auth, `draft auth set-key`, `draft auth status`, reading Draft pages, opening Secret Share links, reading public comments, checking daemon status, or asks about Draft CLI command usage.
  Do not use this skill when "draft" is only a verb or when the request is unrelated to the actual InnoSage Draft CLI.
metadata:
  clawdis:
    emoji: "📝"
    requires:
      bins:
        - "draft"
    install:
      - id: "npm"
        kind: "node"
        package: "@innosage/draft-cli"
        bins:
          - "draft"
        label: "Install draft-cli (npm)"
    envVars:
      - name: "DRAFT_SECRET_SHARE_API_KEY"
        required: false
        description: "Optional Secret Share API key for hosted Secret Share workflows. Prefer environment variables for automation."
---

# Draft CLI Skill

Use the `draft` CLI for authentication setup, connection diagnosis, and read-only Draft inspection.

This skill intentionally documents read and configuration workflows. If the user asks for content mutation, page publishing, annotation creation, workspace writes, or Secret Share creation, stop and ask for explicit confirmation of the exact command, target, and expected output before proceeding outside this read/configuration workflow.

## Safety and Permissions

| Scope | Capability | Rationale |
| :--- | :--- | :--- |
| **Network** | `https://draft.innosage.co` | Required for Draft page and app-origin workflows. |
| **Network** | `https://api.draft.innosage.co` | Required for hosted Secret Share records and public comments. |
| **Processes** | `draft` binary | Used to run local CLI commands. |

## Draft CLI Auth

Use this workflow when the user asks to configure, verify, or inspect Draft CLI auth for Secret Share workflows.

The current auth interface is:

```bash
draft auth set-key "<secret-share-api-key>"
draft auth status
draft auth status --json
```

Rules for agents:

- Do not run `draft status`, `draft start-server`, or `draft daemon` before `draft auth ...`; auth commands are local configuration commands.
- Prefer `draft auth status --json` when automation needs machine-readable output.
- Do not print or repeat the API key after configuration.
- If the user provides an API key in chat, pass it directly to `draft auth set-key` and avoid storing it in logs or session notes.
- For CI or one-off automation, prefer `DRAFT_SECRET_SHARE_API_KEY` over stored credentials.

Credential precedence for Secret Share workflows:

- explicit command flag, when a command supports one
- `DRAFT_SECRET_SHARE_API_KEY`
- compatibility fallback `DRAFT_API_KEY`
- key stored by `draft auth set-key`

## Connection-First Pattern For Live Page Reads

Use this sequence before live page read commands:

```bash
draft status --json
draft start-server
draft status --json
```

If status reports `BROWSER_NOT_CONNECTED` in a browser-backed workflow, run:

```bash
draft daemon
draft status --json
```

Proceed with live page reads only after `draft status --json` reports `READY`.

Use production by default. Only pass a staging or development `--app <url>` when the user explicitly asks for that environment.

## Read-Only Page Commands

List available Draft pages:

```bash
draft page ls --json
```

Read a page as Markdown:

```bash
draft page cat <page_id>
```

Read a page with a small JSON envelope:

```bash
draft page cat <page_id> --json
```

Read raw structured document data only when needed:

```bash
draft page cat <page_id> --format json
```

## Secret Share Reads

Secret Share links are hosted encrypted snapshots, not live Draft pages. A URL containing `/#/secret/<secret_id>` must be handled with `draft secret open`, not page commands or browser automation.

Use:

```bash
draft secret open '<secret_url_or_id>' --password '<reader_password>' --json
draft secret open '<secret_url_with_key>' --json
draft secret open <secret_id> --key <fragment_key> --json
```

Rules:

- Do not run `draft status`, `draft start-server`, or `draft daemon` before `draft secret open`.
- Use the reader password only for local decrypt.
- Prefer `--json` when automation needs metadata and Markdown.
- If `draft secret open` is unavailable, check `draft --version` and update `@innosage/draft-cli` before falling back to browser automation.

## Public Comment Reads

Public comments are hosted sidecar records. They do not require daemon readiness.

```bash
draft public-comments list --url '<published_or_preview_url>' --json
draft public-comments list --page-id <page_id> --json
draft public-comments get <comment_id> --json
```

Use `--publish-version` only when you must pin an exact published snapshot.

## Troubleshooting

- `DAEMON_OFFLINE`: run `draft start-server`, then `draft status --json`.
- `BROWSER_NOT_CONNECTED`: run `draft daemon`, then `draft status --json`.
- `REQUEST_TIMEOUT`: run `draft status --json` before retrying.
- `PAGE_NOT_FOUND`: run `draft page ls --json` to confirm the page ID.
- Secret Share or public-comment failures are usually HTTP, credential, expiration, or decryption problems, not daemon readiness problems.
