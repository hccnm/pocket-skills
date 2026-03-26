## 1. 项目结构创建

- [x] 1.1 创建 `platforms/cursor/generate-prd-from-code/` 目录结构
- [x] 1.2 创建空的 `.cursorrules` 文件
- [x] 1.3 创建空的 `SKILL.md` 文件

## 2. Cursor Rules 文件实现

- [x] 2.1 编写 `.cursorrules` 文件的概述部分，说明 skill 的用途和输出
- [x] 2.2 编写快速开始部分，定义纯代码模式的命令流程
- [x] 2.3 编写前端增强模式的命令流程
- [x] 2.4 编写工作流部分，定义五个步骤：检测技术栈 → 提取事实 → 决定是否使用前端 → 合并证据 → 保持推断透明
- [x] 2.5 编写输出契约部分，定义主 PRD 和模块附录的结构
- [x] 2.6 编写参考文档部分，引用 `core/references/` 下的文档

## 3. SKILL.md 文档实现

- [x] 3.1 编写 frontmatter（name, description, license, compatibility, metadata）
- [x] 3.2 复用 `.cursorrules` 的内容结构
- [x] 3.3 添加注意事项部分，强调初始化完整覆盖和产品语言优先原则

## 4. 验证与测试

- [x] 4.1 验证 `.cursorrules` 文件格式符合 Cursor 规范
- [x] 4.2 验证相对路径 `../../core/scripts/` 在目标项目中可正确解析
- [x] 4.3 对比 Claude Code adapter，确保输出契约一致