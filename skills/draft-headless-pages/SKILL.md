---
name: draft-headless-pages
description: >
  Operate Draft page-domain content through the headless CLI v2 runtime.
  Use this skill when the user wants remote, Linux, Docker, CI, or unattended automation against Draft pages.
  Keep this skill scoped to page-domain workflows under `draft ... --runtime v2`; do not use it for workspace/file-backed markdown loops.
  Prefer publish-for-review when a human needs to inspect or comment on headless output.
metadata:
  clawdis:
    emoji: "📝"
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
        description: "The invite code required to publish Draft pages safely. It can be used for free during the beta test."
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
- the request is a generic Draft CLI question that is not specifically about headless page-domain usage

## Boundaries

- Runtime plane: CLI `v2` only.
- Storage plane: page-domain content only.
- Human review surface: published or preview page URL.
- Not in scope: `workspace` mode or local file bindings.

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
4. Treat publish-and-review as the standard human feedback path.

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
- Human leaves comments on the public page or sends revision instructions back through chat or tasking.
- Agent applies a new headless page pass and republishes if needed.

## Public Comment Retrieval

Public-page comments are part of the standard publish-and-review loop for this skill.

For these commands:

- Do not start with `draft status`.
- Do not require `draft start-server`.
- Do not add extra runtime setup.

Preferred procedure:

1. Capture the publish or preview URL from `draft page publish <page_id> --json`.
2. List public comments for the review artifact:

```bash
draft public-comments list --url '<published_or_preview_url>' --json
```

3. If only the page ID is known, resolve comments by page ID instead:

```bash
draft public-comments list --page-id <page_id> --json
```

4. For any comment that needs exact context, fetch the single comment record:

```bash
draft public-comments get <comment_id> --json
```

Agent rules:

- Use `list` for discovery and triage.
- Use `get` when you need the full body, quote, offsets, or bounded context before editing.
- Re-check comments after republishing if the review loop spans multiple iterations.
- Use public comments as the default review signal after `draft page publish`.

## Failure Handling

Use these guardrails before retrying:

- If the daemon is offline, rerun `draft start-server --runtime v2`, then `draft status --json`.
- If status does not report `v2`, stop and fix runtime selection before writing.
- If a command fails with a missing page ID or lookup error, rediscover the target page before mutating it.
- If public comment retrieval fails, verify that you are using the published or preview URL path, or retry with `--page-id <page_id>` when only page identity is known.
- If review requires file-path identity, Git diffs, or durable workspace comments, stop using this skill and switch to workspace mode.

## Non-Goals

- Do not mix `v2` page mode with `workspace` mode.
- Do not assume a desktop browser is available.
