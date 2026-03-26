## ADDED Requirements

### Requirement: 已安装 skills 检测

系统 SHALL 能够检测各工具目录下已安装的 skills。

#### Scenario: 检测 Claude Code 已安装 skills
- **WHEN** 用户选择卸载 Claude Code 的 skills
- **THEN** 系统扫描 `~/.claude/skills/` 目录并返回已安装的 skill 列表

#### Scenario: 检测 Cursor 已安装 skills
- **WHEN** 用户选择卸载 Cursor 的 skills
- **THEN** 系统扫描 `~/.cursor/skills/` 目录并返回已安装的 skill 列表

#### Scenario: 无已安装 skills
- **WHEN** 指定工具目录下没有已安装的 skills
- **THEN** 系统显示提示信息并返回主菜单

### Requirement: 交互式卸载选择

系统 SHALL 提供交互式界面让用户选择要卸载的 skills。

#### Scenario: 显示已安装 skills 列表
- **WHEN** 用户进入卸载选择步骤
- **THEN** 系统显示所有已安装的 skills，使用 checkbox 多选格式

#### Scenario: 空格切换选中状态
- **WHEN** 用户按下 `Space` 键
- **THEN** 当前高亮项的选中状态切换

#### Scenario: 确认卸载选择
- **WHEN** 用户按下 `Enter` 键
- **THEN** 系统确认选中的 skills 为待卸载项

### Requirement: 卸载确认

系统 SHALL 在执行卸载前显示详细信息并要求二次确认。

#### Scenario: 显示卸载预览
- **WHEN** 用户选择要卸载的 skills
- **THEN** 系统显示将要删除的目录路径列表

#### Scenario: 二次确认
- **WHEN** 系统显示卸载预览后
- **THEN** 系统要求用户输入 `y` 确认或 `n` 取消

#### Scenario: 取消卸载
- **WHEN** 用户在确认步骤输入 `n`
- **THEN** 系统取消卸载操作并返回主菜单

### Requirement: 执行卸载

系统 SHALL 安全地删除选中的 skill 目录。

#### Scenario: 成功卸载
- **WHEN** 用户确认卸载
- **THEN** 系统删除选中的 skill 目录及其所有内容

#### Scenario: 卸载结果显示
- **WHEN** 卸载操作完成
- **THEN** 系统显示每个 skill 的卸载结果（成功/失败）

#### Scenario: 卸载失败处理
- **WHEN** 某个 skill 卸载失败（如权限问题）
- **THEN** 系统显示错误信息，继续卸载其他选中的 skills

### Requirement: 命令行卸载参数

系统 SHALL 支持 `--uninstall` 参数进入卸载模式。

#### Scenario: 交互式卸载模式
- **WHEN** 用户运行 `install.py --uninstall`
- **THEN** 系统进入卸载流程，引导用户选择工具和 skills

#### Scenario: 非交互式卸载
- **WHEN** 用户运行 `install.py --uninstall --skills skill1,skill2 --tools claude-code`
- **THEN** 系统直接卸载指定的 skills，无需交互确认

#### Scenario: 卸载所有 skills
- **WHEN** 用户运行 `install.py --uninstall --skills all --tools all`
- **THEN** 系统卸载所有工具下的所有 skills