## Why

当前安装脚本 (`install.py`) 硬编码只安装单一 skill (`generate-prd-from-code`)，用户无法选择安装哪些 skills。随着项目发展，skills 目录将包含更多技能包，用户需要能够：

1. 查看所有可用的 skills
2. 选择性地安装特定的 skills
3. 批量安装多个 skills
4. 卸载已安装的 skills

## What Changes

- 新增 skills 发现机制：自动扫描 `skills/` 目录获取可用 skills 列表
- 新增交互式选择界面：支持空格多选模式选择要安装的 skills
- 新增卸载功能：检测已安装的 skills，支持选择性卸载
- 支持命令行参数模式：`--skills`、`--tools`、`--uninstall` 参数
- 保留原有工具选择流程（Claude Code / Cursor / 全部）

## Capabilities

### New Capabilities

- `skill-discovery`: 自动发现和列出 skills 目录中所有可用的技能包
- `skill-selection`: 交互式多选界面（checkbox），支持空格选择、箭头移动
- `skill-uninstall`: 检测已安装的 skills 并支持选择性卸载
- `cli-arguments`: 支持通过命令行参数指定 skills 和操作，实现非交互式安装/卸载

### Modified Capabilities

无现有 spec，无需修改。

## Impact

- **代码变更**: `install.py` 主逻辑重构
- **用户体验**: 安装流程新增 skills 选择步骤；新增卸载流程
- **向后兼容**: 保留原有工具选择流程，不破坏现有使用方式
- **扩展性**: 未来新增 skill 无需修改安装脚本，自动发现