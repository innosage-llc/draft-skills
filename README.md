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
| [draft-cli](skills/draft-cli) | Manage Draft pages using the Draft CLI. List, read, create, append, replace, and patch documents from the command line. |
