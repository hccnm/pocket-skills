# Pocket Skills

[English](README.md) | [中文](docs/README_CN.md)

A curated collection of AI-friendly skills for code analysis, documentation generation, and more. Each skill is self-contained with platform adapters for Claude Code, Cursor, Codex, and Gemini CLI.

## Why Pocket Skills?

- **Self-contained** — Each skill bundles its own instructions, references, and platform adapters
- **Multi-platform** — Works with Claude Code, Cursor, Codex, and Gemini CLI
- **One-command install** — Interactive installer with checkbox selection
- **Evidence-backed** — Skills produce structured, verifiable outputs

## Available Skills

### [generate-prd-from-code](skills/generate-prd-from-code/SKILL.md)

Reverse-engineer a codebase into a business-first PRD (Product Requirement Document). Supports two modes:

- **Source-driven** — Explore repository structure, routes, services, entities, menus, and docs directly to infer product scope
- **Frontend-enhanced** — Crawl a live UI to capture pages, fields, and flows, then trace them back to source logic for a complete frontend-backend closed loop

Output: AI context overview + main PRD + per-module appendices + coverage checklist.

### [project-md-reconstructor](skills/project-md-reconstructor/SKILL.md)

Recreate the OpenSpec `project.md` workflow for the current repository — first classify the workspace as frontend, backend, full-stack, or unclear, then generate a reuse-aware `docs/project.md` plus only the matching technical document(s) for the detected side.

## Quick Start

### 1. Install

```bash
# macOS / Linux
./install.sh

# Windows
install.bat

# Or directly with Python
python3 install.py
```

### 2. Use in Claude Code

```bash
# Generate a PRD from the current project
/pocket-generate-prd-from-code

# Generate docs/project.md and the matching technical doc(s) from the current project
/pocket-project-md-reconstructor
```

### 3. Use in Cursor

Copy the `.cursorrules` from the skill's platform adapter to your project root:

```bash
cp skills/generate-prd-from-code/platforms/cursor/.cursorrules /path/to/your/project/
```

### 4. Use in Codex / Gemini CLI

After installation, skills are available under:
- Codex: `~/.codex/skills/pocket-<skill-name>/`
- Gemini CLI: `~/.gemini/commands/pocket-<skill-name>.toml`

## Installation

### Requirements

- Python 3.8+
- [questionary](https://github.com/tmbo/questionary) for interactive mode

### Interactive Mode

The installer walks you through:

1. Choose **Install** or **Uninstall**
2. Select skills via checkbox (Space to toggle, Enter to confirm)
3. Select target tools
4. Confirm and execute

```bash
pip install questionary   # Required for interactive mode
```

### Command Line Mode

```bash
# Install specific skills to specific tools
python3 install.py --skills generate-prd-from-code --tools claude-code

# Install all skills to all tools
python3 install.py --skills all --tools all

# Skip confirmation
python3 install.py --skills generate-prd-from-code --tools all --yes

# Uninstall
python3 install.py --uninstall --skills all --tools all --yes

# Help
python3 install.py --help
```

| Parameter | Description |
|-----------|-------------|
| `--skills` | Comma-separated skill names, or `all` |
| `--tools` | `claude-code`, `cursor`, `codex`, `gemini-code`, or `all` |
| `--uninstall` | Switch to uninstall mode |
| `--yes`, `-y` | Skip confirmation prompts |

## Manual Usage

Skills can also be used without the installer:

1. Open the target repository in your coding agent.
2. Invoke `generate-prd-from-code`.
3. Let the agent inspect the workspace first and decide whether the currently available evidence is enough.
4. If a frontend URL is available, provide it so the agent can capture live page evidence.
5. Review the generated files under `docs/prd/`.

## Repository Layout

```text
pocket-skills/
├── skills/                          # Skill collection
│   ├── generate-prd-from-code/
│   │   ├── SKILL.md                 # Skill definition
│   │   ├── references/              # Templates & rules
│   │   └── platforms/               # Platform adapters
│   │       ├── claude-code/
│   │       ├── cursor/
│   │       ├── codex/
│   │       └── gemini-code/
│   └── project-md-reconstructor/
│       ├── SKILL.md
│       ├── references/
│       └── platforms/
├── install.py                       # Installer
├── install.sh / install.bat         # Launchers
└── docs/                            # Documentation
```

## Adding New Skills

1. Create a directory under `skills/` (kebab-case naming)
2. Add `SKILL.md` with YAML frontmatter
3. Add the supporting resources the skill actually needs, such as `references/`, `platforms/`, `agents/`, or optional `scripts/`
4. The installer auto-discovers new skills

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
