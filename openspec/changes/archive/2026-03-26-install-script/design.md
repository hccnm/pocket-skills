## Context

当前 `generate-prd-from-code-skill` 项目包含以下可安装内容：

| 组件 | 位置 | 安装目标 |
|------|------|----------|
| Claude Code skill | `platforms/claude-code/generate-prd-from-code/` | `~/.claude/skills/` |
| Cursor skill | `platforms/cursor/generate-prd-from-code/` | `~/.cursor/skills/` 或 `.cursor/skills/` |
| 共享脚本 | `core/scripts/` | 随 skill 引用 |
| 参考文档 | `core/references/` | 随 skill 引用 |

用户需要一种简便的方式将这些内容安装到各自的 AI 工具中。

## Goals / Non-Goals

**Goals:**
- 提供单一入口的交互式安装脚本
- 支持 Claude Code 和 Cursor 两个平台
- 支持 Windows 和 macOS 操作系统
- 支持安装（首次）和更新（已有安装）两种模式
- 自动检测操作系统并适配路径分隔符
- 显示清晰的操作结果和状态

**Non-Goals:**
- 不支持 Linux（可后续添加）
- 不处理 Python 环境安装（假设用户已有 Python 3.8+）
- 不实现卸载功能（可后续添加）
- 不处理多版本管理

## Decisions

### 1. 脚本语言选择

**决策**: 使用 Python

**理由**:
- Python 3.8+ 是 skill 运行的前置条件，用户必然已安装
- 跨平台一致性优于 Shell/Bash
- 内置 `input()` 支持交互，无需额外依赖
- 可复用 `core/scripts/` 的设计模式

**替代方案**: Shell + PowerShell
- 放弃原因: 需要维护两套脚本，测试成本高

### 2. 安装模式

**决策**: 检测已有安装，自动判断安装/更新

**流程**:
1. 检测目标路径是否已存在 skill
2. 存在 → 询问是否更新（覆盖）
3. 不存在 → 执行安装（复制文件）

**理由**:
- 简化用户操作，无需区分模式
- 避免误覆盖，需要用户确认

### 3. 目标路径策略

**决策**: 默认安装到用户级全局目录

| 工具 | 安装路径 |
|------|----------|
| Claude Code | `~/.claude/skills/generate-prd-from-code/` |
| Cursor | `~/.cursor/skills/generate-prd-from-code/` |

**理由**:
- 全局可用，无需每个项目重复安装
- 符合各工具官方推荐路径

**替代方案**: 项目级安装
- 放弃原因: 需要用户指定项目路径，增加交互复杂度

### 4. 文件复制策略

**决策**: 每个技能目录包含完整的共享资源，实现自包含安装

**安装后目录结构**:
```
~/.claude/skills/generate-prd-from-code/
├── SKILL.md
└── core/
    ├── scripts/
    │   ├── detect_stack.py
    │   ├── extract_repo_facts.py
    │   ├── extract_frontend_source_evidence.py
    │   └── merge_evidence.py
    └── references/
        ├── prd-template.md
        ├── evidence-rules.md
        └── stack-detection-guide.md

~/.cursor/skills/generate-prd-from-code/
├── SKILL.md
└── core/
    ├── scripts/
    └── references/
```

**理由**:
- 每个 skill 完全独立，无外部依赖
- SKILL.md 中的路径改为 `./core/` 相对路径
- 安装/更新/删除都是单一目录操作
- 避免污染用户主目录

**路径替换**: 安装时将 SKILL.md 中的 `../../core/` 替换为 `./core/`

### 5. 交互流程设计

```
Generate PRD from Code - 安装向导

检测到操作系统: macOS

请选择要安装的工具:
  [1] Claude Code
  [2] Cursor
  [3] 全部安装

请输入选择 (1-3): 3

即将安装到以下位置:
  - Claude Code: ~/.claude/skills/generate-prd-from-code/
  - Cursor: ~/.cursor/skills/generate-prd-from-code/

是否继续? (y/n): y

正在安装...
  ✓ 安装 Claude Code skill
    - 复制 SKILL.md
    - 复制 core/scripts/
    - 复制 core/references/
  ✓ 安装 Cursor skill
    - 复制 SKILL.md
    - 复制 core/scripts/
    - 复制 core/references/

安装完成!

使用方法:
  Claude Code: 在项目中使用 /generate-prd-from-code
  Cursor: 在 Chat 中使用 /generate-prd-from-code
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| Windows 路径分隔符问题 | 使用 `pathlib.Path` 处理路径，避免硬编码分隔符 |
| 已有安装被覆盖 | 更新前显示 diff 摘要或要求二次确认 |
| 用户主目录权限问题 | 捕获异常，提示用户手动安装 |
| Python 版本不兼容 | 在脚本开头检查 Python 版本，给出明确提示 |