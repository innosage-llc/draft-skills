# Draft Skills

Agent skills for multiple Draft runtime planes:
headless page automation for remote agents, browser-backed CLI for legacy local sessions, and workspace review flows for local markdown authorship.

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

## Skill Selection

Use this decision model first:

| If your environment looks like this | Use this skill | Why |
| ----------------------------------- | -------------- | --- |
| Remote OpenClaw agent, Docker, CI, Linux worker, isolated runtime | [draft-headless-pages](skills/draft-headless-pages) | Headless `v2` page automation is the correct default for agents that do not share a browser session with the user. |
| Remote agent with required human approval gates before and after execution | [draft-agent-loop](skills/draft-agent-loop) | Adds plan approval, execution logging, and sign-off on top of headless Draft pages. |
| Local desktop session with browser-backed Draft CLI behavior | [draft-cli](skills/draft-cli) | Supports the browser-backed runtime path. Keep this for local/manual operation, not as the default remote-agent choice. |
| Local Draft CLI development from this repository with a need to avoid collisions with another Draft workflow on the same machine | [draft-cli-dev](skills/draft-cli-dev) | Forces the repo-local CLI path and a dedicated development port so development work stays isolated from installed/global Draft usage. |
| Local repo markdown file is the source of truth and Draft is only the review surface | [draft-review-loop](skills/draft-review-loop) | Keeps authorship in local files and uses Draft for comments and review handoff. |

## Skills

| Skill                         | Description                                                                                                             |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [draft-headless-pages](skills/draft-headless-pages) | Headless Draft page automation for remote agents, Docker, CI, and Linux environments. This is the default Draft runtime skill for OpenClaw-style isolated environments. |
| [draft-agent-loop](skills/draft-agent-loop) | Approval-gated human-in-the-loop workflow built on top of headless Draft pages for remote agents. |
| [draft-cli](skills/draft-cli) | Operational skill for browser-backed or legacy Draft CLI commands. Useful for local desktop sessions, but not the default choice for remote OpenClaw agents. |
| [draft-cli-dev](skills/draft-cli-dev) | Development-lane skill for working on Draft CLI from this repo. Uses the repo-local CLI and a dedicated dev port to avoid collisions with installed/global Draft workflows on the same machine. |
| [draft-review-loop](skills/draft-review-loop) | Workflow skill for local-first authoring with Draft review handoff. Guides agents to write/update workspace markdown first, then ask humans to review in Draft and apply accepted feedback back to the local file. |

Boundary model:
- `draft-headless-pages`: headless `v2` page automation for remote agents
- `draft-agent-loop`: approval workflow layered on top of `draft-headless-pages`
- `draft-cli`: browser-backed or legacy operational path
- `draft-cli-dev`: repo-local Draft CLI development lane with isolated port defaults
- `draft-review-loop`: local-file review collaboration loop
- Source of truth in `draft-review-loop`: local workspace markdown
- Review surface in headless flows: published or preview Draft page URL

## Review Handoff Examples

Compact examples agents can imitate:

- Proposal review:
  - Local first: write `docs/proposals/q2-plan.md`
  - Open review surface: `draft open docs/proposals/q2-plan.md --json`
  - Handoff phrase: "I wrote `docs/proposals/q2-plan.md` locally and opened it in Draft for your review."
- Spec review:
  - Open and read comments: `draft open docs/spec.md --json` then `draft workspace comments docs/spec.md --json`
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
- `./scripts/quick_validate_draft_skills.py`

Product note:
- `draft-skills` intentionally permits a top-level `version` field in skill frontmatter.
- The local gate enforces the product contract through the repo-local validator above.

Merge rule (local-only workflow):
- If `scripts/gate` fails, do not merge.
- If `scripts/gate` passes, PR is eligible to merge.
- Gate order is:
  1. structural validation (`quick_validate.py`)
  2. `draft-cli` review-loop regression guard
  3. Phase 2 deterministic smoke checks
  4. Phase 3 regression corpus checks
  5. Phase 4 workflow regression checks (`draft-review-loop`)
