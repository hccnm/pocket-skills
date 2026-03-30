---
name: generate-prd-from-code
description: Reverse-engineer an existing repository into a business-first PRD for initialization and AI onboarding using native repository exploration and browser MCP evidence when available. If a paired frontend repo, paired backend repo, or running frontend URL is likely needed but missing, ask the user whether to supplement those inputs or explicitly proceed with a limited current-repo-only PRD. Use when you need to generate complete product documentation from a codebase, infer modules from frontend/backend source, or respond to requests such as "根据代码库生成 PRD", "通过前端页面梳理功能文档", or "从现有后端/前端反推产品功能".
---

# Generate PRD from Code

## Overview

Turn the available evidence into an AI-friendly, product-first initialization pack with:

- one AI context overview
- one main PRD
- one appendix per inferred module
- one initialization coverage check

The workflow is agent-native:

- explore repository structure directly
- read code, docs, routes, menus, forms, and states directly
- use browser or Chrome MCP only when the user provides a running frontend URL
- write final Markdown directly without relying on intermediate JSON or external extraction scripts

When live frontend evidence exists, treat visible pages as the primary product surface:

- navigation and page hierarchy
- complete visible leaf-menu coverage
- filters, fields, table columns, buttons, tabs, and empty states
- dialogs, drawers, and form fields
- visible statuses, wording, and exception branches
- runtime requests emitted by the page
- backend responsibilities that explain page behavior

When no frontend URL is provided, rely on frontend source, backend source, and docs. In that mode, the generated PRD MUST explicitly state that page interaction conclusions come from source code and naming signals rather than a live UI session.

## Preflight Gate

Before generating any PRD files, inspect the current workspace and classify the evidence shape:

- single full-stack repository
- frontend-only repository
- backend-only repository
- multi-project workspace with several candidate frontend/backend projects
- unclear or mixed workspace

Then decide whether the requested PRD scope is under-evidenced.

You MUST pause and ask the user a concise blocking question before generating files when any of these are true:

- the workspace looks backend-only and no frontend URL or paired frontend repo has been provided
- the workspace looks frontend-only and no paired backend repo has been provided
- the workspace contains multiple candidate projects, but the target product scope is still ambiguous
- the workspace references separate frontend/backend repositories or services, but only one side is currently available
- the user asks for a complete product PRD, but the currently available evidence only supports a partial code-only view

When you need to ask, keep it short and action-oriented. Ask whether the user wants to:

- provide a frontend URL
- provide the paired frontend or backend repository path
- identify which project or project combination should define the PRD scope
- or explicitly continue with `先基于当前仓库生成`

Only proceed without extra inputs when at least one of these is true:

- the repository already contains enough evidence for the requested scope
- the user explicitly says to proceed based on the current repository first
- the user narrows the request to the currently opened repository only

If you proceed with incomplete evidence, clearly label the output as a limited current-repo-only PRD and list the missing evidence sources up front.

## Workflow

### 0. Run the preflight gate

Inspect the current workspace before writing any `docs/prd/` output.

Check:

- whether this looks like frontend-only, backend-only, full-stack, multi-project, or unclear
- whether a complete PRD would require another repository or a running frontend URL
- whether the user has already given permission to continue with partial evidence
- whether multiple candidate projects exist and which ones are relevant to the requested product scope

If evidence is incomplete, stop and ask the user before creating PRD files.

### 1. Establish scope and candidate projects

When the workspace contains multiple projects or top-level apps:

- list the candidate frontend and backend projects
- infer each candidate's role from manifests, routes, page directories, docs, and naming
- decide which project or project combination is relevant to the requested PRD scope
- do not silently merge unrelated projects into the same PRD

When the scope is still ambiguous after exploration, ask the user to confirm the target project range before continuing.

### 2. Collect repository evidence

Do not rely on extraction scripts or intermediate JSON.
Instead, build a coverage-first evidence set directly from source and docs.

Start by building a module and page inventory before writing product prose.

Collect from source:

- repository structure and candidate application boundaries
- frontend routes, menus, breadcrumbs, page titles, i18n labels, modal titles, and form schemas
- page directories, table columns, filters, actions, tabs, and empty states
- backend routes, controllers, services, facades, managers, validators, processors, entities, enums, schedulers, listeners, queues, and integrations
- README, `docs/`, migration notes, product notes, and other business-facing documentation

For code-only generation, prefer breadth first:

- identify all candidate modules first
- identify the key pages under each module
- identify the main business objects, statuses, and processes
- record missing evidence explicitly instead of skipping modules silently

### 3. Collect frontend evidence when a URL is provided

Use browser or Chrome MCP only when the user explicitly provides a running frontend URL.
Do not guess a running address.

When live UI evidence exists:

1. capture all visible leaf menu items first, not just a hand-picked subset
2. record titles, breadcrumbs, routes, and page entry paths
3. deeply capture each opened page:
   - filters
   - columns
   - metrics
   - actions and bulk actions
   - dialogs and form fields
   - visible statuses
   - helper text and empty states
4. record runtime requests whenever possible, especially list, detail, submit, approve, reject, assign, import, export, history, and status-update requests
5. trace important requests back to backend routes and supporting logic

If some visible pages cannot be opened or fully captured, keep them as menu-level placeholders and mark them as blocked or initialization-incomplete.

### 4. Synthesize evidence in-session

Do not create `repo-facts.json`, `frontend-evidence.json`, or any other required intermediate artifact.

Instead, organize the evidence directly in the agent workflow:

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

### 5. Write PRD outputs directly

Write the final Markdown directly to the target output directory.

Default output directory is `docs/prd/` under the target repository unless the user asks for another location.
Default language is Chinese.

Generate:

- one AI context overview
- one main PRD
- one appendix per inferred module
- one initialization coverage check

### 6. Keep inference explicit

Follow `references/evidence-rules.md` strictly:

- when frontend evidence exists, prefer page facts for product surface area
- when frontend evidence exists, initialization is not complete until every visible leaf page is either deeply captured or explicitly marked as blocked
- when no frontend URL exists, make the source-only evidence boundary explicit
- for every important page, try to connect visible actions to runtime requests and then to backend route logic
- use code and docs to fill invisible rules, statuses, and constraints
- do not let code structure replace page-first product language
- put every unsupported guess into `假设与待确认`

## Output Contract

Generate an AI context overview that helps the next agent onboard quickly.

Generate a main PRD with these sections:

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

Generate each module appendix with these sections:

- 模块概览
- 覆盖页面
- 页面规格（每个关键页面至少包含页面目标、筛选字段、列表字段、核心操作、弹窗字段、可见状态、流程图、前后端闭环说明）
- 模块业务规则
- 后端支撑索引
- 状态与流转
- 异常处理场景
- 与其他模块关系
- 待确认项

## References

- Read `references/prd-template.md` before changing the output structure.
- Read `references/evidence-rules.md` before mixing code, docs, and UI evidence.
- Read `references/stack-detection-guide.md` when the workspace uses multiple stacks or the project boundaries are weak.

## Notes

- Prefer frontend-enhanced mode whenever the user provides a valid frontend URL.
- Treat this as an initialization workflow: complete relevant-module coverage is the default target.
- Scope first, then coverage, then writing. Do not write the PRD before building a module and page inventory.
- In multi-project workspaces, do not combine unrelated products into the same PRD without explicit justification.
- Keep the documentation optimized for another AI agent, but written in product language rather than technical inventory language.
- Avoid interface-by-interface dumps in the final document.
- When states are explicit, render a Mermaid `stateDiagram-v2` instead of leaving the state flow as dense text.
- Prefer readable Chinese labels from frontend source and i18n over raw identifiers.
- If a real page request cannot be matched back to a stable backend route, describe the closure from the request itself rather than attaching an unrelated route.
