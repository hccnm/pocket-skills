# Product-First PRD Template

Use this template when the skill needs to explain or adjust the generated output structure.
The target reader is another AI agent, so the document should optimize for business structure, page clarity, and reading order more than polished presentation.

## AI Context

Generate one lightweight overview file for agent onboarding:

1. `文档用途`
2. `一句话理解系统`
3. `建议阅读顺序`
4. `高优先级模块`
5. `初始化覆盖检查`
6. `最关键的状态流转`
7. `证据边界`

## Main PRD

1. `文档说明`
   - Explain whether the PRD was built from live UI, source-only inference, or both.
2. `产品定位`
   - Summarize the system in business language.
3. `目标角色`
   - Prefer visible UI roles and product responsibilities.
4. `顶层导航与信息架构`
   - Prefer live frontend menus, breadcrumbs, page names, or source-backed page groupings when no live UI exists.
5. `初始化覆盖检查`
   - Explain how many relevant modules or pages were found, how many were deeply captured, how many remain placeholders, and which ones are blocked by missing evidence.
6. `模块总览`
   - Summarize each business module in one or two product sentences.
7. `核心业务对象`
   - Explain orders, audits, suppliers, announcements, metrics, or other product objects.
8. `核心业务流程`
   - Use Mermaid diagrams when possible.
9. `关键状态与业务规则`
   - Prefer visible statuses and code-supported transitions.
10. `关键状态机图`
   - Convert important status transitions into Mermaid `stateDiagram-v2` when possible.
11. `前后端闭环说明`
   - Summarize how visible pages, runtime requests, source logic, and backend behavior connect into complete product behavior.
12. `页面规格索引`
   - Tell the agent which page specs exist and where to look first.
13. `假设与待确认`
   - Put every unsupported guess here.

## Module Appendix

1. `模块概览`
2. `覆盖页面`
3. `页面规格`
   - `页面目标`
   - `页面入口`
   - `目标角色`
   - `页面组成`
   - `筛选字段定义`
   - `关键指标`
   - `列表字段定义`
   - `核心操作`
   - `关键弹窗或表单`
   - `可见状态`
   - `页面流程图`
   - `前后端闭环说明`
   - `前后端闭环表`
4. `模块业务规则`
5. `后端支撑索引`
6. `状态与流转`
   - include `状态机图`
7. `异常处理场景`
8. `与其他模块关系`
9. `待确认项`

## Output Rules

- Write one AI context file, one main PRD, and one appendix per inferred module.
- Default output directory to `docs/prd/`.
- Default language to Chinese unless the user asks otherwise.
- If a frontend URL is provided, prefer page evidence over code structure in the final write-up.
- If a frontend URL is provided, prefer full visible-menu coverage over a hand-picked subset of pages.
- Use runtime requests and matched backend routes to explain product闭环, but keep the wording product-first rather than technical.
- If no frontend URL is provided, explicitly say the UI layer was inferred from source code and route naming.
- In multi-project workspaces, explicitly state which project or project combination defines the PRD scope.
- Do not turn the final document into an API list or controller inventory.
- Avoid generic field descriptions such as “用于支持展示或处理判断”.
- Avoid generic action purposes such as “用于推动当前页面中的业务处理动作”.
- Prefer readable Chinese labels from frontend source and i18n. Only show raw English identifiers when absolutely necessary, and mark inferred rewrites clearly.
- If a flow cannot be confidently reconstructed, write `待补充` instead of generating a meaningless generic Mermaid flow.
- If a field meaning is uncertain, say it is pending confirmation instead of fabricating a vague explanation.
- If a module or page was discovered but still lacks enough evidence, keep it visible in the coverage check or appendix and mark the gap explicitly.
