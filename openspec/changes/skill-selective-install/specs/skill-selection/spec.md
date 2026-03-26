## ADDED Requirements

### Requirement: 交互式 skill 选择界面

系统 SHALL 提供基于 checkbox 的交互式多选界面让用户选择要安装的 skills。

#### Scenario: 显示可用 skills 列表
- **WHEN** 用户进入 skill 选择步骤
- **THEN** 系统显示所有可用 skills，格式为 `[ ] skill-name`，当前项高亮显示

#### Scenario: 空格切换选中状态
- **WHEN** 用户按下 `Space` 键
- **THEN** 当前高亮项的选中状态切换（`[ ]` ↔ `[x]`）

#### Scenario: 上下移动光标
- **WHEN** 用户按下 `↑/↓` 或 `j/k` 键
- **THEN** 高亮条移动到上一个/下一个 skill

#### Scenario: 确认选择
- **WHEN** 用户按下 `Enter` 键
- **THEN** 系统确认当前所有选中状态为 `[x]` 的 skills

#### Scenario: 取消退出
- **WHEN** 用户按下 `Ctrl+C`
- **THEN** 系统退出安装流程

### Requirement: 视觉反馈

系统 SHALL 提供清晰的视觉反馈显示当前选择状态。

#### Scenario: 选中状态显示
- **WHEN** 某个 skill 被选中
- **THEN** 该项显示为 `[x] skill-name`

#### Scenario: 未选中状态显示
- **WHEN** 某个 skill 未被选中
- **THEN** 该项显示为 `[ ] skill-name`

#### Scenario: 当前高亮项
- **WHEN** 光标停留在某项上
- **THEN** 该项以不同颜色或样式高亮显示

### Requirement: 默认选择行为

系统 SHALL 在只有一个 skill 时提供合理的默认行为。

#### Scenario: 单 skill 自动选择
- **WHEN** 只有 1 个 skill 可用
- **THEN** 系统自动选中该 skill 并显示确认信息

#### Scenario: 无 skills 可安装
- **WHEN** 没有 skills 可用
- **THEN** 系统显示错误信息并退出

### Requirement: 依赖库处理

系统 SHALL 妥善处理 `questionary` 库的依赖情况。

#### Scenario: questionary 已安装
- **WHEN** `questionary` 库已安装
- **THEN** 系统使用完整的 checkbox 多选界面

#### Scenario: questionary 未安装
- **WHEN** `questionary` 库未安装
- **THEN** 系统提示用户安装或降级为简单输入模式

### Requirement: 选择确认

系统 SHALL 在执行安装前显示选中的 skills 列表并要求确认。

#### Scenario: 显示选择摘要
- **WHEN** 用户完成 skill 选择（按下 Enter）
- **THEN** 系统显示选中的 skills 列表并要求最终确认

#### Scenario: 取消安装
- **WHEN** 用户在确认步骤选择取消
- **THEN** 系统退出安装流程