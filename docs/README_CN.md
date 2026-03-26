# Pocket Skills

[English](../README.md) | 中文

一套精心策划的 AI 友好技能集合，用于代码分析、文档生成等场景。每个技能都是自包含的，并提供了 Claude Code、Cursor、Codex、Gemini CLI 等 AI 编码助手的平台适配器。

## 为什么选择 Pocket Skills？

- **自包含**：每个技能都包含自己的脚本、参考文档和平台适配器
- **多平台**：支持 Claude Code、Cursor、Codex 和 Gemini CLI
- **易于安装**：交互式安装器，支持复选框选择
- **可验证输出**：技能产生结构化、可验证的输出结果

## 可用技能

| 技能 | 描述 |
|------|------|
| [generate-prd-from-code](../skills/generate-prd-from-code/SKILL.md) | 从代码库逆向工程，生成业务导向的 PRD（产品需求文档） |

## 仓库结构

```text
pocket-skills/
├── skills/                    # 所有技能集合
│   └── generate-prd-from-code/
│       ├── SKILL.md           # 主入口（通用版本）
│       ├── references/        # 模板和规则
│       ├── scripts/           # Python 提取脚本
│       └── platforms/         # 平台适配器
│           ├── claude-code/
│           ├── cursor/
│           ├── codex/
│           └── gemini-code/
├── install.py                 # 交互式安装器
├── install.sh                 # macOS/Linux 启动脚本
├── install.bat                # Windows 启动脚本
└── docs/                      # 文档
```

## 安装

### 系统要求

- Python 3.8+
- 可选：[questionary](https://github.com/tmbo/questionary) 用于增强交互体验

### 交互式安装

运行安装器：

```bash
# macOS/Linux
./install.sh

# Windows
install.bat

# 或直接使用 Python
python3 install.py
```

安装器将：
1. 显示主菜单，选择 **安装** 或 **卸载**
2. 通过复选框界面展示可用技能
3. 让您选择目标工具（Claude Code、Cursor、Codex、Gemini CLI 或全部）
4. 确认后执行安装

### 命令行选项

用于非交互式或脚本化使用：

```bash
# 安装特定技能
python3 install.py --skills generate-prd-from-code --tools claude-code

# 安装多个技能
python3 install.py --skills skill1,skill2 --tools claude-code,cursor,codex

# 安装所有技能到所有工具
python3 install.py --skills all --tools all

# 跳过确认提示
python3 install.py --skills generate-prd-from-code --tools all --yes

# 卸载技能
python3 install.py --uninstall --skills generate-prd-from-code --tools claude-code

# 从所有工具卸载所有技能
python3 install.py --uninstall --skills all --tools all --yes

# 显示帮助
python3 install.py --help
```

### 参数说明

| 参数 | 描述 |
|------|------|
| `--skills` | 逗号分隔的技能列表，或 `all` 表示全部 |
| `--tools` | 目标工具：`claude-code`、`cursor`、`codex`、`gemini-code` 或 `all` |
| `--uninstall` | 切换到卸载模式 |
| `--yes`, `-y` | 跳过确认提示 |

### 增强交互模式

如需最佳交互体验（空格切换、方向键导航的复选框选择），请安装 questionary：

```bash
pip install questionary
```

未安装 questionary 时，安装器会回退到简单的数字选择模式。

## 卸载

移除已安装的技能：

```bash
# 交互式卸载
python3 install.py --uninstall

# 非交互式卸载
python3 install.py --uninstall --skills generate-prd-from-code --tools claude-code --yes
```

## 快速开始

### 在 Claude Code 中使用

安装后，在您的项目中使用该技能：

```
/generate-prd-from-code
```

### 手动使用

```bash
# 进入技能目录
cd skills/generate-prd-from-code

# 直接运行脚本
python3 scripts/detect_stack.py --repo /path/to/your/repo --pretty
python3 scripts/extract_repo_facts.py --repo /path/to/your/repo --output /tmp/repo-facts.json
python3 scripts/merge_evidence.py --facts /tmp/repo-facts.json --output-dir /path/to/your/repo/docs/prd --language zh
```

### 在 Cursor 中使用

```bash
cd skills/generate-prd-from-code/platforms/cursor
# 将 .cursorrules 复制到您的项目根目录
```

### 在 Codex 中使用

安装后，技能位于 `~/.codex/skills/generate-prd-from-code/`。

### 在 Gemini CLI 中使用

安装器会创建：

- 全局命令：`~/.gemini/commands/generate-prd-from-code.toml`
- 支持文件：`~/.gemini/pocket-skills/generate-prd-from-code/`

当您需要仓库范围的工作流时，Gemini CLI 也支持在 `.gemini/commands/` 中创建项目级自定义命令。

## 添加新技能

添加新技能的步骤：

1. 在 `skills/` 下创建以技能名称命名的目录（使用 kebab-case 命名法）
2. 添加包含 frontmatter 和说明的 `SKILL.md` 文件
3. 添加 `scripts/` 目录存放自动化脚本
4. 添加 `references/` 目录存放模板和规则
5. 添加 `platforms/` 目录存放平台特定适配器

安装器会自动发现 `skills/` 目录下的任何新技能。

## 贡献

欢迎贡献！详情请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md)。

## 许可证

MIT 许可证 - 详情请参阅 [LICENSE](../LICENSE)。