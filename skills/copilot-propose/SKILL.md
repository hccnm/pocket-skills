---
name: copilot-propose
description: 为目标仓库中的某个需求创建 pocket-copilot change 提案，基于 rules、knowledge 和仓库事实生成 spec.md、tasks.md、log.md，并明确待澄清项。适用于任何进入编码前需要先做结构化提案的场景。
---

# Pocket Copilot Propose

## Overview

在 `pocket-copilot/changes/<change-name>/` 下创建变更提案，并生成：

- `spec.md`
- `tasks.md`
- `log.md`

这个 skill 负责提案，不负责编码。

## Preconditions

调用前必须先确认：

- `pocket-copilot/` 已存在
- `pocket-copilot/rules/` 已存在
- `pocket-copilot/knowledge/index.md` 已存在

如果初始化目录不存在，先让用户运行 `pocket-copilot-init`。

## Core Rules

- 所有代码现状结论必须附出处。
- 不要跳过 research 直接写方案。
- 待澄清项未清空前，不进入 apply。
- 不要在提案阶段修改代码。
- 默认中文输出。

## Workflow

### 1. Research first

先读取：

- `pocket-copilot/rules/`
- `pocket-copilot/knowledge/`
- 与当前需求相关的仓库代码、配置、文档

把结论写进 `spec.md` 的“代码现状”部分，并附路径或符号出处。

### 2. Clarify scope

先收敛：

- 目标是什么
- 哪些内容明确在范围内
- 哪些内容不在范围内
- 当前还有哪些未知点

### 3. Generate proposal files

在 `pocket-copilot/changes/<change-name>/` 下生成：

- `spec.md`
- `tasks.md`
- `log.md`

要求：

- `spec.md` 记录背景、现状、功能点、风险、待澄清
- `tasks.md` 把需求拆成可验证的原子任务
- `log.md` 记录当前阶段的关键决策

### 4. Gate before apply

在结束前明确指出：

- 哪些待澄清项仍未解决
- 当前是否可以进入 `pocket-copilot-apply`

若仍有未决问题，结论必须是“暂不能进入 apply”。

## References

- `references/propose-contract.md`

## Notes

- `change-name` 应稳定、可读、适合做目录名。
- 不要把“nice to have”混进本次主变更。
