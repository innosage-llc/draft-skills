# Draft Skills

Agent Skills for Draft — the performance-first markdown editor.

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
| [draft-cli](skills/draft-cli) | Manage Draft pages using the Draft CLI. List, read, create, append, replace, and patch documents from the command line. Requires the [draft-cli binary](https://www.npmjs.com/package/@innosage/draft-cli). |

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

Validator location (repo-local default):
- `./.agents/skills/skill-creator/scripts/quick_validate.py`

Merge rule (local-only workflow):
- If `scripts/gate` fails, do not merge.
- If `scripts/gate` passes, PR is eligible to merge.
- Gate order is structural (`quick_validate.py`) first, then behavioral smoke checks.
