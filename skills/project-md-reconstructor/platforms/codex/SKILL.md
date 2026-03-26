---
name: project-md-reconstructor
description: Codex adapter for project-md-reconstructor. Use when Codex needs to scan an existing repository and generate docs/project.md from a fixed project context template.
license: MIT
compatibility: No special runtime required
metadata:
  author: pocket-skills
  version: "1.0"
---

# Project MD Reconstructor

Use the main skill at `../../SKILL.md`.

Also read:

- `../../references/project-template.md`
- `../../references/scanning-rules.md`

When invoked:

1. Create `docs/project.md` from the template if it does not exist.
2. Scan the repository.
3. Fill the template with project purpose, tech stack, conventions, reusable building blocks, constraints, and dependencies.
4. Keep the structure unchanged.
