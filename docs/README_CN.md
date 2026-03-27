# Pocket Skills

[English](../README.md) | 中文

一套精心策划的 AI 友好技能集合，用于代码分析、文档生成等场景。每个技能都是自包含的，并提供了 Claude Code、Cursor、Codex、Gemini CLI 等平台的适配器。

## 为什么选择 Pocket Skills？

- **自包含** — 每个技能自带脚本、参考文档和平台适配器
- **多平台** — 支持 Claude Code、Cursor、Codex 和 Gemini CLI
- **一键安装** — 交互式安装器，复选框选择
- **可验证输出** — 技能产生结构化、可验证的输出结果

## 可用技能

### [generate-prd-from-code](../skills/generate-prd-from-code/SKILL.md)

从代码库逆向工程，生成业务导向的 PRD（产品需求文档）。支持两种模式：

- **纯代码模式** — 分析仓库结构、路由、服务和实体，推断产品范围
- **前端增强模式** — 爬取线上 UI 捕获页面、字段和流程，再追溯到后端逻辑，形成完整的前后端闭环

输出：AI 上下文概览 + 主 PRD + 各模块附录 + 覆盖检查清单。

### [project-md-reconstructor](../skills/project-md-reconstructor/SKILL.md)

复现 OpenSpec 的 `project.md` 工作流 — 扫描现有仓库，生成一个复用感知的 `docs/project.md`，涵盖技术栈、编码规范、架构模式、约束条件和可复用构建块。

## 快速开始

### 1. 安装

```bash
# macOS / Linux
./install.sh

# Windows
install.bat

# 或直接使用 Python
python3 install.py
```

### 2. 在 Claude Code 中使用

```bash
# 从当前项目生成 PRD
/pocket-generate-prd-from-code

# 从当前项目生成 docs/project.md
/pocket-project-md-reconstructor
```

### 3. 在 Cursor 中使用

将技能平台适配器中的 `.cursorrules` 复制到项目根目录：

```bash
cp skills/generate-prd-from-code/platforms/cursor/.cursorrules /path/to/your/project/
```

### 4. 在 Codex / Gemini CLI 中使用

安装后，技能位于：
- Codex：`~/.codex/skills/pocket-<skill-name>/`
- Gemini CLI：`~/.gemini/commands/pocket-<skill-name>.toml`

## 安装

### 系统要求

- Python 3.8+
- [questionary](https://github.com/tmbo/questionary) 用于交互模式

### 交互式安装

安装器引导你完成：

1. 选择 **安装** 或 **卸载**
2. 复选框选择技能（空格切换，回车确认）
3. 复选框选择目标工具
4. 确认并执行

```bash
pip install questionary   # 交互模式依赖
```

### 命令行模式

```bash
# 安装指定技能到指定工具
python3 install.py --skills generate-prd-from-code --tools claude-code

# 安装所有技能到所有工具
python3 install.py --skills all --tools all

# 跳过确认提示
python3 install.py --skills generate-prd-from-code --tools all --yes

# 卸载
python3 install.py --uninstall --skills all --tools all --yes

# 查看帮助
python3 install.py --help
```

| 参数 | 描述 |
|------|------|
| `--skills` | 逗号分隔的技能名称，或 `all` |
| `--tools` | `claude-code`、`cursor`、`codex`、`gemini-code` 或 `all` |
| `--uninstall` | 切换到卸载模式 |
| `--yes`, `-y` | 跳过确认提示 |

## 手动使用

也可以不通过安装器，直接运行脚本：

```bash
cd skills/generate-prd-from-code

# 检测技术栈
python3 scripts/detect_stack.py --repo /path/to/your/repo --pretty

# 提取仓库信息
python3 scripts/extract_repo_facts.py --repo /path/to/your/repo --output /tmp/repo-facts.json

# 合并证据生成 PRD
python3 scripts/merge_evidence.py --facts /tmp/repo-facts.json --output-dir /path/to/your/repo/docs/prd --language zh
```

## 仓库结构

```text
pocket-skills/
├── skills/                          # 技能集合
│   ├── generate-prd-from-code/
│   │   ├── SKILL.md                 # 技能定义
│   │   ├── references/              # 模板与规则
│   │   ├── scripts/                 # Python 脚本
│   │   └── platforms/               # 平台适配器
│   │       ├── claude-code/
│   │       ├── cursor/
│   │       ├── codex/
│   │       └── gemini-code/
│   └── project-md-reconstructor/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── platforms/
├── install.py                       # 安装器
├── install.sh / install.bat         # 启动脚本
└── docs/                            # 文档
```

## 添加新技能

1. 在 `skills/` 下创建目录（使用 kebab-case 命名）
2. 添加带 YAML frontmatter 的 `SKILL.md`
3. 按需添加 `scripts/`、`references/`、`platforms/`
4. 安装器会自动发现新技能

## 贡献

欢迎贡献！详情请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 许可证

MIT 许可证 - 详情请参阅 [LICENSE](../LICENSE)。
