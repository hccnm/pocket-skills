---
name: generate-prd-from-code
description: Reverse-engineer an existing repository into a business-first PRD for initialization and AI onboarding. Start by identifying what the currently opened project contains and whether the evidence is complete enough. If a paired frontend repo, paired backend repo, or running frontend URL is likely needed but missing, ask the user whether to supplement those inputs or explicitly proceed with a limited current-repo-only PRD. When a frontend URL is provided, prioritize a full live-UI crawl across all visible modules, then trace the corresponding requests and backend logic to form a frontend-backend closed loop; use code and docs as supporting evidence. Use when Codex needs to generate complete product documentation from a codebase, infer all modules from backend/frontend source, or respond to requests such as "根据代码库生成 PRD", "通过前端页面梳理功能文档", or "从现有后端/前端反推产品功能".
---

# Generate PRD from Code

## Overview

Turn an existing repository into an AI-friendly, product-first initialization pack with:

- one AI context overview
- one main PRD
- one appendix per inferred module
- one complete coverage check across visible pages or inferred modules

When the user provides a running frontend URL, prioritize the live UI as the primary product evidence:

- navigation and page hierarchy
- full visible leaf-menu coverage
- visible filters, fields, table columns, buttons, switches, tabs, and empty states
- page-level dialogs and form fields
- visible statuses and wording
- page-level flows that can be rendered as Mermaid diagrams
- network requests emitted by each page and the backend routes they map to
- backend responsibilities that explain why the page behaves that way

Use code and repository documents only to supplement:

- hidden business rules
- state names and transitions not fully visible in the UI
- background constraints that affect product behavior
- the backend logic that closes the loop between what the user sees and what the system actually does

If the user does not provide a frontend URL, do not immediately generate output blindly. First decide whether the currently opened repository is sufficient on its own. When it is not sufficient, ask the user whether to supplement the missing frontend/backend evidence or explicitly proceed with a limited current-repo-only PRD.

## Preflight Gate

Before generating any PRD files, inspect the currently opened project and classify it into one of these shapes:

- full-stack monorepo with both frontend and backend evidence
- backend-only repository
- frontend-only repository
- unclear or mixed repository

Then decide whether the requested PRD scope is under-evidenced.

You MUST pause and ask the user a concise blocking question before generating files when any of these are true:

- the workspace looks backend-only and no frontend URL or paired frontend repo has been provided
- the workspace looks frontend-only and no paired backend repo has been provided
- the workspace references separate frontend/backend repositories or services, but only one side is currently available
- the user asks for a complete product PRD, but the currently opened repository can only support a partial code-only view

When you need to ask, keep it short and action-oriented. Ask whether the user wants to:

- provide a frontend URL
- provide the paired frontend or backend repository path
- or explicitly continue with "先基于当前仓库生成"

Only proceed without extra inputs when at least one of these is true:

- the repository already contains enough evidence for the requested scope
- the user explicitly says to proceed based on the current repository first
- the user narrows the request to the currently opened repository only

If you proceed with incomplete evidence, clearly label the output as a limited current-repo-only PRD and list the missing evidence sources up front.

## Quick Start

Use code-only mode when the user does not provide a frontend URL:

```bash
python3 ../../scripts/detect_stack.py --repo /path/to/repo --pretty
python3 ../../scripts/extract_repo_facts.py --repo /path/to/repo --output /tmp/repo-facts.json
python3 ../../scripts/merge_evidence.py --facts /tmp/repo-facts.json --output-dir /path/to/repo/docs/prd --language zh
```

Use frontend-enhanced mode when the user provides a running frontend URL:

1. Run the same code-only extraction commands.
2. Open the provided URL with Chrome MCP.
3. Capture all visible leaf menu items first, not just a hand-picked subset.
4. For every visible leaf menu item:
   - record its title
   - record its breadcrumb path
   - if it can be opened, capture its route
   - if it cannot be opened or deeply captured yet, still keep it as a menu-level page stub
5. Then, continue until every visible leaf page reaches at least page-level capture, unless blocked by permissions or broken navigation.
6. For every opened page, capture:
   - filter fields
   - table columns
   - key buttons and bulk actions
   - row actions
   - dialogs and form fields
   - visible status terms
   - empty-state or helper text
   - exception-related wording and status branches
   - the page's runtime requests, especially list, detail, submit, approve, reject, assign, status-update, history, export, and import requests
7. For every captured request, trace the corresponding backend route and inspect the supporting logic:
   - controller or router method
   - direct service, facade, manager, validator, or processor call hints
   - state-machine, scheduler, listener, queue, or integration hints that change business behavior
8. Save the frontend evidence to a JSON file that matches `../../references/evidence-rules.md`.
9. Merge the frontend evidence:

```bash
python3 ../../scripts/merge_evidence.py \
  --facts /tmp/repo-facts.json \
  --frontend-evidence /tmp/frontend-evidence.json \
  --output-dir /path/to/repo/docs/prd \
  --language zh
```

## Workflow

### 0. Run the preflight gate

Inspect the currently opened repository before running generation commands.

Check:

- whether this looks like backend-only, frontend-only, full-stack, or unclear
- whether a complete PRD would require another repository or a running frontend URL
- whether the user has already given permission to continue with partial evidence

If evidence is incomplete, stop and ask the user before creating any `docs/prd/` output.

### 1. Detect the stack

Run `../../scripts/detect_stack.py` first to understand which analysis path to trust most.
Read `../../references/stack-detection-guide.md` when the repository uses multiple stacks or weak signals.

### 2. Extract repository facts

Run `../../scripts/extract_repo_facts.py` against the repository root.
The extractor is designed to capture:

- repository modules and package structure
- controllers, routers, and route definitions
- service, domain, entity, enum, scheduler, listener, and queue artifacts
- README and `docs/` evidence
- security, permission, auth, integration, and scheduling signals
- frontend source route hints when frontend code exists in the same repository

Treat the extractor output as the supporting baseline for the PRD. Do not let it drag the final document into controller or interface inventory mode.

### 3. Decide whether frontend evidence is needed

Skip browser work when the user does not provide a frontend URL, but do not assume that means generation should continue immediately.
Do not guess or invent a running frontend address.

If the repository appears backend-only or otherwise incomplete for a page-first PRD, ask the user whether to provide the missing frontend evidence or continue with a limited current-repo-only PRD.

Use Chrome MCP only when the user explicitly provides a URL and the live UI would clarify:

- page names and navigation hierarchy
- complete leaf-menu coverage
- page structure and visible fields
- page actions and bulk actions
- page dialogs and form inputs
- visible status names
- route-to-page mapping
- request-to-page mapping
- request-to-backend-route mapping
- role-specific entry points
- wording that is visible only in the UI

When frontend evidence exists, let the UI drive the structure of the PRD. Code is there to explain the invisible rules and backend responsibilities behind the page, not to dominate the output.

### 4. Merge evidence into PRD outputs

Run `../../scripts/merge_evidence.py` to generate:

- one AI context overview
- one main PRD
- one appendix per inferred module
- one initialization coverage check
- if some menus are visible but not yet deeply captured, still surface them as menu-level placeholder modules or pages, but treat them as incomplete initialization output rather than final completion

Default output directory is `docs/prd/` under the target repository unless the user asks for another location.
Default language is Chinese.

### 5. Keep inference explicit

Follow `../../references/evidence-rules.md` strictly:

- when frontend evidence exists, prefer page facts for product surface area
- when frontend evidence exists, initialization is not complete until every visible leaf page is either deeply captured or explicitly marked as blocked
- for every important page, try to connect visible actions to runtime requests and then to backend route logic
- use code and docs to fill invisible rules, statuses, and constraints
- do not let code structure replace page-first product language
- put every unsupported guess into `假设与待确认`

If no frontend URL is provided, explicitly state in the generated PRD that page interaction conclusions come from source code and naming signals instead of a live UI session.
If the user chose to continue without missing frontend/backend evidence, explicitly state that the document is a limited current-repo-only PRD.

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

- Read `../../references/prd-template.md` before changing the output structure.
- Read `../../references/evidence-rules.md` before mixing code, docs, and UI evidence.
- Read `../../references/stack-detection-guide.md` when the stack detector returns multiple plausible frameworks or weak confidence.

## Notes

- Prefer frontend-enhanced mode whenever the user provides a valid frontend URL.
- This skill is suitable as an initialization skill: it should prefer complete module coverage over small hand-picked samples.
- Keep the documentation optimized for another AI agent, but written in product language rather than technical language.
- Keep the PRD structured, page-first, and evidence-backed.
- Avoid interface-by-interface dumps in the final document.
- When states are explicit, render a Mermaid `stateDiagram-v2` instead of leaving the state flow as dense text.
- Avoid vague field descriptions. If the meaning is uncertain, mark it as pending confirmation.
- Prefer frontend source labels, i18n translations, and modal form definitions over raw English identifiers.
- Do not use generic business-purpose placeholders such as “用于推动当前页面中的业务处理动作”.
- If a real page request cannot be matched back to a stable backend route, describe the closure from the request itself rather than attaching an unrelated route.
- If the repository is unfamiliar or only partially readable, say so clearly in the generated assumptions section.
