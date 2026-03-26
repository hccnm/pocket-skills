## ADDED Requirements

### Requirement: Skill 自动发现

系统 SHALL 能够自动发现 `skills/` 目录下所有有效的 skill 包。一个有效的 skill 包定义为：包含 `SKILL.md` 文件的目录。

#### Scenario: 发现单个 skill
- **WHEN** `skills/` 目录下有一个包含 `SKILL.md` 的子目录 `generate-prd-from-code`
- **THEN** 系统返回 `["generate-prd-from-code"]` 作为可用 skill

#### Scenario: 发现多个 skills
- **WHEN** `skills/` 目录下有多个包含 `SKILL.md` 的子目录
- **THEN** 系统返回所有有效 skill 名称列表

#### Scenario: 空目录处理
- **WHEN** `skills/` 目录为空或不存在
- **THEN** 系统返回空列表并显示友好提示

#### Scenario: 忽略无效目录
- **WHEN** `skills/` 目录下有子目录但不包含 `SKILL.md`
- **THEN** 系统忽略该目录，仅返回有效的 skills

### Requirement: Skill 元信息读取

系统 SHALL 能够读取每个 skill 的基本信息用于展示。

#### Scenario: 读取 skill 名称
- **WHEN** 发现 skill 目录 `generate-prd-from-code`
- **THEN** 系统能够读取并显示该 skill 的名称

#### Scenario: 读取 skill 描述
- **WHEN** skill 的 `SKILL.md` 文件包含描述信息
- **THEN** 系统能够提取并展示描述摘要