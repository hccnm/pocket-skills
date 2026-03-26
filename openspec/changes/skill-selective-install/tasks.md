## 1. Skill 发现机制

- [x] 1.1 创建 `SkillInfo` 数据类，包含 name、path、description 字段
- [x] 1.2 实现 `discover_skills()` 函数，扫描 `skills/` 目录并返回有效 skill 列表
- [x] 1.3 实现 `get_skill_info()` 函数，从 `SKILL.md` 提取 skill 元信息
- [x] 1.4 添加空目录和无效目录的处理逻辑

## 2. 交互式 Skill 选择（Checkbox 多选）

- [x] 2.1 添加 `questionary` 依赖检查函数 `check_questionary()`
- [x] 2.2 实现 `show_skill_checkbox()` 函数，使用 questionary.checkbox 多选界面
- [x] 2.3 实现备选方案 `show_skill_menu_fallback()`，无 questionary 时降级为简单输入
- [x] 2.4 实现单 skill 自动选择逻辑
- [x] 2.5 实现选择确认步骤

## 3. 命令行参数支持

- [x] 3.1 添加 `argparse` 模块解析命令行参数
- [x] 3.2 实现 `--skills` 参数支持（逗号分隔列表或 `all`）
- [x] 3.3 实现 `--tools` 参数支持（逗号分隔列表或 `all`）
- [x] 3.4 实现 `--uninstall` 参数，进入卸载模式
- [x] 3.5 实现 `--help` 帮助信息
- [x] 3.6 实现参数验证：检查 skill 名称有效性
- [x] 3.7 实现非交互模式：参数完整时跳过交互

## 4. 安装逻辑重构

- [x] 4.1 重构 `install_skill()` 函数，支持动态 skill 名称参数
- [x] 4.2 更新 `get_install_paths()` 函数，移除硬编码 `SKILL_NAME`
- [x] 4.3 重构 `main()` 函数流程：先选 skills，再选工具
- [x] 4.4 更新安装预览和摘要显示，支持多 skill 展示

## 5. 卸载功能

- [x] 5.1 实现 `detect_installed_skills()` 函数，检测工具目录下已安装的 skills
- [x] 5.2 实现 `show_installed_skills_menu()` 函数，显示已安装 skills 列表供选择
- [x] 5.3 实现 `uninstall_skill()` 函数，删除选中的 skill 目录
- [x] 5.4 实现卸载确认步骤，显示将要删除的路径并要求二次确认
- [x] 5.5 实现卸载结果显示（成功/失败）

## 6. 主菜单模式

- [x] 6.1 实现 `show_main_menu()` 函数，显示"安装"和"卸载"选项
- [x] 6.2 根据用户选择进入安装流程或卸载流程
- [x] 6.3 支持 `--uninstall` 参数直接进入卸载模式

## 7. 测试与验证

- [x] 7.1 手动测试 checkbox 多选界面（需 questionary）- 已验证 questionary 可用
- [x] 7.2 手动测试降级模式（无 questionary）- 已验证 fallback 工作
- [x] 7.3 手动测试命令行参数模式（安装和卸载）- 已验证
- [x] 7.4 手动测试卸载流程 - 已验证
- [x] 7.5 测试边界情况：空 skills 目录、无效 skill 名称、无已安装 skills - 已验证无效名称
- [x] 7.6 验证向后兼容性：原有使用方式仍然有效

## 8. 文档更新

- [x] 8.1 更新 README.md 说明新的安装和卸载方式
- [x] 8.2 添加 questionary 依赖说明和安装提示
- [x] 8.3 添加命令行参数使用示例（安装和卸载）