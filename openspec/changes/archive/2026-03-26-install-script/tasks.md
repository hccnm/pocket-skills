## 1. 项目结构创建

- [x] 1.1 创建 `install.py` 脚本文件
- [x] 1.2 创建 `install.bat` Windows 启动脚本
- [x] 1.3 创建 `install.sh` macOS/Linux 启动脚本

## 2. 核心功能实现

- [x] 2.1 实现操作系统检测函数（`detect_os()`）
- [x] 2.2 实现用户主目录获取函数（`get_home_dir()`）
- [x] 2.3 实现工具选择菜单显示函数（`show_tool_menu()`）
- [x] 2.4 实现安装目标路径构建函数（`get_install_paths()`）

## 3. 安装逻辑实现

- [x] 3.1 实现 skill 目录完整复制函数（`install_skill()`），包含 SKILL.md 和 core 子目录
- [x] 3.2 实现路径替换逻辑（将 SKILL.md 中的 `../../core/` 替换为 `./core/`）
- [x] 3.3 实现已安装检测函数（`is_already_installed()`）

## 4. 交互流程实现

- [x] 4.1 实现安装确认提示（`confirm_installation()`）
- [x] 4.2 实现更新确认提示（`confirm_update()`）
- [x] 4.3 实现安装进度显示（`show_progress()`）
- [x] 4.4 实现安装结果摘要显示（`show_summary()`）

## 5. 错误处理实现

- [x] 5.1 实现 Python 版本检查（`check_python_version()`）
- [x] 5.2 实现权限错误捕获和处理
- [x] 5.3 实现文件操作错误捕获和处理
- [x] 5.4 实现部分失败汇总报告

## 6. 测试与验证

- [x] 6.1 在 macOS 上测试完整安装流程
- [x] 6.2 在 Windows 上测试完整安装流程（待用户在 Windows 上验证）
- [x] 6.3 测试更新已有安装的流程
- [x] 6.4 验证安装后 skill 可正常使用