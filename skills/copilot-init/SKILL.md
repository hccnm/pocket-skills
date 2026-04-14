---
name: copilot-init
description: 在目标仓库中初始化 pocket-copilot 工作流目录，安全创建 rules、knowledge、agents、changes/templates、archives，并基于仓库现状预填上下文与基础模板。适用于要开始使用渐进式 Spec 工作流的项目。
---

# Pocket Copilot Init

## Overview

在当前打开的目标仓库根目录初始化 `pocket-copilot/` 工作流骨架，并预填一版可直接使用的上下文与模板。

这个 skill 只负责初始化，不负责创建具体需求变更，也不会自动进入 propose 或 apply。

固定输出目录：

```text
pocket-copilot/
├── rules/
│   ├── project-context.md
│   ├── coding-style.md
│   ├── security.md
│   └── domain-rules.md
├── knowledge/
│   └── index.md
├── agents/
│   ├── copilot-prompt.md
│   ├── spec-reviewer.md
│   └── code-quality-reviewer.md
├── changes/
│   └── templates/
│       ├── spec.md
│       ├── tasks.md
│       ├── test-spec.md
│       └── log.md
└── archives/
```

## Core Rules

- 默认中文输出。
- 幂等执行，默认安全合并。
- 已存在文件不覆盖，只补缺失项。
- 所有预填内容都必须区分：
  - 仓库证据
  - 模板默认值
  - 待人工补充项
- 不要编造不存在的技术栈、分层、领域规则或安全要求。
- 如果仓库信息不足，明确标记“待补充”，不要假装已经确认。

## Workflow

### 1. Preflight

在写入任何文件前，先扫描当前仓库：

- `README*`
- `docs/`
- 构建与清单文件，例如 `package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml`、`pom.xml`、`build.gradle`
- 顶层源码、脚本、配置、测试目录

判断当前仓库大致属于：

- frontend
- backend
- full-stack
- unclear

### 2. Create directories safely

创建缺失目录，但不要删除任何现有目录：

- `pocket-copilot/rules`
- `pocket-copilot/knowledge`
- `pocket-copilot/agents`
- `pocket-copilot/changes/templates`
- `pocket-copilot/archives`

### 3. Generate missing files only

仅为缺失文件写入模板，不覆盖用户已有内容。

模板来源：

- `references/project-context-template.md`
- `references/coding-style-template.md`
- `references/security-template.md`
- `references/domain-rules-template.md`
- `references/knowledge-index-template.md`
- `references/copilot-prompt-template.md`
- `references/spec-reviewer-template.md`
- `references/code-quality-reviewer-template.md`
- `references/change-spec-template.md`
- `references/change-tasks-template.md`
- `references/change-test-spec-template.md`
- `references/change-log-template.md`

### 4. Prefill carefully

对新生成的文件做谨慎预填：

- `project-context.md`
  - 项目类型
  - 技术栈
  - 构建方式
  - 主要模块或目录
  - 关键依赖触点
- `coding-style.md`
  - 仅记录仓库中能观察到的命名、目录组织、测试风格、约定
  - 不确定处写“待补充”
- `security.md`
  - 写通用底线
  - 项目特有风险写“待补充”
- `domain-rules.md`
  - 只记录能从仓库或文档中看出的规则
  - 没证据就留空位

其余模板保持通用版本即可。

### 5. Final report

结束时用结构化摘要报告：

- `created`
- `skipped`
- `needs-manual-review`

并给出下一步建议：

- 使用 `pocket-copilot-propose` 创建首个 change

## Output Requirements

初始化完成后，至少要满足：

- `pocket-copilot/` 目录完整存在
- `rules/`、`knowledge/`、`agents/`、`changes/templates/`、`archives/` 结构齐全
- 关键文件可直接作为后续 workflow 输入
- 没有覆盖已有内容

## Notes

- 如果目标仓库里已经存在 `pocket-copilot/`，继续采用安全合并策略。
- 如果某些文件已存在但显然与模板差异较大，不覆盖，只在最终摘要中提示人工检查。
- 不要顺手创建具体 change 目录，初始化阶段只创建模板和基础上下文。
