---
name: copilot-fix
description: Claude Code adapter for pocket-copilot fix. 对已有 change 做增量修正并同步文档。
license: MIT
compatibility: No special runtime required
metadata:
  author: pocket-skills
  version: "1.0"
---

# Pocket Copilot Fix

- `../../references/fix-contract.md`

Use this skill to fix an existing `pocket-copilot` change.

Requirements:

- identify the concrete issue first
- update docs before code when the plan is stale
- keep the scope targeted
- sync `spec.md`, `tasks.md`, and `log.md`
