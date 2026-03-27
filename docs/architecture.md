# Architecture

## Design Principles

### 1. Self-Contained Skills

Each skill is a complete, standalone unit:

| Component | Purpose |
|-----------|---------|
| `SKILL.md` | Main entry point with instructions for AI agents |
| `scripts/` | Automation scripts (stack detection, extraction, merging) |
| `references/` | Templates, rules, and examples |
| `platforms/` | Platform-specific adapters |

### 2. Shared Within Skill, Not Across

Skills do not share resources with each other:

- Each skill can be independently installed / updated
- No cross-skill dependencies
- Simple, predictable structure

### 3. Platform Adapters

Lightweight wrappers that:

- Reference the main skill's resources via relative paths (`../../scripts/`, `../../references/`)
- Add platform-specific configurations
- Maintain consistent output contracts

### 4. Command Naming

- **Installed commands** use a `pocket-` prefix (e.g., `pocket-generate-prd-from-code`)
- **Source directories** under `skills/` keep original kebab-case names

## Directory Structure

```text
pocket-skills/
├── skills/
│   └── [skill-name]/
│       ├── SKILL.md               # Universal skill definition
│       ├── references/            # Templates, rules, examples
│       ├── scripts/               # Automation scripts
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

```
../../scripts/      → Main skill scripts
../../references/   → Main skill templates & rules
../../SKILL.md      → Main skill entry point
```

## Installer Behavior

The `install.py` installer:

1. **Auto-discovers** all skills under `skills/` (no config needed)
2. **Copies** skill files to platform-specific locations
3. **Prefixes** installed commands with `pocket-`
4. **Supports** install, uninstall, interactive, and CLI modes

| Platform | Install Location |
|----------|-----------------|
| Claude Code | `~/.claude/commands/pocket-<skill>.md` |
| Cursor | `~/.cursor/rules/pocket-<skill>/` |
| Codex | `~/.codex/skills/pocket-<skill>/` |
| Gemini CLI | `~/.gemini/commands/pocket-<skill>.toml` |

## Adding New Skills

1. Create directory under `skills/`
2. Add `SKILL.md` with YAML frontmatter (`name`, `description`)
3. Add supporting files (`scripts/`, `references/`)
4. Add platform adapters under `platforms/`
5. Installer auto-discovers — no other config changes needed
