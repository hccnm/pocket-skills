---
name: copilot-archive
description: 归档已完成 review 的 pocket-copilot change，提取 log 中的知识发现和踩坑记录，沉淀到 knowledge，并将 change 移入 archives。适用于完整流程结束后的收口与知识沉淀。
---

# Pocket Copilot Archive

## Overview

归档已完成 review 的 `pocket-copilot` change，并做知识沉淀。

主要动作：

- 读取 `log.md`
- 提取知识发现和踩坑记录
- 建议写回 `knowledge/`
- 将 change 移入 `archives/<change-name>/`

## Preconditions

- `spec.md`、`tasks.md`、`log.md` 已存在
- review 已完成
- 当前 change 已达到可归档状态

## Core Rules

- 先总结，再归档。
- 知识沉淀优先写可复用规则，不写一次性噪音。
- 归档路径固定为 `pocket-copilot/archives/<change-name>/`
- 默认中文输出。

## Workflow

### 1. Read the change log

读取并整理：

- 时间线
- 技术决策
- 踩坑记录
- 知识发现
- Spec-Code 偏差记录

### 2. Propose knowledge entries

把适合长期沉淀的内容整理成知识项，建议写入：

- `knowledge/index.md`
- 或新的知识文档（如果用户需要更细颗粒度）

### 3. Archive the change

确认归档后，将整个 change 目录移到：

- `pocket-copilot/archives/<change-name>/`

## References

- `references/archive-contract.md`
