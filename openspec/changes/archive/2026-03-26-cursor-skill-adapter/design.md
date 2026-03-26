## 背景

当前 `platforms/cursor/` 目录仅有计划文档，缺少实际可用的 skill 实现。Claude Code adapter (`platforms/claude-code/generate-prd-from-code/SKILL.md`) 已有完整实现，可作为主要参考。

Cursor IDE 使用 `.cursorrules` 文件作为项目规则入口，格式为 Markdown 文档。需要创建适配 Cursor 的规则文件，复用 `core/` 目录下的共享脚本。

## 目标与边界

**目标：**
- 创建 Cursor 可识别的 `.cursorrules` 文件
- 复用 `core/scripts/` 下的 Python 脚本进行代码分析
- 保持与 Claude Code adapter 相同的 PRD 输出格式
- 支持前端 URL 增强模式和纯代码模式两种工作流

**边界（不涉及）：**
- 不修改 `core/` 目录下的共享脚本
- 不改变现有的 PRD 输出契约
- 不创建新的分析能力，仅做平台适配

## 技术决策

### 1. 文件格式选择

**决策**: 使用 `.cursorrules` 文件 + `SKILL.md` 文档组合

**理由**:
- `.cursorrules` 是 Cursor 官方推荐的项目规则格式
- `SKILL.md` 提供完整的 skill 文档，便于理解和维护
- 与 Claude Code adapter 结构保持一致

**替代方案**: 仅使用 `.cursorrules`
- 放弃原因: 缺少完整文档，不利于维护

### 2. 脚本调用方式

**决策**: 使用相对路径调用 `../../core/scripts/` 下的 Python 脚本

**理由**:
- Cursor 支持在规则中定义 Shell 命令
- 相对路径确保跨项目可移植性
- 与 Claude Code adapter 保持一致

### 3. 前端证据采集

**决策**: 在规则中引导用户使用浏览器工具采集前端证据

**理由**:
- Cursor 支持浏览器工具调用
- 前端优先的工作流能生成更准确的产品文档
- 与 Claude Code adapter 的 `frontend-enhanced mode` 一致

## 风险与权衡

| 风险 | 缓解措施 |
|------|----------|
| Cursor 规则格式限制 | 保持 Markdown 格式，避免复杂结构 |
| 相对路径跨平台问题 | 使用正斜杠路径，测试 macOS/Linux/Windows 兼容性 |
| Python 环境依赖 | 在 SKILL.md 中明确 Python 3.8+ 要求 |

## 迁移计划

无需迁移，这是新增功能。

## 待解决问题

无。