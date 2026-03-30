# Evidence Rules

Use these rules whenever the skill turns source material into product language.

## Priority

### If a frontend URL is provided

1. `页面事实`
   - live menu labels
   - page titles and breadcrumbs
   - complete leaf-menu inventory
   - visible filters, columns, buttons, switches, tabs, and helper text
   - dialogs, form fields, empty states, and visible statuses
   - runtime requests emitted by the page
2. `前端源码事实`
   - routes
   - page component structure
   - i18n labels, form definitions, modal titles, and table columns
3. `后端源码事实`
   - status enums, services, validators, schedulers, listeners, queues
   - controller or router methods and their service or facade call hints
   - code names that explain invisible business rules
4. `文档事实`
   - README, `docs/`, internal product notes, migration notes
5. `推断`
   - anything not directly supported by the sources above

### If no frontend URL is provided

1. `前端源码事实`
2. `后端源码事实`
3. `文档事实`
4. `推断`

## Required Behavior

- When frontend evidence exists, let pages drive the final PRD structure.
- Treat this skill as an initialization workflow: full relevant-module coverage is the default target.
- Do not silently drop visible leaf menu items just because they were not deeply captured.
- Do not silently drop discovered source modules just because the evidence is weaker than other modules.
- Build a module and page inventory before writing product prose.
- In a multi-project workspace, first determine which project or project combination belongs to the requested PRD scope. Do not merge unrelated projects into the same document.
- For menu items that are visible but not yet opened, keep a menu-level placeholder record so the final PRD reflects full visible coverage.
- For discovered source modules that still lack enough evidence, keep a placeholder in the coverage check and mark them as `初始化未完成`, `待确认`, or `证据不足`.
- For opened pages, capture runtime requests whenever possible so the final PRD can describe a frontend-backend closed loop.
- For important requests, match them back to repository routes and summarize the backend responsibility in product language.
- Use code to explain hidden rules, transitions, or constraints that the page alone cannot show.
- Prefer code facts over docs when they conflict.
- Use docs to explain intent, terminology, and historical background that UI and code names alone cannot express.
- Never let page wording override a code fact that clearly defines the capability boundary.
- Never present a guess as confirmed product behavior.
- Prefer frontend source labels such as `title`, `label`, `placeholder`, i18n translations, and modal titles over raw variable names.
- If a field or action label is still only available as an English identifier, convert it into a readable Chinese phrase and mark it as `推断`, instead of repeating a generic fallback paragraph.
- Extract modal and drawer fields from actual `Form.Item` / `ProForm` definitions whenever frontend source is available.
- Filter out developer comments such as `说明：`, `TODO`, `FIXME`, and inline debugging notes so they never appear as product actions.
- Do not dump interfaces, controllers, paths, or file references into the final产品正文 unless the user explicitly asks for technical documentation.
- If a field meaning is unclear, avoid generic filler text. Mark it as `待确认` or infer conservatively from nearby labels and business context.
- If a page has real request evidence but route matching is weak, describe the闭环 using the real request first. Do not fall back to an unrelated module route just to fill the table.
- When a module has explicit states or transitions, prefer rendering a visual state machine rather than leaving status flow as long plain text.
- If a module contains visible exception states such as `信息错误`, `已挂起`, or `待审核`, summarize the exception handling scenario in product language.
- If a page or module is discovered but still lacks request evidence, explicitly mark it as initialization-incomplete rather than pretending the loop is closed.
- Every important conclusion should be attributable to one of `live UI`、`frontend source`、`backend source`、`docs`、`inference`.

## No Frontend URL Case

If the user does not provide a frontend URL:

- do not guess a running URL
- do not block on browser access
- do not downgrade the task to "analysis only"
- continue with source-driven PRD generation

Add a note in the generated PRD:

`本次未接入运行中前端页面，页面交互类结论主要来自源码与接口命名。`

## Coverage Check Expectations

The generated coverage check should record at least:

- how many candidate modules were discovered
- how many pages were deeply captured
- how many pages remain menu-only or source-only placeholders
- which modules or pages are blocked by missing frontend/backend evidence
- what the current source-only evidence boundary is when no live UI is available

Keep the coverage check factual and compact. Missing evidence should surface as an explicit gap, not as silent omission.
