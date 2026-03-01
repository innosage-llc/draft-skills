# Idea Evaluation: `draft-skills` Repo

## Concept

Create a public `innosage-llc/draft-skills` repo following the [Agent Skills specification](https://agentskills.io/specification), modeled after [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills). The repo would list skills published to the web, with `draft-cli` as the first skill.

---

## What You Already Have

**`@innosage/draft-cli@0.7.0`** — a fully functional CLI with 8 commands:

| Command | Purpose |
|---|---|
| `draft daemon [url]` | Start background daemon for PWA connections |
| `draft status` | Check connection with Draft PWA |
| `draft ls` | List all pages |
| `draft cat <id>` | View page content (markdown/json/raw) |
| `draft create [title]` | Create a new page |
| `draft append <id>` | Append content to a page |
| `draft replace <id>` | Replace a semantic section by heading |
| `draft patch <id>` | Apply a unified diff to a page |

---

## The `obsidian-skills` Pattern You're Mirroring

```
obsidian-skills/
├── .claude-plugin/          ← Claude marketplace metadata
│   ├── plugin.json          ← name, version, description, author
│   └── marketplace.json     ← skill registry for marketplace
├── skills/
│   ├── obsidian-cli/SKILL.md    ← CLI interaction skill
│   ├── obsidian-markdown/SKILL.md
│   ├── obsidian-bases/SKILL.md
│   ├── json-canvas/SKILL.md
│   └── defuddle/SKILL.md
├── LICENSE
└── README.md                ← Skills table + installation methods
```

**Key pattern**: Each `SKILL.md` is a self-contained instruction set (YAML frontmatter + Markdown body) that teaches any agent how to use a specific tool.

---

## Options to Consider

### Option A: Pure Agent Skills Repo (Recommended Start)

**What**: Mirror `obsidian-skills` exactly. A repo of `SKILL.md` files.

```
innosage-llc/draft-skills/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   └── draft-cli/SKILL.md       ← First skill
├── LICENSE (MIT)
└── README.md
```

**Installation by users**:
```bash
# Claude Code marketplace
/plugin marketplace add innosage-llc/draft-skills

# skills.sh (Vercel distribution hub)
npx skills add git@github.com:innosage-llc/draft-skills.git

# Manual
git clone ... into ~/.claude/skills/ or .agent/skills/
```

**Pros**:
- ✅ Lowest effort — one afternoon to ship v1
- ✅ Cross-platform: works with Claude Code, Codex CLI, Gemini CLI, Cursor, OpenCode
- ✅ Immediate visibility on skills.sh and Claude marketplace
- ✅ Follows the dominant standard (100k+ installs ecosystem-wide)

**Cons**:
- ⚠️ Skills are just instructions, not runnable tools — agent still needs `draft-cli` installed separately
- ⚠️ No web UI for browsing skills (just a GitHub README table)

---

### Option B: Skills Repo + Published Web Catalog

**What**: Same as Option A, but add an auto-generated static website listing all skills.

**Additional work**:
- Add a GitHub Action that generates a static site from `skills/*/SKILL.md`
- Deploy to GitHub Pages or your existing Cloudflare infrastructure
- e.g., `skills.draft.so` or `draft.so/skills`

**Pros**:
- ✅ Beautiful, browsable catalog for marketing
- ✅ SEO value — people searching "Draft AI editor CLI" find your skills
- ✅ Aligns with your Friday marketing workflow

**Cons**:
- ⚠️ Extra build/deploy pipeline to maintain
- ⚠️ Overkill if you only have 1-2 skills initially

---

### Option C: Skills as a Claude Code Plugin (with MCP Server)

**What**: Beyond static skills, bundle an MCP server that exposes `draft-cli` as live tools.

```
draft-skills/
├── .claude-plugin/
│   ├── plugin.json
│   └── mcp-servers/draft-cli.json   ← MCP server config
├── skills/
│   └── draft-cli/SKILL.md
└── src/
    └── mcp-server.ts                ← wraps draft CLI as MCP tools
```

**Pros**:
- ✅ Agent can use Draft commands as native tools (not just instructions)
- ✅ Higher fidelity — structured input/output, not just "run this bash command"
- ✅ Strongest differentiation from obsidian-skills

**Cons**:
- ⚠️ Significantly more engineering effort
- ⚠️ MCP server needs maintenance and versioning
- ⚠️ Scope creep risk — the CLI *already works* via bash

---

### Option D: Monorepo (Skills + CLI Source)

**What**: Move `draft-cli` source into the same repo as skills.

**Pros**:
- ✅ Single repo to maintain
- ✅ Skills and CLI always in sync

**Cons**:
- ❌ npm package would need restructuring
- ❌ Breaks the clean separation of "skills teach, CLI does"
- ❌ Against the `obsidian-skills` pattern (Obsidian CLI is a separate project)

---

## Recommendation

### Start with **Option A**, graduate to **Option B** on the first Marketing Friday

| Phase | What | When |
|---|---|---|
| **Phase 1** | Ship `draft-skills` repo with `draft-cli` skill | This weekend (1-2h) |
| **Phase 2** | Add web catalog (GitHub Pages or Cloudflare) | Next Marketing Friday |
| **Phase 3** | Add more skills: `draft-markdown`, `draft-publishing` | As features mature |
| **Phase 4** | Consider MCP server (Option C) if demand is proven | Q2 2026 |

### First Skill: `draft-cli/SKILL.md` Content Sketch

Based on the `obsidian-cli` pattern, your first `SKILL.md` would cover:

```yaml
---
name: draft-cli
description: >
  Interact with Draft pages using the Draft CLI to list, read, create,
  and edit documents. Use when the user asks to manage Draft content
  from the command line or integrate Draft with development workflows.
---
```

Body would document: installation (`npm install -g @innosage/draft-cli`), daemon setup, command reference, common patterns (list → cat → append workflow), and output format options.

---

## Future Skills Roadmap

| Skill | Description | Priority |
|---|---|---|
| `draft-cli` | CLI interaction (list, cat, create, append, replace, patch) | 🟢 First |
| `draft-markdown` | Draft-flavored markdown syntax, block types, conventions | 🟡 Next |
| `draft-publishing` | Publishing workflow (Cloudflare Workers, R2, custom domains) | 🟡 Next |
| `draft-collaboration` | Real-time collab patterns, Firestore schema | 🔵 Later |
| `draft-pwa` | PWA development, offline-first patterns, MHTML handling | 🔵 Later |
