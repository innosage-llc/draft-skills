# Draft Skills

Agent skills for InnoSage Draft.

Current contract:
- canonical `draft-cli` skill1.10.1 includes saved PNG/JPEG inventory → original local
  extraction → image-capable runtime viewing; feature-detect `page get-image`.
  The verified npm pin is `@innosage/draft-cli@1.0.171`; older CLI versions may
  not include it. A skill update alone does not upgrade the CLI binary.
- live page commands prefer the configured JSON Workspace and workspace metadata commands
- `draft --workspace-json <folder>` remains the explicit override for one-off page operations
- hosted Secret Share and auth commands stay supported
- browser-backed relay, `draft daemon`, runtime v1, `draft open`, `draft public-comments ...`, and `--mode workspace` are removed

These skills follow the [Agent Skills specification](https://agentskills.io/specification).

## Installation

### Marketplace (Claude Code)

```bash
/plugin marketplace add innosage-llc/draft-skills
/plugin install draft@draft-skills
```

### npx skills

```bash
npx skills add git@github.com:innosage-llc/draft-skills.git
```

### Manual

- Claude Code: add this repo under `/.claude`
- Codex CLI: copy `skills/` into `~/.codex/skills`
- OpenCode:

```sh
git clone https://github.com/innosage-llc/draft-skills.git ~/.opencode/skills/draft-skills
```

## Skill Selection

| Situation | Skill | Why |
| --- | --- | --- |
| Draft page reads/writes or Secret Share/auth commands | [draft-cli](skills/draft-cli) | Canonical JSON Workspace-first Draft CLI skill. |
| Working on the repo-local CLI in `products/notion-editor/cli` | [draft-cli-dev](skills/draft-cli-dev) | Uses the repo-local binary on an isolated port. |

## Skills

| Skill | Description |
| --- | --- |
| [draft-cli](skills/draft-cli) | JSON Workspace-first `draft` / `draft page ...` operations plus hosted Secret Share/auth commands. |
| [draft-agent-loop](skills/draft-agent-loop) | Approval-gated workflow built on top of headless Draft page operations. |
| [draft-cli-dev](skills/draft-cli-dev) | Repo-local CLI development lane with default port `31414`. |

## Merge Gate

Image support is distributed through the existing Git/marketplace/manual routes
above. Check the installed `skills/draft-cli/SKILL.md` version and CLI command
capability together. Local Codex image viewing has been exercised with isolated
synthetic PNG/JPEG outputs; this does not claim every model/runtime or ChatGPT Web
consumes CLI files. No separate inference service is introduced.

Run the local gate before merging:

```bash
./scripts/gate
```

Equivalent commands:

```bash
npm run gate
npm run smoke
npm run regression
```

Gate order:
1. structural validation
2. `draft-cli` review-loop regression guard
3. Phase 2 smoke checks
4. Phase 3 regression checks
5. Offline security guidance, distribution and release preflight checks


## Public feedback and release consistency

Skill1.10.1 adds bounded first-party feedback guidance and removes obsolete invite
setup. Public feedback stays no-auth/no-daemon; a fetch runtime must actually
restrict destination IPs and disable redirects or the agent must skip retrieval.
The deterministic fixtures are reference policy checks, not a network sandbox or
proof of agent compliance. See [distribution/release notes](docs/distribution.md)
for verified npm/installer sources, active mirrors, archive regeneration, release
approval and exact remote artifact/audit receipts.

```bash
python3 scripts/check_draft_cli_security.py
python3 scripts/check_skill_distribution.py
python3 scripts/check_release_preflight.py
./scripts/publish_clawhub_skills.sh --dry-run --skill draft-cli
```

Dry-run is the default and never commits or publishes. Public release requires
separate approval and explicit `--publish`; a successful upload is not proof of
remote source equality or audit PASS.
