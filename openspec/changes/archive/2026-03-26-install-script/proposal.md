## Why

用户需要将 `generate-prd-from-code` skill 安装到不同的 AI 编程工具（Claude Code、Cursor 等）。目前缺少统一的安装入口，用户需要手动复制文件到各自工具的配置目录，过程繁琐且容易出错。

一个交互式安装脚本可以简化部署流程，自动检测操作系统，引导用户选择目标工具，并正确处理安装路径。

## What Changes

- 新增跨平台安装脚本，支持 Windows 和 macOS
- 提供交互式命令行界面，用户可选择安装目标工具
- 支持安装和更新两种操作模式
- 自动检测操作系统并适配路径格式
- 显示安装状态和结果摘要

## Capabilities

### New Capabilities

- `skill-installer`: 交互式安装脚本，用于将 generate-prd-from-code skill 部署到用户选择的 AI 工具中

### Modified Capabilities

无现有 capability 需要修改。

## Impact

- 新增文件：安装脚本（位置待设计确定）
- 依赖现有 skill 文件：`platforms/claude-code/generate-prd-from-code/SKILL.md`
- 依赖现有 skill 文件：`platforms/cursor/generate-prd-from-code/SKILL.md`（或调整后的位置）
- 依赖共享引擎：`core/scripts/` 下的 Python 脚本
- 依赖参考文档：`core/references/` 下的规则和模板文档