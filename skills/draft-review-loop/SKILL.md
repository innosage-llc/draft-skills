---
name: draft-review-loop
version: "1.0.1"
description: >
  Retired workflow for the former CLI workspace review loop. Do not use for new work.
metadata:
  clawdis:
    author: innosage-llc
    dependencies:
      - name: "toliuweijing/draft-cli"
        type: "other"
        url: "https://clawhub.ai/toliuweijing/draft-cli"
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

# Draft Review Loop

This workflow is retired.

For local markdown authoring, edit the local file directly with normal repository tools. For Draft
page operations, use `draft-cli` and the headless `draft page ...` command surface.
