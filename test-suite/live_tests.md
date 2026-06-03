# Draft CLI Live Tests

This document now covers the current headless-only Draft CLI contract.

Removed from the live suite:
- `draft daemon`
- runtime v1 / `v1_DEPRECATED`
- `draft open`
- `draft workspace ...`
- `draft public-comments ...`

Use the shipped evals and local gate as the authoritative regression surface:
- [`../evals/evals.json`](../evals/evals.json)
- [`../evals/smoke_phase2.json`](../evals/smoke_phase2.json)
- [`../evals/regression_phase3.json`](../evals/regression_phase3.json)
- [`../scripts/gate`](../scripts/gate)

Minimal live checks for the current CLI:
1. `draft status --json`
2. `draft start-server`
3. `draft status --json`
4. `draft page ls --json`
5. `draft page create "Live Test" --json`
6. `draft page append <page_id> --json`
7. `draft page cat <page_id> --json`
8. `draft page annotate <page_id> --anchor <text> --note <note> --json`
9. `draft page comments <page_id> --json`
10. `draft stop-server`

Secret Share checks remain hosted:
1. `draft auth status --json`
2. `draft secret create --file <path> --expires 1h --json`
3. `draft secret open <secret_url_or_id> --password <password> --json`
