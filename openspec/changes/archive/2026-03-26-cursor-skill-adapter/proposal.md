## 背景

Cursor 平台目前缺少 `generate-prd-from-code` skill 的完整实现。虽然 `platforms/cursor/README.md` 已定义了适配器需求和预期形状，但缺少实际可用的 skill 文件。用户无法在 Cursor IDE 中使用此功能从代码库生成 PRD 文档。

## 变更内容

- 新建 `platforms/cursor/generate-prd-from-code/.cursorrules` 文件，作为 Cursor 的规则入口
- 新建 `platforms/cursor/generate-prd-from-code/SKILL.md` 文件，提供 skill 的完整说明文档
- 确保复用 `../../core/` 目录下的共享脚本和参考文档
- 保持与 Claude Code adapter 相同的输出契约（AI context overview + main PRD + module appendices）

## 能力

### 新增能力

- `cursor-rules-generation`: Cursor 规则文件生成能力，支持在 `.cursorrules` 格式中定义从代码生成 PRD 的完整工作流

### 修改能力

无现有 capability 需要修改。

## 影响范围

- 新增文件：`platforms/cursor/generate-prd-from-code/.cursorrules`
- 新增文件：`platforms/cursor/generate-prd-from-code/SKILL.md`
- 依赖共享引擎：`core/scripts/` 下的 Python 脚本
- 依赖参考文档：`core/references/` 下的规则和模板文档