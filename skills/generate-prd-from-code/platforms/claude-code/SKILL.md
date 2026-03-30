---
name: generate-prd-from-code
description: Reverse-engineer an existing repository into a business-first PRD for initialization and AI onboarding using native repository exploration and available browser tools. If a paired frontend repo, paired backend repo, or running frontend URL is likely needed but missing, ask the user whether to supplement those inputs or explicitly proceed with a limited current-repo-only PRD.
license: MIT
compatibility: Agent-native workflow; no external extraction scripts required
metadata:
  author: pocket-skills
  version: "2.0"
---

# Generate PRD from Code

## Overview

Turn the available evidence into an AI-friendly, product-first initialization pack with:

- one AI context overview
- one main PRD
- one appendix per inferred module
- one initialization coverage check

This Claude Code adapter is agent-native:

- inspect repository files directly
- use browser tools only when the user provides a live frontend URL
- synthesize findings in-session
- write final Markdown directly without extraction scripts or intermediate JSON

## Preflight Gate

Before generating any PRD files, inspect the current workspace and classify the evidence shape:

- single full-stack repository
- frontend-only repository
- backend-only repository
- multi-project workspace with several candidate frontend/backend projects
- unclear or mixed workspace

Pause and ask the user before generating files when:

- the workspace looks backend-only and no frontend URL or paired frontend repo has been provided
- the workspace looks frontend-only and no paired backend repo has been provided
- the workspace contains multiple candidate projects, but the target product scope is still ambiguous
- the workspace references separate frontend/backend repositories or services, but only one side is currently available
- the user asks for a complete product PRD, but the currently available evidence only supports a partial code-only view

When needed, ask whether the user wants to:

- provide a frontend URL
- provide the paired frontend or backend repository path
- identify which project or project combination should define the PRD scope
- or explicitly continue with `先基于当前仓库生成`

## Workflow

### 0. Scope first

Inspect the workspace before writing any `docs/prd/` output.

Check:

- whether this looks like frontend-only, backend-only, full-stack, multi-project, or unclear
- whether a complete PRD would require another repository or a running frontend URL
- whether multiple candidate projects exist and which ones are relevant to the requested product scope
- whether the user has already allowed partial-evidence generation

If evidence is incomplete, stop and ask the user before creating PRD files.

### 1. Collect repository evidence directly

Do not use extraction scripts or require intermediate JSON.

Build a coverage-first evidence set directly from:

- repository structure and candidate app boundaries
- frontend routes, menus, breadcrumbs, page titles, i18n labels, modal titles, and form schemas
- page directories, table columns, filters, actions, tabs, and empty states
- backend routes, controllers, services, facades, managers, validators, processors, entities, enums, schedulers, listeners, queues, and integrations
- README, `docs/`, migration notes, and business-facing documents

For code-only generation, identify all candidate modules and important pages before writing product prose. Do not silently drop low-confidence modules; mark them as pending confirmation or initialization-incomplete.

### 2. Collect live frontend evidence when a URL is provided

When the user explicitly provides a running frontend URL:

1. prefer interactive browser tools if available in the current Claude Code session
2. capture all visible leaf menu items first
3. record page titles, breadcrumbs, routes, and entry paths
4. deeply capture each opened page:
   - filters
   - columns
   - metrics
   - actions and bulk actions
   - dialogs and form fields
   - visible statuses
   - helper text and empty states
5. record runtime requests whenever possible
6. trace important requests back to backend routes and supporting logic

If interactive browser tools are unavailable, say so explicitly and fall back to source-only evidence rather than inventing UI facts.

### 3. Synthesize evidence in-session

Organize the evidence directly in the conversation:

- module inventory
- page inventory
- key business objects
- core flows
- key states and transitions
- frontend-backend closure notes
- evidence boundaries
- assumptions and items to confirm

Every important conclusion should be attributable to one of:

- live UI
- frontend source
- backend source
- docs
- inference

### 4. Write PRD outputs directly

Write the final Markdown directly to the target output directory.

Default output directory is `docs/prd/` under the target repository unless the user asks for another location.
Default language is Chinese.

Generate:

- one AI context overview
- one main PRD
- one appendix per inferred module
- one initialization coverage check

### 5. Keep inference explicit

Follow `../../references/evidence-rules.md` strictly:

- when frontend evidence exists, prefer page facts for product surface area
- when frontend evidence exists, initialization is not complete until every visible leaf page is either deeply captured or explicitly marked as blocked
- when no frontend URL exists, make the source-only evidence boundary explicit
- for every important page, try to connect visible actions to runtime requests and then to backend route logic
- use code and docs to fill invisible rules, statuses, and constraints
- put every unsupported guess into `假设与待确认`

## Output Contract

Main PRD sections:

- 文档说明
- 产品定位
- 目标角色
- 顶层导航与信息架构
- 初始化覆盖检查
- 模块总览
- 核心业务对象
- 核心业务流程
- 关键状态与业务规则
- 关键状态机图
- 前后端闭环说明
- 页面规格索引
- 假设与待确认

Module appendix sections:

- 模块概览
- 覆盖页面
- 页面规格
- 模块业务规则
- 后端支撑索引
- 状态与流转
- 异常处理场景
- 与其他模块关系
- 待确认项

## References

- `../../references/prd-template.md`
- `../../references/evidence-rules.md`
- `../../references/stack-detection-guide.md`

## Notes

- Prefer frontend-enhanced mode whenever the user provides a valid frontend URL.
- Scope first, then coverage, then writing.
- In multi-project workspaces, do not merge unrelated products into one PRD without explicit justification.
- Keep the final write-up product-first, not file-inventory-first.
