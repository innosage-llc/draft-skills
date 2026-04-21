---
name: draft-headless-pages
version: "1.0.3"
description: >
  Retired compatibility alias for the former headless Draft page skill.
  Use `draft-cli` instead for all new `draft` and `draft page ...` work.
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

This skill is retired.

Use `draft-cli` for all new `draft` and `draft page ...` work. `draft-cli` is now the single source of truth for:

- headless `v2` page-domain operations
- `draft start-server` / `draft status --json` default startup and recovery
- `draft page ...` create/read/mutate/publish flows
- public comment retrieval
- the compatibility appendix for `v1_DEPRECATED`

## Migration Guidance

If you previously would have used `draft-headless-pages`, use `draft-cli` instead.

Examples:

```bash
draft start-server
draft status --json
draft page create "Title" --json
draft page publish <page_id> --json
draft public-comments list --page-id <page_id> --json
```

## Trigger Rule

- Do not trigger this skill for new work.
- Only acknowledge it when a user explicitly references `draft-headless-pages` by name and needs migration guidance.
- Redirect the user to `draft-cli`.
