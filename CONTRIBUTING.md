# Contributing to Pocket Skills

Thank you for your interest in contributing to Pocket Skills!

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
       │   └── SKILL.md
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

4. **Test thoroughly** with each supported platform
5. **Update README.md** to list your skill
6. **Submit a pull request**

### Improving Existing Skills

1. Open an issue to discuss your proposed changes
2. Fork and make your improvements
3. Ensure backwards compatibility
4. Submit a pull request

## Skill Guidelines

### SKILL.md Requirements

- Must have YAML frontmatter with `name` and `description`
- Should be clear enough for an AI agent to follow
- Should include:
  - Overview
  - Quick Start
  - Workflow/Steps
  - Output Contract
  - References (if applicable)

### Code Standards

- Python scripts should be compatible with Python 3.8+
- Use clear variable names and add comments
- Include usage examples in the script or SKILL.md

### Platform Adapters

- Each adapter should reference the main skill's resources using relative paths
- Use `../../scripts/` and `../../references/` from within platform directories
- Document any platform-specific requirements

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open an issue for any questions or discussions.