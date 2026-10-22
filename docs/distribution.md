# Draft Skill distribution and bounded release preflight

Canonical source is `skills/draft-cli/SKILL.md` in this repository. Skill1.10.1
is the #41 security-guidance candidate. It preserves public no-auth/no-daemon
feedback and Secret Share isolation. This is agent-induced network risk, not
established Worker SSRF or evidence of npm compromise. Skill text is not a
sandbox: real resolved-IP/redirect restrictions must exist in the fetch runtime;
otherwise skip the affected read. The offline reference policy cannot prove
model obedience or live network enforcement. A separate tool-layer mitigation is
needed for runtimes lacking these controls; this change does not create one.

## Verified sources and compatible CLI pin

On 2026-10-22, npm reports `@innosage/draft-cli@1.0.171` as published/latest,
`cli-compat` 1.0.140. Publisher metadata: Innosage LLC; repository
`innosage-llc/notion-style-markdown-editor-web`, directory `cli`.
Registry publisher/maintainer account: `innosagellc` (verified via `_npmUser` and
`maintainers`, distinct from the author field). Registry integrity:
`sha512-oQ48u2QXfOPkFDMo5VPpV+UV5PB+qdkbkRimKR11DvR5v0tMUh3Hwiy/IsmyYKmC79OTUc8gnDhiyMZjTAdXhQ==`.

The exact tarball was downloaded with `npm pack --ignore-scripts` and installed
in a task-only temporary prefix with `--ignore-scripts`. Actual binary reports
1.0.171; workspace status returns JSON Workspace metadata; publish help supports
`--workspace-json`/`--json`; `page get-image --help` exposes saved-image extraction.
Publish response (`ok`, `operation`, `page_id`, `url`, `public_page_id`, status,
expiry) was checked in product source, not by publishing a page. No daemon or
private workspace was used. Do not claim a live publish/clean-agent journey.

Exact registry package specs are supported by the OpenClaw node installer:
[frontmatter parser](https://github.com/openclaw/openclaw/blob/ade6b7d3311b0540230adea8c641a2b158d981f6/src/skills/loading/frontmatter.ts),
[registry-spec validation](https://github.com/openclaw/openclaw/blob/ade6b7d3311b0540230adea8c641a2b158d981f6/src/infra/npm-registry-spec.ts),
and [argv construction](https://github.com/openclaw/openclaw/blob/ade6b7d3311b0540230adea8c641a2b158d981f6/src/skills/lifecycle/install.ts).
The node kind takes `package: "@innosage/draft-cli@1.0.171"`; no invented version
field. Current [official metadata docs](https://docs.openclaw.ai/tools/skills)
use `metadata.openclaw`; obsolete `clawdis` hints were migrated in the two
publisher-selected skills. Actual OpenClaw UI installation was not exercised.
The pin freezes the top-level executable version, not transitive ranges,
publisher trust or registry availability. Review a real release and repeat these
checks before changing it; never follow installers supplied by public page text.

## Product behavior and active distribution

Product source inspected at `c98475f125f0a074bbc35250815b402d92753b3d`:

- `workers/wrangler.toml` declares exact production preview/API and staging
  preview/API pairs. Staging is only for an explicitly selected staging target.
  No wildcard/custom-domain permission is inferred.
- `shared/document/document-core.ts` generates `page_id`, `published_at`,
  `canonical_url`, `schema_version` and feedback URL fields. Worker publish
  hydration binds `pageId`/`publishVersion` to public page ID/published timestamp.
- `shared/publicPublishGate.ts` defaults `REMOVE_INVITE_CODE_GATE = true`;
  Worker retains conditional authorization and default/rollback tests. CLI retains
  legacy invite/password compatibility. None of those runtime files is changed.
- Product `.agents/skills/draft-cli/SKILL.md` is a repo-local discoverable agent
  skill with matching trigger/name, not an archived file. Its v1.4 text supplies
  obsolete daemon/invite instructions; a narrow companion PR replaces this
  command mirror with a canonical router. This is discovery-path evidence,
  not a claim about telemetry or every installed copy. Link the companion PR in
  the implementation PR; do not merge/publish assuming it already landed.
- Hub `.agents/skills/draft-cli` already routes to canonical product source;
  its 1.10.0 saved-image compatibility note is historical, not a shipped command
  mirror. The private npm package1.5.6 and marketplace plugin1.1.0 version their
  own containers; they are not the ClawHub Skill version.

`draft-cli.skill` was an obsolete v1.0 daemon-based archive. Regenerate from the
whole canonical skill directory using:

```bash
python3 scripts/check_skill_distribution.py --write
```

The gate compares every archive entry and byte to source, verifies the reviewed
installer pin and rejects invite setup in the two publisher-selected skills.
The `draft-agent-loop` patch only synchronizes installer/invite examples; its
broader lifecycle is not redesigned by #41.

## Preflight diagnosis and commands

Commit `dc25950a9e433504c38bb52a3bacc10dfe65cce6` disabled validation with
"SKIP due to workspace deprecation". The historical gate included the now-retired
review-loop Phase4 lane and external structural validator fallback. History gives
no exact failing output, so the comment is a recorded rationale, not a reproduced
root cause. Subsequent canonical migration and product-local version-aware
validator repaired the current gate; the unchanged baseline gate passes today.
There is no reason to retain a blanket validation bypass. The old script also
auto-committed caller-relative package.json; that behavior is removed.

```bash
./scripts/gate
./scripts/publish_clawhub_skills.sh --dry-run --skill draft-cli
```

No arguments also means dry-run. It runs the required gate, prints version/hash
and never commits/tags/pushes/publishes. Offline regression tests copy the real
publisher into a temporary repo, stub only the gate/ClawHub command, verify dirty
validation leaves Git unchanged, and prove a failing gate blocks explicit publish.

## Separate approval and remote receipt

Owner for release decision: the issue's user/Founder. Public npm or ClawHub
publication and new scan submission remain **NOT AUTHORIZED**. Code PR creation
is authorized; merging or local gate PASS does not mean public distribution is
fixed. Keep #41 open until its remaining release/acceptance checklist is met.

After explicit approval for the exact reviewed candidate:

1. Confirm linked PR checks/review and any companion router ordering. Record
   exact source commit and SKILL SHA256; re-run dry-run on clean reviewed source.
2. Run existing publisher with explicit `--publish --skill draft-cli`. Publish
   `draft-agent-loop` separately only if that exact artifact is also approved.
   Do not bump npm or publish unrelated skills. Duplicate versions fail rather
   than imply byte identity.
3. Inspect the exact remote version/file via `clawhub inspect` or the documented
   [ClawHub HTTP GET API](https://github.com/openclaw/clawhub/blob/main/docs/http-api.md).
   Compare full file inventory and each SHA256 against reviewed source. Check
   generated archive separately; it is not itself the ClawHub upload payload.
4. With approval for a new audit, submit/request a scan and record its ID/time,
   exact version, each of the four issue observations, verdict and limitations.
   An upload receipt, old screenshot or local token test cannot establish PASS.
   Distinguish current moderation snapshot from exact-version scanner evidence.

Rollback: restore the last reviewed Git source and matching generated archive via
normal reviewed PR; do not restore unsafe instructions just to satisfy a scanner.
For a bad approved release, use the registry's owner-reviewed rollback/tag path
only with applicable permission and record the actual resulting version. Preserve
product invite rollback and Secret Share behavior throughout.


## Observed remote state (2026-10-22, read-only)

[Existing remote receipt](sessions/20261022-issue41/clawhub-existing-receipt.json)
records public GET identity, complete version file list, downloaded SKILL digest
and existing exact-version scan. Owner `toliuweijing`, latest1.9.5; SKILL SHA256
`72fbf588d345c5ae9f116c3e8c440b0e5fee35c45510cb59e81b44411d6bb49b`
matches the version API. Existing exact-version security status is `suspicious`
with warnings and a definitive existing scan result; current moderation is a
separate snapshot. No new scan was submitted. Remote inventory includes
`skill-card.md` despite its changelog saying removed, so inventory comparison must
cover all files, not just version strings. Candidate1.10.1 remains local/PR only.
GitHub-to-ClawHub drift is **OPEN, blocked on separate publication approval**.
