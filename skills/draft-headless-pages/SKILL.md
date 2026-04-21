---
name: draft-headless-pages
version: "1.0.3"
description: >
  Headless Draft page automation for remote agents, Docker, CI, and Linux environments.
  Use this as the default Draft skill for OpenClaw-style isolated runtimes where the agent does not share a browser session with the user.
  Keep this skill scoped to page-domain workflows under `draft ... --runtime v2`; do not use it for workspace/file-backed markdown loops or browser-backed v1 flows.
  Prefer publish-for-review when a human needs to inspect or comment on headless output.
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
        description: "Defaults to `innosage` for the current free beta publish flow."
---

# Draft Headless Pages Skill

Use this skill for isolated Draft page automation in CLI `v2`.

For OpenClaw and other remote-agent environments, this should be the default Draft runtime skill.

## Use This Skill When

- the agent is running remotely, in Docker, in CI, or on a Linux worker
- the agent should create, edit, publish, or review Draft pages without a paired browser tab
- the user wants a published page URL as the review surface

## Do Not Use This Skill When

- the workflow depends on local workspace markdown files as source of truth
- the agent is expected to operate through a browser-backed v1 Draft session
- the user is asking for a human approval workflow rather than raw page automation

## Trigger Guidance

Trigger this skill when the request is about:

- headless Draft page creation or mutation from Linux, Docker, CI, or a remote agent
- page-domain automation that should not depend on a paired browser tab
- review handoff by publishing a headless page for a human to inspect
- commands such as `draft start-server --runtime v2`, `draft page create`, `draft page patch`, or `draft page publish`

Do not trigger this skill when:

- the task is workspace/file-backed markdown authoring or review
- the request is a generic Draft CLI question that is not specifically about headless page-domain usage
- the primary need is gated human oversight; use `draft-agent-loop` on top of this runtime instead

## Boundaries

- Runtime plane: CLI `v2` only.
- Storage plane: page-domain content only.
- Human review surface: published or preview page URL.
- Not in scope: `workspace` mode or local file bindings.
- Not in scope: browser-backed v1 session management.

If the user needs repo-backed markdown review with durable comments, use `draft-review-loop` and workspace commands instead.
If the user needs approval checkpoints and execution sign-off, use `draft-agent-loop`, which should depend on this skill.

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
draft page insert-image <page_id> /path/to/local/image.png --json
draft page update-image <page_id> <local_id> --align center --width 500 --json
draft page delete-image <page_id> <local_id> --json
draft page annotate <page_id> --anchor "text" --note "feedback" --json
draft page comments <page_id> --json
draft page publish <page_id> --json
```

Usage guidance:

- Use `--json` for control flow, IDs, URLs, and retry logic.
- Use `draft page cat <page_id>` when the goal is human-readable markdown inspection.
- Save the `local_id` returned by `draft page insert-image`; it is required for later `update-image` or `delete-image` calls.
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

## Image Insertion and Management

Image commands are regular page mutations in headless `v2`, so they follow the normal startup contract for this skill:

1. Run `draft start-server --runtime v2`
2. Confirm `draft status --json`
3. Use local file paths for image uploads
4. Save the returned `local_id` for follow-up operations

Preferred commands:

```bash
draft page insert-image <page_id> /path/to/local/image.png --json
draft page insert-image <page_id> /path/to/local/image.jpg --align center --width 500 --json
draft page update-image <page_id> <local_id> --align right --json
draft page update-image <page_id> <local_id> --width 500 --json
draft page delete-image <page_id> <local_id> --json
```

Agent rules:

- Use `insert-image` only after the page exists and the headless runtime is healthy.
- Treat the returned `local_id` as required state for later image updates or deletion.
- Re-read the page with `draft page cat <page_id>` after image mutations when the user needs markdown-visible confirmation of surrounding content.
- Keep image handling in page mode; do not switch to workspace mode just to upload media.

## Review Handoff Pattern

Publish-for-review is the default handoff path for this skill because it works without assuming shared browser state.

```bash
# Free beta invite code examples:
draft page publish <page_id> --invite-code "${GLOBAL_INVITE_CODE:-innosage}" --json
```

If `GLOBAL_INVITE_CODE` is already set in the environment, a plain publish command also works:

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
