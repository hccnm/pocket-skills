# Pocket Skills

[English](README.md) | [中文](docs/README_CN.md)

A curated collection of AI-friendly skills for code analysis, documentation generation, and more. Each skill is self-contained with platform adapters for Claude Code, Cursor, Codex, Gemini CLI, and other AI coding assistants.

## Why Pocket Skills?

- **Self-contained**: Each skill includes its own scripts, references, and platform adapters
- **Multi-platform**: Works with Claude Code, Cursor, Codex, and Gemini CLI
- **Easy installation**: Interactive installer with checkbox selection
- **Evidence-backed**: Skills produce structured, verifiable outputs

## Available Skills

| Skill | Description |
|-------|-------------|
| [generate-prd-from-code](skills/generate-prd-from-code/SKILL.md) | Reverse-engineer a codebase into a business-first PRD |

## Repository Layout

```text
pocket-skills/
├── skills/                    # All skills collection
│   └── generate-prd-from-code/
│       ├── SKILL.md           # Main entry (universal version)
│       ├── references/        # Templates and rules
│       ├── scripts/           # Python extraction scripts
│       └── platforms/         # Platform adapters
│           ├── claude-code/
│           ├── cursor/
│           ├── codex/
│           └── gemini-code/
├── install.py                 # Interactive installer
├── install.sh                 # macOS/Linux launcher
├── install.bat                # Windows launcher
└── docs/                      # Documentation
```

## Installation

### Requirements

- Python 3.8+
- Optional: [questionary](https://github.com/tmbo/questionary) for enhanced interactive experience

### Interactive Installation

Run the installer:

```bash
# macOS/Linux
./install.sh

# Windows
install.bat

# Or directly with Python
python3 install.py
```

The installer will:
1. Show a main menu to choose **Install** or **Uninstall**
2. Display available skills with a checkbox interface
3. Let you select target tools (Claude Code, Cursor, Codex, Gemini CLI, or all)
4. Confirm and execute the installation

### Command Line Options

For non-interactive or scripted use:

```bash
# Install specific skills
python3 install.py --skills generate-prd-from-code --tools claude-code

# Install multiple skills
python3 install.py --skills skill1,skill2 --tools claude-code,cursor,codex

# Install all skills to all tools
python3 install.py --skills all --tools all

# Skip confirmation prompts
python3 install.py --skills generate-prd-from-code --tools all --yes

# Uninstall skills
python3 install.py --uninstall --skills generate-prd-from-code --tools claude-code

# Uninstall all skills from all tools
python3 install.py --uninstall --skills all --tools all --yes

# Show help
python3 install.py --help
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `--skills` | Comma-separated list of skills to install/uninstall, or `all` |
| `--tools` | Target tools: `claude-code`, `cursor`, `codex`, `gemini-code`, or `all` |
| `--uninstall` | Switch to uninstall mode |
| `--yes`, `-y` | Skip confirmation prompts |

### Enhanced Interactive Mode

For the best interactive experience with checkbox selection (Space to toggle, Arrow keys to navigate), install questionary:

```bash
pip install questionary
```

Without questionary, the installer falls back to a simple number-based selection.

## Uninstallation

To remove installed skills:

```bash
# Interactive uninstall
python3 install.py --uninstall

# Non-interactive uninstall
python3 install.py --uninstall --skills generate-prd-from-code --tools claude-code --yes
```

## Quick Start

### Using with Claude Code

After installation, use the skill in your project:

```
/generate-prd-from-code
```

### Manual Usage

```bash
# Navigate to the skill directory
cd skills/generate-prd-from-code

# Run the scripts directly
python3 scripts/detect_stack.py --repo /path/to/your/repo --pretty
python3 scripts/extract_repo_facts.py --repo /path/to/your/repo --output /tmp/repo-facts.json
python3 scripts/merge_evidence.py --facts /tmp/repo-facts.json --output-dir /path/to/your/repo/docs/prd --language zh
```

### Using with Cursor

```bash
cd skills/generate-prd-from-code/platforms/cursor
# Copy .cursorrules to your project root
```

### Using with Codex

After installation, the skill is available under `~/.codex/skills/generate-prd-from-code/`.

### Using with Gemini CLI

The installer creates:

- a global command at `~/.gemini/commands/generate-prd-from-code.toml`
- support files under `~/.gemini/pocket-skills/generate-prd-from-code/`

Gemini CLI also supports project-level custom commands in `.gemini/commands/` when you want repository-scoped workflows.

## Adding New Skills

To add a new skill:

1. Create a directory under `skills/` with your skill name (use kebab-case)
2. Add a `SKILL.md` file with frontmatter and instructions
3. Add `scripts/` for automation scripts
4. Add `references/` for templates and rules
5. Add `platforms/` for platform-specific adapters

The installer will automatically discover any new skills added to the `skills/` directory.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
