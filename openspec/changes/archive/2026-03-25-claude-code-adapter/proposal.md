## Why

这是一个 **从代码生成 PRD** 的技能项目,但 **Claude Code 适配器尚未实现**。目前只有 Codex 适配器完成,而 Claude Code 适配器只有占位符 README。

Claude Code 是 Anthropic 的官方 CLI 工具,这个项目应该首先支持它。实现适配器将使 Claude Code 用户能够直接使用此技能从代码库生成产品文档。

## What Changes

- 创建 `platforms/claude-code/generate-prd-from-code/SKILL.md` - Claude Code 技能定义文件
- 技能将引用 `core/scripts/` 中的共享提取脚本
- 技能将遵循 `core/references/` 中的模板和规则
- 保持与 Codex 适配器相同的产品优先输出原则

## Capabilities

### New Capabilities
- `claude-code-skill`: Claude Code 平台的 PRD 生成技能,支持从代码库或前端 URL 生成产品优先的 PRD 文档

### Modified Capabilities
<!-- 无现有能力需要修改 -->

## Impact

- `platforms/claude-code/generate-prd-from-code/SKILL.md`: 新增文件
- 引用 `core/scripts/`: detect_stack.py, extract_repo_facts.py, merge_evidence.py
- 引用 `core/references/`: prd-template.md, evidence-rules.md, stack-detection-guide.md