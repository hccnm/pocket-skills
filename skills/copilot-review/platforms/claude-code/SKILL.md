---
name: copilot-review
description: Claude Code adapter for pocket-copilot review. 对已有 change 做两阶段审查：Spec Compliance 与 Code Quality。
license: MIT
compatibility: No special runtime required
metadata:
  author: pocket-skills
  version: "1.0"
---

# Pocket Copilot Review

- `../../references/spec-compliance-checklist.md`
- `../../references/code-quality-checklist.md`

Use this skill to review an existing `pocket-copilot` change in two phases:

1. Spec Compliance
2. Code Quality

Rules:

- do not merge the two phases into one generic review
- stop after phase 1 if spec compliance fails
- produce a clear PASS / FAIL conclusion
