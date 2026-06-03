# Draft Skills

Agent skills for InnoSage Draft.

Current contract:
- live page commands use the headless v2 Draft CLI daemon
- hosted Secret Share and auth commands stay supported
- browser-backed relay, `draft daemon`, runtime v1, CLI workspace mode, and `draft public-comments ...` are removed

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
| Draft page reads/writes or Secret Share/auth commands | [draft-cli](skills/draft-cli) | Canonical headless Draft CLI skill. |
| Working on the repo-local CLI in `products/notion-editor/cli` | [draft-cli-dev](skills/draft-cli-dev) | Uses the repo-local binary on an isolated port. |

## Skills

| Skill | Description |
| --- | --- |
| [draft-cli](skills/draft-cli) | Headless `draft` / `draft page ...` operations plus hosted Secret Share/auth commands. |
| [draft-agent-loop](skills/draft-agent-loop) | Approval-gated workflow built on top of headless Draft page operations. |
| [draft-cli-dev](skills/draft-cli-dev) | Repo-local CLI development lane with default port `31414`. |

## Merge Gate

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
