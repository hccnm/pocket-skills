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
2. `代码事实`
   - status enums, services, validators, schedulers, listeners, queues
   - controller/router methods and their service or facade call hints
   - code names that explain invisible business rules
3. `文档事实`
   - README, `docs/`, internal product notes, migration notes
4. `推断`
   - anything not directly supported by the sources above

### If no frontend URL is provided

1. `代码事实`
2. `文档事实`
3. `推断`

## Required Behavior

- When frontend evidence exists, let pages drive the final PRD structure.
- Treat this skill as an initialization workflow: full visible-module coverage is the default target.
- Do not silently drop visible leaf menu items just because they were not deeply captured.
- For menu items that are visible but not yet opened, keep a menu-level placeholder record so the final PRD reflects full module coverage.
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
- Do not dump interfaces, controllers, paths, or file references into the final product正文 unless the user explicitly asks for technical documentation.
- If a field meaning is unclear, avoid generic filler text. Mark it as `待确认` or infer conservatively from nearby labels and business context.
- If a page has real request evidence but route matching is weak, describe the闭环 using the real request first. Do not fall back to an unrelated module route just to fill the table.
- When a module has explicit states or transitions, prefer rendering a visual state machine rather than leaving status flow as long plain text.
- If a module contains visible exception states such as `信息错误`, `已挂起`, or `待审核`, summarize the exception handling scenario in product language.
- If a page is visible but still lacks request evidence, explicitly mark the page as initialization-incomplete rather than pretending the loop is closed.

## No Frontend URL Case

If the user does not provide a frontend URL:

- do not guess a running URL
- do not block on browser access
- do not downgrade the task to "analysis only"
- continue with code-only PRD generation

Add a note in the generated PRD:

`本次未接入运行中前端页面，页面交互类结论主要来自源码与接口命名。`

## Frontend Evidence JSON Shape

When Chrome MCP is used, save the captured facts in a JSON object like this:

```json
{
  "base_url": "http://example.local:3000/",
  "captured_at": "2026-03-24T08:30:00Z",
  "pages": [
    {
      "title": "订单仪表盘",
      "route": "#/Dashboard/OrderDashboard",
      "breadcrumbs": ["仪表盘", "订单仪表盘"],
      "module_hint": "dashboard",
      "capture_status": "full",
      "filters": [
        { "name": "开始日期", "type": "date" },
        { "name": "结束日期", "type": "date" }
      ],
      "metrics": [
        { "name": "今日订单提交数" },
        { "name": "今日处理总数" }
      ],
      "charts": [
        { "name": "订单库存表" },
        { "name": "订单状态分布表" }
      ],
      "actions": [
        { "name": "搜索" },
        { "name": "重置" }
      ],
      "statuses": ["待处理", "配送中", "配送完成"],
      "dialogs": [],
      "empty_state": "",
      "network_refs": ["dashboard-statistics"]
    }
  ],
  "menus": [
    {
      "title": "仪表盘",
      "children": ["订单仪表盘", "数据表"]
    }
  ],
  "network_requests": [
    {
      "id": "dashboard-statistics",
      "method": "GET",
      "url": "http://example.local/api/statistics/dashboard/statistics",
      "page_title": "订单仪表盘"
    }
  ]
}
```

Keep this file factual and compact. Do not pre-write PRD language into the JSON.
Use page terms as they appear on screen. If a field meaning is unknown, leave `purpose` empty and let the generator infer conservatively.
Use `capture_status: "menu_only"` for pages that are visible in the menu but not yet deeply captured.
Try to record at least one runtime request per opened page. For pages with submit, approve, assign, status, or export actions, prefer recording those requests over only recording the menu request.
