---
name: draft-review-loop
description: >
  Run the local-first authoring plus Draft review handoff loop for workspace markdown files.
  Use this skill when the user asks to write or revise a document and explicitly wants human review in Draft,
  or when the task is to apply Draft comments back to a local file.
  DO NOT use this skill for pure Draft command questions (use draft-cli) or generic writing tasks with no Draft review intent.
  Keep local workspace markdown as source of truth and use Draft GUI as the human review surface.
compatibility: >
  Requires the draft-cli skill and @innosage/draft-cli (Node.js >= 18).
metadata:
  author: innosage-llc
  version: "1.0"
---

# Draft Review Loop Skill

Use this skill to run a human-agent review loop where authorship stays in local markdown and Draft is the review surface.

## Trigger Guidance

Trigger this skill when the user intent matches collaboration workflow requests such as:

- "Write a doc and let me review it in Draft."
- "Prepare a proposal for review in Draft."
- "Revise this workspace file based on Draft comments."
- "Use Draft as the review surface while keeping the repo file as source of truth."

Do not trigger this skill when:

- the user only asks how to run Draft commands (`draft status`, `draft ls`, `draft patch`, etc.)
- the user uses "draft" only as a verb for generic writing (for example, "draft an email")
- the user requests direct Draft-page mutation as the primary authoring surface

## Boundaries

- Source of truth: local workspace markdown file.
- Review surface: Draft GUI page opened from that file.
- Transport and command handling: `draft-cli` skill.
- This skill defines workflow behavior, not low-level CLI troubleshooting.

## Required Workflow

Follow this sequence unless the user explicitly asks for a different flow.

1. Create or update the local markdown file first.
2. Ensure Draft connection through `draft-cli` connection-first pattern (`draft status --json` and recovery if needed).
3. Open the local file in Draft review surface:

```bash
draft open <path> --json
```

4. Explicitly hand off to human review in Draft.
5. Read review artifacts from Draft comments:

```bash
draft comments list <path> --json
```

6. Apply accepted feedback back to the local markdown file with normal file-editing tools.

## Human Handoff Language

Use direct handoff language after `draft open <path> --json`, for example:

- "I updated `<path>` locally and opened it in Draft for your review."
- "Please leave comments in Draft; I will apply accepted feedback back to the local file."

## Revision Application Rule

When comments arrive, edit the local file by default. Do not default to mutating Draft page content directly unless the user explicitly requests page-first mutation.

## Non-Goals

- Do not imply fully headless live collaboration.
- Do not move source of truth from workspace markdown to Draft pages.
