---
name: copilot-propose
description: Codex adapter for pocket-copilot propose. 基于 rules、knowledge 和仓库事实生成 change proposal。
license: MIT
compatibility: No special runtime required
metadata:
  author: pocket-skills
  version: "1.0"
---

# Pocket Copilot Propose

- `../../references/propose-contract.md`

Use this skill to create `pocket-copilot/changes/<change-name>/` with:

1. `spec.md`
2. `tasks.md`
3. `log.md`

Requirements:

- research first
- cite repository evidence for current-state findings
- list unresolved questions explicitly
- do not start implementation in this phase
