---
name: copilot-init
description: Gemini Code adapter for pocket-copilot init. 在当前仓库中安全初始化 pocket-copilot 工作流目录，并预填上下文与模板。
license: MIT
compatibility: Agent-native workflow; no external scripts required
metadata:
  author: pocket-skills
  version: "1.0"
---

# Pocket Copilot Init

- `../../references/project-context-template.md`
- `../../references/coding-style-template.md`
- `../../references/security-template.md`
- `../../references/domain-rules-template.md`
- `../../references/knowledge-index-template.md`
- `../../references/copilot-prompt-template.md`
- `../../references/spec-reviewer-template.md`
- `../../references/code-quality-reviewer-template.md`
- `../../references/change-spec-template.md`
- `../../references/change-tasks-template.md`
- `../../references/change-test-spec-template.md`
- `../../references/change-log-template.md`

Use this skill to initialize `pocket-copilot/` in the current repository.

When invoked:

1. Scan the repository first.
2. Create missing directories under `pocket-copilot/`.
3. Create only missing files from templates.
4. Prefill `rules/project-context.md` and other base rules carefully from repository evidence.
5. Never overwrite existing files.
6. End with `created / skipped / needs-manual-review`.
