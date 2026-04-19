---
name: draft-headless-pages
description: >
  Operate Draft page-domain content through the headless CLI v2 runtime.
  Use this skill when the user wants remote, Linux, Docker, CI, or unattended automation against Draft pages without assuming a browser-backed live session.
  Keep this skill scoped to page-domain workflows under `draft ... --runtime v2`; do not use it for workspace/file-backed markdown loops or browser-paired collaboration.
  Prefer publish-for-review when a human needs to inspect or comment on headless output.
metadata:
  clawdis:
    emoji: "headless"
    requires:
      bins:
        - "draft"
      env:
        - "GLOBAL_INVITE_CODE"
    install:
      - id: "npm"
        kind: "node"
        package: "@innosage/draft-cli"
        bins:
          - "draft"
        label: "Install draft-cli (npm)"
    envVars:
      - name: "GLOBAL_INVITE_CODE"
        required: true
        description: "Invite code used when publishing a Draft page for review."
---

# Draft Headless Pages Skill

Use this skill for isolated Draft page automation in CLI `v2`.

## Trigger Guidance

Trigger this skill when the request is about:

- headless Draft page creation or mutation from Linux, Docker, CI, or a remote agent
- page-domain automation that should not depend on a paired browser tab
- review handoff by publishing a headless page for a human to inspect
- commands such as `draft start-server --runtime v2`, `draft page create`, `draft page patch`, or `draft page publish`

Do not trigger this skill when:

- the task is workspace/file-backed markdown authoring or review
- the user wants live browser collaboration or a browser-paired session
- the request is a generic Draft CLI question that is not specifically about headless page-domain usage

## Boundaries

- Runtime plane: CLI `v2` only.
- Storage plane: page-domain content only.
- Human review surface: published or preview page URL.
- Not in scope: `workspace` mode, local file bindings, or browser-paired `v1` collaboration.

If the user needs repo-backed markdown review with durable comments, use `draft-review-loop` and workspace commands instead.

## Startup and Verification

Always make the runtime explicit.

```bash
draft start-server --runtime v2
draft status --json
```

Proceed only when `draft status --json` shows a healthy headless session for `v2`.

Operational rules:

1. Start the daemon with `--runtime v2` before page commands.
2. Check `draft status --json` before mutating content.
3. Treat status JSON as the source of truth for daemon health and selected runtime.
4. Do not describe this flow as browser-paired or live collaborative.

## Safe Command Set

Prefer these commands for headless page workflows:

```bash
draft page create "Title" --json
draft page cat <page_id>
draft page append <page_id> "content" --json
draft page replace <page_id> --heading "Section" --content "replacement" --json
draft page patch <page_id> --json
draft page annotate <page_id> --anchor "text" --note "feedback" --json
draft page comments <page_id> --json
draft page publish <page_id> --json
```

Usage guidance:

- Use `--json` for control flow, IDs, URLs, and retry logic.
- Use `draft page cat <page_id>` when the goal is human-readable markdown inspection.
- Use `draft page comments <page_id> --json` to read page annotations without scraping full page content again.
- Use `draft page annotate` only when the workflow explicitly needs page-bound feedback markers.

## Default Workflow

Use this compact sequence unless the user asks for a different handoff:

1. Start headless runtime: `draft start-server --runtime v2`
2. Verify health: `draft status --json`
3. Create or locate the target page.
4. Apply page mutations with `append`, `replace`, or `patch`.
5. Read back with `draft page cat <page_id>` or comments commands as needed.
6. Publish for human review when feedback is needed.

## Review Handoff Pattern

Publish-for-review is the default handoff path for this skill because it works without assuming shared browser state.

```bash
draft page publish <page_id> --json
```

Use handoff language like:

- "The headless Draft page is ready for review at `<url>`."
- "Please review the published page and send revision requests back here."
- "If you need durable file-linked review instead, we should switch to the workspace review loop."

Feedback model:

- Human reviews the published or preview URL.
- Human sends revision instructions back through chat or tasking.
- Agent applies a new headless page pass and republishes if needed.

Do not claim that `v2` is a live shared browser editing session.

## Failure Handling

Use these guardrails before retrying:

- If the daemon is offline, rerun `draft start-server --runtime v2`, then `draft status --json`.
- If status does not report `v2`, stop and fix runtime selection before writing.
- If a command fails with a missing page ID or lookup error, rediscover the target page before mutating it.
- If review requires file-path identity, Git diffs, or durable workspace comments, stop using this skill and switch to workspace mode.
- If a requested action depends on browser-only behavior, do not improvise; state that the task belongs to `v1` or GUI workflows instead.

## Non-Goals

- Do not mix `v2` page mode with `workspace` mode.
- Do not position `v2` as browser-backed live collaboration.
- Do not assume a desktop browser is available.
