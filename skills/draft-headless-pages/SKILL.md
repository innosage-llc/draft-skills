---
name: draft-headless-pages
version: "1.0.3"
description: >
  Retired compatibility alias for headless Draft page work. Use `draft-cli` instead.
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

# Draft Headless Pages

This skill is a retired alias. Use `draft-cli` for all `draft` and `draft page ...` work.
