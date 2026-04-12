# Draft Skills

Agent Skills for Draft's dual-surface collaboration model:
local workspace markdown for authoring, plus Draft GUI/CLI for human review and coordination.

These skills follow the [Agent Skills specification](https://agentskills.io/specification) so they can be used by any skills-compatible agent, including Claude Code, Codex CLI, and Cursor.

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

### Manually

#### Claude Code

Add the contents of this repo to a `/.claude` folder in the root of your project. See more in the [official Claude Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

#### Codex CLI

Copy the `skills/` directory into your Codex skills path (typically `~/.codex/skills`).

#### OpenCode

Clone the entire repo into the OpenCode skills directory (`~/.opencode/skills/`):

```sh
git clone https://github.com/innosage-llc/draft-skills.git ~/.opencode/skills/draft-skills
```

## Skills

| Skill                         | Description                                                                                                             |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [draft-cli](skills/draft-cli) | Operational skill for Draft transport and commands. Manage workspace/page operations, open local files in Draft for review, and run comment/publish flows safely through the CLI. Requires the [draft-cli binary](https://www.npmjs.com/package/@innosage/draft-cli). |
| [draft-review-loop](skills/draft-review-loop) | Workflow skill for local-first authoring with Draft review handoff. Guides agents to write/update workspace markdown first, then ask humans to review in Draft and apply accepted feedback back to the local file. |

Boundary model:
- `draft-cli`: how to operate Draft safely and correctly.
- `draft-review-loop`: how to run the local-first authoring and Draft review collaboration loop.
- Source of truth: local workspace markdown.
- Review surface: Draft GUI.

## Review Handoff Examples

Compact examples agents can imitate:

- Proposal review:
  - Local first: write `docs/proposals/q2-plan.md`
  - Open review surface: `draft open docs/proposals/q2-plan.md --json`
  - Handoff phrase: "I wrote `docs/proposals/q2-plan.md` locally and opened it in Draft for your review."
- Spec review:
  - Open and read comments: `draft open docs/spec.md --json` then `draft comments list docs/spec.md --json`
  - Handoff phrase: "Please leave comments in Draft; I will apply accepted feedback to `docs/spec.md` locally."
- Release-note review:
  - Local first: write `docs/releases/2026-04-12.md`
  - Open review surface: `draft open docs/releases/2026-04-12.md --json`
  - Handoff phrase: "Release notes are authored locally and ready for your Draft review."

Always keep local markdown as the source of truth. Use Draft as the review surface, not the default authoring surface.

## Local Merge Gate

Run this before merging any PR to `main`:

```bash
./scripts/gate
```

Equivalent npm shortcut:

```bash
npm run gate
```

Phase 2 smoke command (runs only deterministic smoke assertions):

```bash
npm run smoke
```

Phase 3 regression command (runs checked-in typed regression corpus):

```bash
npm run regression
```

Validator location (repo-local default):
- `./.agents/skills/skill-creator/scripts/quick_validate.py`

Merge rule (local-only workflow):
- If `scripts/gate` fails, do not merge.
- If `scripts/gate` passes, PR is eligible to merge.
- Gate order is structural (`quick_validate.py`) first, then behavioral smoke checks, then regression corpus checks.
