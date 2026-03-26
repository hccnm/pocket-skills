## Context

项目已有完整的共享引擎在 `core/scripts/` 和 `core/references/`。Codex 适配器(`platforms/codex/generate-prd-from-code/SKILL.md`)是一个成熟的参考实现。

Claude Code 适配器需要创建一个类似的 SKILL.md,但针对 Claude Code 的技能格式进行适配。

## Goals / Non-Goals

**Goals:**
- 创建一个 Claude Code 可识别的 SKILL.md 文件
- 复用 `core/scripts/` 中的共享提取脚本
- 遵循与 Codex 适配器相同的产品优先输出原则

**Non-Goals:**
- 不修改 core 共享引擎
- 不创建符号链接目录结构(与 Codex 不同,Claude Code 技能文件直接放在技能目录)
- 不实现新的提取逻辑

## Decisions

### Decision 1: 技能文件位置

在 `platforms/claude-code/generate-prd-from-code/SKILL.md` 创建技能文件。

**理由:** 遵循现有项目结构,与 Codex 适配器保持一致的目录布局。

### Decision 2: 技能格式

采用 Claude Code 的 SKILL.md 格式,包含:
- YAML front matter (name, description)
- 技能说明和使用场景
- 工作流程步骤
- 输出约定
- 参考文档链接

**理由:** 这是 Claude Code 识别技能的标准格式,与项目中 `.claude/skills/` 下已有的技能格式一致。

### Decision 3: 脚本引用

技能将直接引用 `core/scripts/` 中的脚本,使用相对路径 `../../core/scripts/`。

**理由:** 避免代码重复,确保所有平台适配器使用相同的提取逻辑。