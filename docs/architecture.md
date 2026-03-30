# Architecture

## Design Principles

### 1. Self-Contained Skills

Each skill is a complete, standalone unit:

| Component | Purpose |
|-----------|---------|
| `SKILL.md` | Main entry point with instructions for AI agents |
| `references/` | Templates, rules, examples, and shared guidance |
| `platforms/` | Platform-specific adapters |
| `agents/` | Optional platform metadata or prompts |
| `scripts/` | Optional helper automation for skills that still need it |

### 2. Shared Within Skill, Not Across

Skills do not share resources with each other:

- Each skill can be independently installed or updated
- No cross-skill dependencies
- Simple, predictable structure

### 3. Platform Adapters

Lightweight wrappers that:

- specialize the main skill workflow for a specific tool
- reference the main skill's resources via relative paths when needed
- maintain consistent output contracts

### 4. Command Naming

- **Installed commands** use a `pocket-` prefix (for example `pocket-generate-prd-from-code`)
- **Source directories** under `skills/` keep original kebab-case names

## Directory Structure

```text
pocket-skills/
├── skills/
│   └── [skill-name]/
│       ├── SKILL.md               # Universal skill definition
│       ├── references/            # Templates, rules, examples
│       ├── agents/                # Optional metadata
│       ├── scripts/               # Optional helper scripts
│       └── platforms/
│           ├── claude-code/       # Claude Code adapter
│           ├── cursor/            # Cursor adapter + .cursorrules
│           ├── codex/             # Codex CLI adapter
│           └── gemini-code/       # Gemini CLI adapter + .toml
├── install.py                     # Interactive installer
├── install.sh                     # macOS/Linux launcher
├── install.bat                    # Windows launcher
└── docs/                          # Documentation
```

## Path Conventions

From within a platform adapter directory:

```text
../../references/   → Main skill templates and rules
../../agents/       → Optional platform metadata
../../SKILL.md      → Main skill entry point
```

## Installer Behavior

The `install.py` installer:

1. **Auto-discovers** all skills under `skills/`
2. **Copies** each skill's self-contained resources into platform-specific locations
3. **Prefixes** installed commands with `pocket-`
4. **Supports** install, uninstall, interactive, and CLI modes

| Platform | Install Location |
|----------|-----------------|
| Claude Code | `~/.claude/commands/pocket-<skill>.md` |
| Cursor | `~/.cursor/rules/pocket-<skill>/` |
| Codex | `~/.codex/skills/pocket-<skill>/` |
| Gemini CLI | `~/.gemini/commands/pocket-<skill>.toml` |

## Adding New Skills

1. Create a directory under `skills/`
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Add the supporting resources the skill actually needs
4. Add platform adapters under `platforms/`
5. Installer auto-discovers the skill with no extra config
