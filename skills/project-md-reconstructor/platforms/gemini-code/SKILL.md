---
name: project-md-reconstructor
description: Gemini Code adapter for project-md-reconstructor. Use when Gemini Code needs to classify the current repository as frontend, backend, full-stack, or unclear, then generate docs/project.md and only the matching technical document(s).
license: MIT
compatibility: No special runtime required
metadata:
  author: pocket-skills
  version: "1.0"
---

# Project MD Reconstructor

- `../../references/project-template.md`
- `../../references/frontend-tech-template.md`
- `../../references/backend-tech-template.md`
- `../../references/scanning-rules.md`

Use this skill to reconstruct repository initialization docs from repository evidence.

When invoked:

1. Classify the current repository as frontend, backend, full-stack, or unclear.
2. Always create or improve `docs/project.md`.
3. Create or improve `docs/project-frontend-tech.md` only for frontend or full-stack repositories.
4. Create or improve `docs/project-backend-tech.md` only for backend or full-stack repositories.
5. If the project type is unclear, update only `docs/project.md` and list missing evidence.
6. Prefer evidence-backed statements and mark unclear conclusions as inferred or unknown.
