# Contributing to Pocket Skills

Thank you for your interest in contributing!

## How to Contribute

### Adding a New Skill

1. **Fork and clone** the repository
2. **Create a skill directory** under `skills/`:
   ```
   skills/your-skill-name/
   ├── SKILL.md           # Required: Main entry with frontmatter
   ├── references/        # Optional: Templates, rules, examples
   ├── scripts/           # Optional: Automation scripts
   └── platforms/         # Optional: Platform adapters
       ├── claude-code/
       │   └── SKILL.md
       ├── cursor/
       │   ├── SKILL.md
       │   └── .cursorrules
       ├── codex/
       │   └── SKILL.md
       └── gemini-code/
           └── SKILL.md
   ```
3. **Write the SKILL.md** with proper frontmatter:
   ```yaml
   ---
   name: your-skill-name
   description: Brief description of what the skill does
   ---

   # Skill Title

   ## Overview
   ...
   ```
4. **Test** with each supported platform
5. **Submit a pull request**

The installer auto-discovers new skills — no other config files need updating.

### Improving Existing Skills

1. Open an issue to discuss proposed changes
2. Fork and make your improvements
3. Ensure backwards compatibility
4. Submit a pull request

## Skill Guidelines

### SKILL.md Requirements

- Must have YAML frontmatter with `name` and `description`
- Should be clear enough for an AI agent to follow autonomously
- Recommended sections: Overview, Quick Start, Workflow, Output Contract, References

### Code Standards

- Python scripts: compatible with Python 3.8+
- Clear variable names with comments
- Include usage examples in SKILL.md or script docstrings

### Platform Adapters

- Reference main skill resources via relative paths (`../../scripts/`, `../../references/`)
- Document any platform-specific requirements
- Installed commands are prefixed with `pocket-`

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue for any questions or discussions.
