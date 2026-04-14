---
name: copilot-review
description: 对 pocket-copilot change 执行两阶段审查，先检查 spec 合规性，再检查代码质量与安全性，输出分阶段结论。适用于 apply 或 fix 之后的正式审查。
---

# Pocket Copilot Review

## Overview

对 `pocket-copilot/changes/<change-name>/` 执行双阶段 review：

1. Phase 1: Spec Compliance
2. Phase 2: Code Quality

Phase 1 不通过时，不进入 Phase 2。

## Preconditions

- 目标 change 已存在
- `spec.md`、`tasks.md`、`log.md` 已存在
- apply 或 fix 已完成到可审查状态

## Core Rules

- 输出必须按阶段拆开。
- 不信执行报告，只信实际代码与文档。
- 审查阶段默认只读思维，不主动扩大实现范围。
- 默认中文输出。

## Workflow

### Phase 1: Spec Compliance

逐条核对：

- spec 要求的功能是否已实现
- 是否有 spec 未要求的多余实现
- 是否存在理解偏差
- 业务规则和接口/数据变更是否正确落地

### Phase 2: Code Quality

仅在 Phase 1 通过后执行，重点检查：

- 安全性
- 可维护性
- 异常处理
- 命名与结构
- 是否违反 rules 中的要求

## Output Contract

必须输出：

- Phase 1 结果
- Phase 2 结果或“未进入 Phase 2”的原因
- 总结论：PASS / FAIL
- 建议回到 `fix` 的问题清单

## References

- `references/spec-compliance-checklist.md`
- `references/code-quality-checklist.md`
