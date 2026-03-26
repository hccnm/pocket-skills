# Pocket Skills Architecture

## Design Principles

### 1. Self-Contained Skills

Each skill is a complete, standalone unit containing:
- **SKILL.md**: Main entry point with instructions
- **scripts/**: Automation scripts
- **references/**: Templates, rules, and examples
- **platforms/**: Platform-specific adapters

### 2. Shared Within Skill, Not Across Skills

Skills do not share resources with each other. This ensures:
- Each skill can be independently installed/updated
- No cross-skill dependencies to manage
- Simple, predictable structure

### 3. Platform Adapters

Platform adapters are lightweight wrappers that:
- Reference the main skill's resources using relative paths (`../../scripts/`, `../../references/`)
- Add platform-specific instructions or configurations
- Maintain consistent output contracts

## Directory Structure

```
pocket-skills/
├── skills/                    # All skills (one per directory)
│   └── [skill-name]/
│       ├── SKILL.md           # Main entry (universal version)
│       ├── references/        # Templates, rules, examples
│       ├── scripts/           # Automation scripts
│       └── platforms/         # Platform adapters
│           ├── claude-code/
│           │   └── SKILL.md
│           ├── cursor/
│           │   ├── SKILL.md
│           │   └── .cursorrules
│           ├── codex/
│           │   ├── SKILL.md
│           │   └── agents/
│           └── gemini-code/
│               └── SKILL.md
├── scripts/                   # Repository-level scripts (installers)
├── docs/                      # Documentation
├── README.md
└── CONTRIBUTING.md
```

## Path Conventions

From within a platform adapter:
- `../../scripts/` → Main skill's scripts
- `../../references/` → Main skill's references
- `../../SKILL.md` → Main skill's entry point

## Adding New Skills

1. Create directory under `skills/`
2. Add `SKILL.md` with frontmatter
3. Add supporting files (scripts, references)
4. Add platform adapters as needed
5. Update README.md

## Future Considerations

- Skill discovery/indexing
- Version management per skill
- Cross-platform testing automation