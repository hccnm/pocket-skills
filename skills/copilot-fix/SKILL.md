---
name: copilot-fix
description: 对 pocket-copilot change 做 review 后的增量修正，聚焦已有变更的偏差、遗漏或质量问题，并强制同步 spec、tasks、log。适用于 apply 之后的修订迭代。
---

# Pocket Copilot Fix

## Overview

在已有 `pocket-copilot/changes/<change-name>/` 基础上做增量修正。

这个 skill 不是重新开始 apply，而是处理 review 或人工发现的问题。

## Preconditions

- 目标 change 已存在
- `spec.md`、`tasks.md`、`log.md` 已存在
- 已经有明确的修正原因，例如：
  - review 发现的问题
  - 人工验收反馈
  - 实施过程中的偏差记录

## Core Rules

- 只做增量修正，不重写整套方案。
- 每次 fix 后都要同步：
  - `spec.md`
  - `tasks.md`
  - `log.md`
- 默认中文输出。

## Workflow

### 1. Confirm what is being fixed

先明确：

- 问题是什么
- 来自哪里
- 影响哪些任务、功能点或规则

### 2. Update docs first when needed

若发现当前 spec 或 tasks 已过期，先修文档，再动代码。

### 3. Apply targeted changes

只修改与本次 fix 相关的最小范围实现。

### 4. Record the fix

把本次修正写回：

- `spec.md`
- `tasks.md`
- `log.md`

并补充验证证据。

## References

- `references/fix-contract.md`
