---
name: copilot-apply
description: 按 pocket-copilot change 中的 tasks.md 执行实现，严格按 spec 和 task 编码，逐步展示验证证据，并同步回写执行日志。适用于已完成提案并进入实现阶段的需求。
---

# Pocket Copilot Apply

## Overview

根据现有 `pocket-copilot/changes/<change-name>/` 中的 `spec.md` 与 `tasks.md` 执行实现。

这个 skill 只负责执行，不重新定义需求范围。

## Preconditions

- `pocket-copilot/changes/<change-name>/spec.md` 存在
- `pocket-copilot/changes/<change-name>/tasks.md` 存在
- 提案阶段已完成关键澄清

如果前置条件不满足，必须先停下并指出缺口。

## Core Rules

- 只按 `tasks.md` 执行，不自由扩写需求。
- 完成每个 task 后都要展示验证证据。
- 有偏差时先回写文档，再继续。
- 默认中文输出。

## Workflow

### 1. Read before change

执行前先读取：

- `spec.md`
- `tasks.md`
- `log.md`
- 相关 `rules/` 与 `knowledge/`

### 2. Execute task by task

按 `tasks.md` 顺序执行，推荐一次完成一个 task。

每个 task 完成后必须至少提供一种证据：

- 编译输出
- 测试输出
- 类型检查输出
- 命令行结果
- 运行结果或截图说明

### 3. Sync documents

执行后同步更新：

- `spec.md` 的执行日志
- `log.md` 的时间线、踩坑或知识发现

如实现发现计划不准确，先修文档再继续代码。

## References

- `references/apply-contract.md`

## Notes

- 如果用户要求批量执行，可连续完成多个 task，但每个 task 仍要保留验证证据。
- 不要在 apply 阶段做未经确认的范围扩张。
