## ADDED Requirements

### Requirement: 命令行 skills 参数

系统 SHALL 支持 `--skills` 命令行参数指定要安装/卸载的 skills。

#### Scenario: 指定单个 skill
- **WHEN** 用户运行 `install.py --skills generate-prd-from-code`
- **THEN** 系统跳过交互式 skill 选择，直接安装指定的 skill

#### Scenario: 指定多个 skills
- **WHEN** 用户运行 `install.py --skills skill1,skill2,skill3`
- **THEN** 系统安装所有指定的 skills

#### Scenario: 安装所有 skills
- **WHEN** 用户运行 `install.py --skills all`
- **THEN** 系统安装所有可用的 skills

#### Scenario: 无效 skill 名称
- **WHEN** 用户指定的 skill 名称不存在
- **THEN** 系统显示错误信息并列出可用的 skills

### Requirement: 命令行 tools 参数

系统 SHALL 支持 `--tools` 命令行参数指定目标工具。

#### Scenario: 指定单个工具
- **WHEN** 用户运行 `install.py --tools claude-code`
- **THEN** 系统仅操作 Claude Code

#### Scenario: 指定多个工具
- **WHEN** 用户运行 `install.py --tools claude-code,cursor`
- **THEN** 系统操作指定的所有工具

#### Scenario: 操作所有工具
- **WHEN** 用户运行 `install.py --tools all`
- **THEN** 系统操作所有支持的工具

### Requirement: 命令行 uninstall 参数

系统 SHALL 支持 `--uninstall` 参数进入卸载模式。

#### Scenario: 交互式卸载
- **WHEN** 用户运行 `install.py --uninstall`
- **THEN** 系统进入卸载流程，引导用户选择工具和 skills

#### Scenario: 非交互式卸载
- **WHEN** 用户运行 `install.py --uninstall --skills skill1,skill2 --tools claude-code`
- **THEN** 系统直接卸载指定的 skills，无需交互

#### Scenario: 卸载所有 skills
- **WHEN** 用户运行 `install.py --uninstall --skills all --tools all`
- **THEN** 系统卸载所有工具下的所有 skills

### Requirement: 命令行帮助信息

系统 SHALL 提供 `--help` 参数显示使用说明。

#### Scenario: 显示帮助
- **WHEN** 用户运行 `install.py --help`
- **THEN** 系统显示所有可用参数及其说明，包括安装和卸载示例

### Requirement: 非交互模式

系统 SHALL 在参数完整时自动进入非交互模式。

#### Scenario: 完全非交互安装
- **WHEN** 用户运行 `install.py --skills skill1 --tools claude-code`
- **THEN** 系统无需用户交互直接完成安装

#### Scenario: 完全非交互卸载
- **WHEN** 用户运行 `install.py --uninstall --skills skill1 --tools claude-code`
- **THEN** 系统无需用户交互直接完成卸载