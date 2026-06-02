---
name: draft-cli
version: "1.8.0"
description: >
  Manage InnoSage Draft pages and hosted Secret Shares using the @innosage/draft-cli.
  Use this skill for `draft`, `draft page ...`, `draft secret ...`, and `draft auth ...`.
  Live page commands use the headless v2 daemon only. Browser-backed relay, `draft daemon`,
  runtime v1, CLI workspace mode, and `draft public-comments ...` are removed.
  Do not use this skill when "draft" is only a verb or when the task is a generic local-file
  writing task unrelated to Draft CLI.
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
      - name: "GLOBAL_INVITE_CODE"
        required: false
        description: "The invite code used to publish Draft pages safely. Defaults to `innosage` during the free beta publish flow."
---

# Draft CLI Skill

Use `draft` for headless page-domain Draft operations and hosted Secret Share helpers.

## Current Runtime Contract

- `draft start-server` starts the only supported live-page runtime: headless v2.
- `draft status --json` is the readiness check for page commands.
- `READY` means the headless daemon is running and page read/write commands can proceed.
- Removed commands and modes must not be used: `draft daemon`, `--runtime v1`, `--runtime v1_DEPRECATED`, `--mode workspace`, `draft open <path>`, `draft workspace ...`, and `draft public-comments ...`.

## Connection Pattern For Page Commands

For page commands such as `draft page ls`, `draft page cat`, `draft page create`,
`draft page append`, `draft page replace`, `draft page patch`, `draft page annotate`, and
`draft page publish`:

```bash
draft status --json
draft start-server
draft status --json
```

If the first status is already `READY`, proceed directly. If it reports `DAEMON_OFFLINE`, run
`draft start-server`, then re-check status. Do not try to pair a browser.

## Page Commands

Prefer explicit `draft page ...` commands:

```bash
draft page ls --json
draft page cat <page_id> --json
draft page create "Title" --json
draft page append <page_id> "More content" --json
draft page replace <page_id> --heading "Status" "Updated body" --json
draft page patch <page_id> --json < change.diff
draft page annotate <page_id> --anchor "exact text" --note "Reviewer note" --json
draft page comments <page_id> --json
draft page comment <comment_id> <page_id> --json
draft page publish <page_id> --json
```

Use `draft page cat <id>` when you want the page content in plain markdown for human review.
Use `draft page cat <id> --format json` only when you need raw structured document data for parsing or automation.

Top-level page aliases can still exist during compatibility windows, but agents should use the
`draft page ...` namespace.

## Write And Share Guardrail

Read-only behavior is the safe fallback. Do not run write/share commands unless the user explicitly
asks for the exact action and target.

- write commands: `draft page create`, `draft page append`, `draft page replace`, `draft page patch`, `draft page annotate`
- share commands: `draft page publish`, `draft secret create`

Before returning a public or shareable URL, review the command output and confirm it is the requested
artifact.

## Secret Share

Secret Share commands are hosted/local-crypto helpers and do not require `draft status` or
`draft start-server`.

Configure the API key:

```bash
draft auth set-key <secret-share-api-key>
draft auth status --json
```

Create a Secret Share:

```bash
draft secret create --file docs/brief.md --expires 1h --json
```

Read a Secret Share:

```bash
draft secret open '<secret_url_or_id>' --password "$DRAFT_SECRET_PASSWORD" --json
```

Use `--password` for password-protected shares. Use `DRAFT_SECRET_PASSWORD` only when the runtime
already provides it.

## Error Handling

- `DAEMON_OFFLINE`: run `draft start-server`, then `draft status --json`.
- `PAGE_NOT_FOUND`: run `draft page ls --json` and retry with a valid page ID.
- `PATCH_MISMATCH`: reread with `draft page cat <page_id>`, regenerate the patch, and retry.
- Missing Secret Share API key: use `draft auth set-key`, `--api-key`, or `DRAFT_SECRET_SHARE_API_KEY`.

Do not recover any error with `draft daemon` or a browser pairing step.
