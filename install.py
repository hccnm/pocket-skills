#!/usr/bin/env python3
"""
Pocket Skills - 安装向导

交互式安装脚本，支持将 skills 安装到 Claude Code、Cursor、Codex 和 Gemini CLI。
支持 Windows、macOS 和 Linux。

功能:
- 自动发现 skills 目录中的可用技能包
- 交互式多选界面（空格选择，箭头移动）
- 命令行参数支持（非交互模式）
- 卸载已安装的 skills
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple


# ============================================================================
# 常量定义
# ============================================================================

MIN_PYTHON_VERSION = (3, 8)
SKILLS_DIR = "skills"
SKILL_PREFIX = "pocket-"

# 工具配置
TOOL_CONFIGS = {
    "claude-code": {
        "name": "Claude Code",
        "skill_dir": ".claude/skills",
    },
    "cursor": {
        "name": "Cursor",
        "skill_dir": ".cursor/skills",
    },
    "codex": {
        "name": "Codex",
        "skill_dir": ".codex/skills",
    },
    "gemini-code": {
        "name": "Gemini CLI",
        "skill_dir": ".gemini/pocket-skills",
        "command_dir": ".gemini/commands",
        "command_ext": ".toml",
    },
}


# ============================================================================
# 数据结构
# ============================================================================


@dataclass
class SkillInfo:
    """Skill 信息"""

    name: str
    path: Path
    description: str = ""
    installed_name: str = ""
    actual_name: str = ""


class InstallResult(NamedTuple):
    """安装结果"""

    skill: str
    tool: str
    success: bool
    path: Path | None = None
    error: str | None = None


class UninstallResult(NamedTuple):
    """卸载结果"""

    skill: str
    tool: str
    success: bool
    path: Path | None = None
    error: str | None = None


# ============================================================================
# 工具函数
# ============================================================================


def check_python_version() -> bool:
    """检查 Python 版本是否满足要求"""
    if sys.version_info < MIN_PYTHON_VERSION:
        print(f"\n❌ 错误: 需要 Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+")
        print(f"   当前版本: Python {sys.version_info.major}.{sys.version_info.minor}")
        return False
    return True


def detect_os() -> str:
    """检测操作系统"""
    system = platform.system().lower()
    if system == "darwin":
        return "macOS"
    elif system == "windows":
        return "Windows"
    elif system == "linux":
        return "Linux"
    else:
        return system.capitalize()


def get_home_dir() -> Path:
    """获取用户主目录"""
    return Path.home()


def get_script_dir() -> Path:
    """获取脚本所在目录（项目根目录）"""
    return Path(__file__).parent.resolve()


def check_questionary() -> bool:
    """检查 questionary 库是否可用"""
    try:
        import questionary  # noqa: F401
        return True
    except ImportError:
        return False


# ============================================================================
# Skill 发现机制
# ============================================================================


def discover_skills() -> list[SkillInfo]:
    """
    发现 skills 目录下所有有效的 skill 包

    一个有效的 skill 包定义为：包含 SKILL.md 文件的目录
    """
    script_dir = get_script_dir()
    skills_root = script_dir / SKILLS_DIR
    skills: list[SkillInfo] = []

    if not skills_root.exists():
        return skills

    for skill_dir in skills_root.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill_info = get_skill_info(skill_dir)
                skills.append(skill_info)

    # 按名称排序
    skills.sort(key=lambda s: s.name)
    return skills


def get_skill_info(skill_path: Path) -> SkillInfo:
    """
    从 SKILL.md 文件提取 skill 元信息
    """
    skill_file = skill_path / "SKILL.md"
    name = skill_path.name
    description = ""

    if skill_file.exists():
        try:
            content = skill_file.read_text(encoding="utf-8")
            description_match = re.search(r"^description:\s*(.+)$", content, flags=re.MULTILINE)
            if description_match:
                description = description_match.group(1).strip().strip("\"'")
            else:
                # 回退到正文中的首行有效文本
                lines = content.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(("#", "---")):
                        description = line[:80]  # 限制描述长度
                        break
        except Exception:
            pass

    return SkillInfo(
        name=name,
        path=skill_path,
        description=description,
        installed_name=get_installed_skill_name(name),
        actual_name=name,
    )


def get_installed_skill_name(skill_name: str) -> str:
    """获取安装后对外暴露的 skill 名称。"""
    if skill_name.startswith(SKILL_PREFIX):
        return skill_name
    return f"{SKILL_PREFIX}{skill_name}"


def get_source_skill_name(installed_name: str) -> str:
    """从安装后的名称恢复仓库中的原始 skill 名称。"""
    if installed_name.startswith(SKILL_PREFIX):
        return installed_name[len(SKILL_PREFIX) :]
    return installed_name


def get_skill_aliases(skill_name: str) -> list[str]:
    """获取一个 skill 可能存在的安装别名，前缀版优先。"""
    aliases: list[str] = []
    for candidate in [get_installed_skill_name(skill_name), skill_name]:
        if candidate not in aliases:
            aliases.append(candidate)
    return aliases


def get_skill_label(skill: SkillInfo) -> str:
    """获取给用户展示的 skill 名称。"""
    return skill.installed_name or get_installed_skill_name(skill.name)


def detect_installed_skills(tool_key: str) -> list[SkillInfo]:
    """
    检测指定工具目录下已安装的 skills
    """
    config = TOOL_CONFIGS[tool_key]
    home = get_home_dir()
    skill_dir = home / config["skill_dir"]
    skills: list[SkillInfo] = []

    if not skill_dir.exists():
        return skills

    for installed_skill in skill_dir.iterdir():
        if installed_skill.is_dir():
            skill_file = installed_skill / "SKILL.md"
            if skill_file.exists():
                source_name = get_source_skill_name(installed_skill.name)
                skill_info = SkillInfo(
                    name=source_name,
                    path=installed_skill,
                    description="",
                    installed_name=get_installed_skill_name(source_name),
                    actual_name=installed_skill.name,
                )
                skills.append(skill_info)

    skills.sort(key=lambda s: s.installed_name or s.name)
    return skills


# ============================================================================
# 显示函数
# ============================================================================


def show_banner() -> None:
    """显示欢迎横幅"""
    print("\n" + "=" * 50)
    print("  Pocket Skills - 安装向导")
    print("=" * 50)


def show_progress(message: str, indent: int = 0) -> None:
    """显示进度信息"""
    prefix = "  " * indent
    print(f"{prefix}{message}")


def require_questionary() -> None:
    """确保交互式模式可用。"""
    if check_questionary():
        return

    raise RuntimeError(
        "交互式模式需要 questionary。请先运行: pip install questionary，"
        "或改用命令行参数模式。"
    )


def show_main_menu() -> str:
    """显示主菜单，让用户选择安装或卸载"""
    require_questionary()
    import questionary

    selected = questionary.checkbox(
        "请选择操作",
        choices=[
            questionary.Choice(title="安装 skills", value="install"),
            questionary.Choice(title="卸载 skills", value="uninstall"),
        ],
        instruction="(空格选择，回车确认；仅可选择一项)",
        validate=lambda answer: True if len(answer) == 1 else "请选择一项操作",
    ).ask()

    return selected[0] if selected else ""


def show_skill_checkbox(skills: list[SkillInfo], title: str = "请选择 skills") -> list[SkillInfo]:
    """
    使用 questionary 显示 checkbox 多选界面
    """
    require_questionary()
    return show_skill_checkbox_questionary(skills, title)


def show_skill_checkbox_questionary(skills: list[SkillInfo], title: str) -> list[SkillInfo]:
    """使用 questionary 库的 checkbox 多选界面"""
    import questionary

    choices = []
    for skill in skills:
        label = get_skill_label(skill)
        if skill.description:
            label += f" - {skill.description}"
        choices.append(questionary.Choice(title=label, value=skill))

    selected = questionary.checkbox(
        title,
        choices=choices,
        instruction="(空格选择，回车确认)",
    ).ask()

    if selected is None:
        # 用户按了 Ctrl+C
        return []
    return selected


def show_tool_checkbox(title: str = "请选择目标工具") -> list[str]:
    """显示工具多选菜单并获取用户选择"""
    tool_keys = list(TOOL_CONFIGS.keys())

    print(f"\n检测到操作系统: {detect_os()}")

    require_questionary()
    return show_tool_checkbox_questionary(tool_keys, title)


def show_tool_checkbox_questionary(tool_keys: list[str], title: str) -> list[str]:
    """使用 questionary 库的 checkbox 多选工具"""
    import questionary

    choices = [
        questionary.Choice(title=TOOL_CONFIGS[tool_key]["name"], value=tool_key)
        for tool_key in tool_keys
    ]

    selected = questionary.checkbox(
        title,
        choices=choices,
        instruction="(空格选择，回车确认)",
    ).ask()

    if selected is None:
        return []
    return selected


def confirm_yes_no(prompt: str, default: bool = True) -> bool:
    """确认提示，支持默认值。"""
    suffix = "(Y/n)" if default else "(y/N)"
    default_hint = "默认: y" if default else "默认: n"

    while True:
        choice = input(f"\n{prompt} {suffix} [{default_hint}]: ").strip().lower()
        if not choice:
            return default
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("❌ 无效输入，请输入 y 或 n，或直接回车使用默认值。")


def confirm_selection(skills: list[SkillInfo], action: str = "安装") -> bool:
    """确认选择"""
    if not skills:
        print(f"\n未选择任何 skill。")
        return False

    print(f"\n将{action}以下 skills:")
    for skill in skills:
        print(f"  - {get_skill_label(skill)}")

    return confirm_yes_no(f"确认{action}?", default=True)


def confirm_update(skill: SkillInfo, tool_key: str, installed_skill: SkillInfo | None = None) -> bool:
    """确认更新已有安装"""
    config = TOOL_CONFIGS[tool_key]
    target = installed_skill.path if installed_skill else get_skill_target(skill.name, tool_key)
    print(f"\n⚠️  检测到 {get_skill_label(skill)} 已安装于 {config['name']}:")
    print(f"   {target}")
    return confirm_yes_no("是否覆盖更新?", default=True)


def confirm_uninstall(skills: list[SkillInfo], tool_key: str) -> bool:
    """确认卸载"""
    if not skills:
        return False

    config = TOOL_CONFIGS[tool_key]
    home = get_home_dir()

    print(f"\n⚠️  将从 {config['name']} 卸载以下 skills:")
    for skill in skills:
        target = skill.path
        print(f"  - {get_skill_label(skill)}")
        print(f"    路径: {target}")

    return confirm_yes_no("确认卸载?", default=True)


# ============================================================================
# 安装逻辑
# ============================================================================


def get_skill_source_path(skill_name: str, tool_key: str) -> Path | None:
    """获取 skill 的源路径"""
    script_dir = get_script_dir()

    # 优先使用平台特定目录；目录名与 tool_key 保持一致
    skill_root = script_dir / SKILLS_DIR / skill_name
    for platform_name in (tool_key, tool_key.replace("-", "")):
        platform_source = skill_root / "platforms" / platform_name
        if platform_source.exists():
            return platform_source

    # 检查 skill 根目录
    skill_source = skill_root
    if skill_source.exists():
        return skill_source

    return None


def get_core_source_path() -> Path | None:
    """获取 core 目录的源路径"""
    script_dir = get_script_dir()

    # 检查项目根目录的 core
    core_source = script_dir / "core"
    if core_source.exists():
        return core_source

    return None


def get_skill_target(skill_name: str, tool_key: str, alias_name: str | None = None) -> Path:
    """获取某个 skill 在目标工具下的安装目录。"""
    config = TOOL_CONFIGS[tool_key]
    installed_name = alias_name or get_installed_skill_name(skill_name)
    return get_home_dir() / config["skill_dir"] / installed_name


def fix_skill_paths(skill_content: str, target: Path) -> str:
    """修复 SKILL.md 中的路径引用，避免工具将相对路径误解为工作区路径。"""
    base = str(target)
    content = skill_content

    for prefix_pattern in [
        r"(?:\.\./){2}",
        r"\./",
        r"(?<![\w/.-])",
    ]:
        content = re.sub(
            prefix_pattern + r"(core|scripts|references|agents)/",
            lambda match: f"{base}/{match.group(1)}/",
            content,
        )

    return content


def rewrite_skill_frontmatter_name(skill_content: str, installed_name: str) -> str:
    """将安装产物中的 frontmatter name 改成对外暴露名称。"""
    if not skill_content.startswith("---\n"):
        return skill_content

    return re.sub(
        r"^name:\s*.+$",
        f"name: {installed_name}",
        skill_content,
        count=1,
        flags=re.MULTILINE,
    )


def strip_frontmatter(markdown: str) -> str:
    """去掉 Markdown 顶部的 YAML frontmatter。"""
    if not markdown.startswith("---\n"):
        return markdown

    _, _, remainder = markdown.partition("\n---\n")
    return remainder if remainder else markdown


def extract_frontmatter_description(markdown: str) -> str | None:
    """从 YAML frontmatter 中提取 description。"""
    if not markdown.startswith("---\n"):
        return None

    frontmatter, _, _ = markdown[4:].partition("\n---\n")
    if not frontmatter:
        return None

    match = re.search(r"^description:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    if not match:
        return None

    return match.group(1).strip().strip("\"'")


def get_command_target(skill_name: str, tool_key: str, alias_name: str | None = None) -> Path | None:
    """获取命令型平台的命令文件路径。"""
    config = TOOL_CONFIGS[tool_key]
    command_dir = config.get("command_dir")
    if not command_dir:
        return None

    extension = config.get("command_ext", ".toml")
    installed_name = alias_name or get_installed_skill_name(skill_name)
    return get_home_dir() / command_dir / f"{installed_name}{extension}"


def write_command_file(
    skill: SkillInfo,
    tool_key: str,
    fixed_content: str,
) -> None:
    """为命令型平台生成入口文件。"""
    command_target = get_command_target(skill.name, tool_key)
    if not command_target:
        return

    prompt = strip_frontmatter(fixed_content).strip()
    command_description = extract_frontmatter_description(fixed_content) or skill.description
    command_target.parent.mkdir(parents=True, exist_ok=True)
    command_target.write_text(
        "\n".join(
            [
                f"description = {json.dumps(command_description, ensure_ascii=False)}",
                f"prompt = {json.dumps(prompt, ensure_ascii=False)}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def copy_entry(source_entry: Path, target_dir: Path, verbose: bool = True) -> None:
    """复制文件或目录到目标目录，若已存在则覆盖。"""
    if not source_entry.exists():
        return

    target_entry = target_dir / source_entry.name
    if target_entry.exists():
        if target_entry.is_dir():
            shutil.rmtree(target_entry)
        else:
            target_entry.unlink()

    if verbose:
        suffix = "/" if source_entry.is_dir() else ""
        show_progress(f"- 复制 {source_entry.name}{suffix}", 1)

    if source_entry.is_dir():
        shutil.copytree(source_entry, target_entry)
    else:
        shutil.copy2(source_entry, target_entry)


def remove_existing_install_artifacts(skill_name: str, tool_key: str) -> None:
    """删除同一个 skill 的新旧安装产物，避免前缀迁移后残留重复入口。"""
    for alias_name in get_skill_aliases(skill_name):
        target = get_skill_target(skill_name, tool_key, alias_name)
        if target.exists():
            shutil.rmtree(target)

        command_target = get_command_target(skill_name, tool_key, alias_name)
        if command_target and command_target.exists():
            command_target.unlink()


def sync_skill_entries(
    skill_root: Path,
    skill_source: Path,
    target: Path,
    verbose: bool = True,
) -> None:
    """复制共享资源，并用平台特定资源覆盖。"""
    excluded = {"SKILL.md", "platforms"}

    for entry in skill_root.iterdir():
        if entry.name in excluded:
            continue
        copy_entry(entry, target, verbose)

    if skill_source == skill_root:
        return

    for entry in skill_source.iterdir():
        if entry.name == "SKILL.md":
            continue
        copy_entry(entry, target, verbose)


def install_skill(skill: SkillInfo, tool_key: str, verbose: bool = True) -> InstallResult:
    """
    安装单个 skill 到指定工具
    """
    config = TOOL_CONFIGS[tool_key]
    target = get_skill_target(skill.name, tool_key)

    script_dir = get_script_dir()
    skill_root = script_dir / SKILLS_DIR / skill.name
    skill_source = get_skill_source_path(skill.name, tool_key)
    try:
        # 检查源目录
        if not skill_source:
            skill_source = skill_root

        if not skill_source.exists():
            return InstallResult(
                skill=get_skill_label(skill),
                tool=tool_key,
                success=False,
                error=f"源目录不存在: {skill_source}",
            )

        # 平台目录只提供适配后的 SKILL.md，其余共享资源默认来自 skill 根目录
        skill_file = skill_source / "SKILL.md"

        if verbose:
            show_progress(f"安装 {get_skill_label(skill)} 到 {config['name']}...", 0)

        # 重装前先清理目标目录，避免旧版本残留文件影响结果
        remove_existing_install_artifacts(skill.name, tool_key)
        target.mkdir(parents=True, exist_ok=True)

        # 复制 SKILL.md
        if skill_file.exists():
            if verbose:
                show_progress("- 复制 SKILL.md", 1)
            skill_content = skill_file.read_text(encoding="utf-8")
            fixed_content = rewrite_skill_frontmatter_name(skill_content, get_installed_skill_name(skill.name))
            fixed_content = fix_skill_paths(fixed_content, target)
            (target / "SKILL.md").write_text(fixed_content, encoding="utf-8")
            if tool_key == "gemini-code":
                if verbose:
                    show_progress("- 生成命令入口", 1)
                write_command_file(skill, tool_key, fixed_content)
        else:
            return InstallResult(
                skill=get_skill_label(skill),
                tool=tool_key,
                success=False,
                error="SKILL.md 不存在",
            )

        # 复制共享资源，并允许平台目录提供覆盖或额外文件（如 .cursorrules、agents/）。
        sync_skill_entries(skill_root, skill_source, target, verbose)

        return InstallResult(
            skill=get_skill_label(skill),
            tool=tool_key,
            success=True,
            path=target,
        )

    except PermissionError as e:
        return InstallResult(
            skill=get_skill_label(skill),
            tool=tool_key,
            success=False,
            error=f"权限不足: {e}",
        )
    except Exception as e:
        return InstallResult(
            skill=get_skill_label(skill),
            tool=tool_key,
            success=False,
            error=str(e),
        )


def uninstall_skill(skill: SkillInfo, tool_key: str, verbose: bool = True) -> UninstallResult:
    """卸载单个 skill"""
    config = TOOL_CONFIGS[tool_key]
    target = skill.path

    try:
        if verbose:
            show_progress(f"卸载 {get_skill_label(skill)} 从 {config['name']}...", 0)

        if not target.exists():
            remove_existing_install_artifacts(skill.name, tool_key)
            return UninstallResult(
                skill=get_skill_label(skill),
                tool=tool_key,
                success=False,
                error="目录不存在",
            )

        remove_existing_install_artifacts(skill.name, tool_key)

        if verbose:
            show_progress("✓ 完成", 1)

        return UninstallResult(
            skill=get_skill_label(skill),
            tool=tool_key,
            success=True,
            path=target,
        )

    except PermissionError as e:
        return UninstallResult(
            skill=get_skill_label(skill),
            tool=tool_key,
            success=False,
            error=f"权限不足: {e}",
        )
    except Exception as e:
        return UninstallResult(
            skill=get_skill_label(skill),
            tool=tool_key,
            success=False,
            error=str(e),
        )


# ============================================================================
# 结果显示
# ============================================================================


def show_install_summary(results: list[InstallResult]) -> None:
    """显示安装结果摘要"""
    print("\n" + "-" * 50)
    print("  安装结果")
    print("-" * 50)

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    # 按工具分组显示
    tools = sorted(set(r.tool for r in results))
    for tool in tools:
        config = TOOL_CONFIGS[tool]
        tool_results = [r for r in results if r.tool == tool]
        print(f"\n{config['name']}:")
        for result in tool_results:
            if result.success:
                print(f"  ✓ {result.skill}")
            else:
                print(f"  ✗ {result.skill}: {result.error}")

    print("\n" + "-" * 50)
    if fail_count == 0:
        print(f"\n🎉 全部安装完成! ({success_count}/{len(results)})")
    else:
        print(f"\n⚠️  部分完成: 成功 {success_count}, 失败 {fail_count}")


def show_uninstall_summary(results: list[UninstallResult]) -> None:
    """显示卸载结果摘要"""
    print("\n" + "-" * 50)
    print("  卸载结果")
    print("-" * 50)

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    # 按工具分组显示
    tools = sorted(set(r.tool for r in results))
    for tool in tools:
        config = TOOL_CONFIGS[tool]
        tool_results = [r for r in results if r.tool == tool]
        print(f"\n{config['name']}:")
        for result in tool_results:
            if result.success:
                print(f"  ✓ {result.skill}")
            else:
                print(f"  ✗ {result.skill}: {result.error}")

    print("\n" + "-" * 50)
    if fail_count == 0:
        print(f"\n🎉 全部卸载完成! ({success_count}/{len(results)})")
    else:
        print(f"\n⚠️  部分完成: 成功 {success_count}, 失败 {fail_count}")


# ============================================================================
# 命令行参数解析
# ============================================================================


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Pocket Skills 安装向导",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式安装
  python install.py

  # 安装指定 skills
  python install.py --skills generate-prd-from-code

  # 安装多个 skills 到指定工具
  python install.py --skills skill1,skill2 --tools claude-code,codex

  # 安装所有 skills 到所有工具
  python install.py --skills all --tools all

  # 卸载 skills
  python install.py --uninstall --skills skill1 --tools cursor
        """,
    )

    parser.add_argument(
        "--skills",
        type=str,
        help="要操作的 skills，逗号分隔或 'all'",
    )

    parser.add_argument(
        "--tools",
        type=str,
        help="目标工具，逗号分隔或 'all' (claude-code, cursor, codex, gemini-code)",
    )

    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="卸载模式",
    )

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="跳过确认提示",
    )

    return parser.parse_args()


def validate_skill_names(skill_names: list[str], available_skills: list[SkillInfo]) -> list[str]:
    """验证 skill 名称有效性"""
    available_names = {s.name for s in available_skills}
    normalized_names = [get_source_skill_name(name) for name in skill_names]
    invalid = [name for name in normalized_names if name not in available_names]

    if invalid:
        print(f"\n❌ 无效的 skill 名称: {', '.join(invalid)}")
        print(f"可用的 skills: {', '.join(available_names)}")
        return []

    deduped: list[str] = []
    for name in normalized_names:
        if name not in deduped:
            deduped.append(name)

    return deduped


def validate_tool_names(tool_names: list[str]) -> list[str]:
    """验证工具名称有效性"""
    valid_names = set(TOOL_CONFIGS.keys())
    invalid = [name for name in tool_names if name not in valid_names and name != "all"]

    if invalid:
        print(f"\n❌ 无效的工具名称: {', '.join(invalid)}")
        print(f"可用的工具: {', '.join(valid_names)}")
        return []

    return tool_names


# ============================================================================
# 主流程
# ============================================================================


def run_install_flow(
    skills_arg: str | None = None,
    tools_arg: str | None = None,
    skip_confirm: bool = False,
) -> int:
    """执行安装流程"""
    # 发现可用 skills
    available_skills = discover_skills()

    if not available_skills:
        print("\n❌ 没有可用的 skills")
        print(f"请确保 {SKILLS_DIR}/ 目录下包含有效的 skill 包")
        return 1

    # 选择 skills
    if skills_arg:
        if skills_arg == "all":
            selected_skills = available_skills.copy()
        else:
            skill_names = [s.strip() for s in skills_arg.split(",")]
            valid_names = validate_skill_names(skill_names, available_skills)
            if not valid_names:
                return 1
            selected_skills = [s for s in available_skills if s.name in valid_names]
    else:
        # 交互式选择
        if len(available_skills) == 1:
            print(f"\n发现 1 个 skill: {get_skill_label(available_skills[0])}")
            selected_skills = available_skills.copy()
        else:
            print(f"\n发现 {len(available_skills)} 个可用的 skills:")
            selected_skills = show_skill_checkbox(available_skills, "请选择要安装的 skills")

        if not selected_skills:
            print("\n已取消。")
            return 0

    # 确认选择
    if not skip_confirm and not confirm_selection(selected_skills, "安装"):
        print("\n已取消。")
        return 0

    # 选择工具
    if tools_arg:
        if tools_arg == "all":
            tools = list(TOOL_CONFIGS.keys())
        else:
            tool_names = [t.strip() for t in tools_arg.split(",")]
            valid_tools = validate_tool_names(tool_names)
            if not valid_tools:
                return 1
            tools = valid_tools
    else:
        tools = show_tool_checkbox("请选择要安装到的工具")
        if not tools:
            print("\n已取消。")
            return 0

    # 执行安装
    print("\n正在安装...")
    results: list[InstallResult] = []

    for tool in tools:
        for skill in selected_skills:
            # 检查是否已安装
            installed = detect_installed_skills(tool)
            already_installed = [s for s in installed if s.name == skill.name]

            if already_installed:
                if not skip_confirm and not confirm_update(skill, tool, already_installed[0]):
                    continue

            result = install_skill(skill, tool)
            results.append(result)

            if result.success:
                show_progress("✓ 完成", 1)
            else:
                show_progress(f"✗ 失败: {result.error}", 1)

    # 显示摘要
    show_install_summary(results)

    return 0 if all(r.success for r in results) else 1


def run_uninstall_flow(
    skills_arg: str | None = None,
    tools_arg: str | None = None,
    skip_confirm: bool = False,
) -> int:
    """执行卸载流程"""
    # 选择工具
    if tools_arg:
        if tools_arg == "all":
            tools = list(TOOL_CONFIGS.keys())
        else:
            tool_names = [t.strip() for t in tools_arg.split(",")]
            valid_tools = validate_tool_names(tool_names)
            if not valid_tools:
                return 1
            tools = valid_tools
    else:
        tools = show_tool_checkbox("请选择要从中卸载的工具")
        if not tools:
            print("\n已取消。")
            return 0

    # 收集已安装的 skills
    all_installed: list[tuple[SkillInfo, str]] = []
    for tool in tools:
        installed = detect_installed_skills(tool)
        for skill in installed:
            all_installed.append((skill, tool))

    if not all_installed:
        print("\n没有已安装的 skills")
        return 0

    # 选择要卸载的 skills
    if skills_arg:
        if skills_arg == "all":
            selected = all_installed.copy()
        else:
            skill_names = set(get_source_skill_name(s.strip()) for s in skills_arg.split(","))
            selected = [(s, t) for s, t in all_installed if s.name in skill_names]
    else:
        # 显示已安装列表供选择
        print(f"\n发现 {len(all_installed)} 个已安装的 skills:")
        skills_by_name: dict[str, list[tuple[SkillInfo, str]]] = {}
        for skill, tool in all_installed:
            if skill.name not in skills_by_name:
                skills_by_name[skill.name] = []
            skills_by_name[skill.name].append((skill, tool))

        skill_infos = [
            SkillInfo(
                name=name,
                path=Path(),
                description=f"已安装到: {', '.join(TOOL_CONFIGS[t]['name'] for _, t in pairs)}",
                installed_name=get_installed_skill_name(name),
                actual_name=name,
            )
            for name, pairs in skills_by_name.items()
        ]

        selected_skills = show_skill_checkbox(skill_infos, "请选择要卸载的 skills")

        if not selected_skills:
            print("\n已取消。")
            return 0

        selected = [
            (s, t)
            for s, t in all_installed
            if s.name in [sel.name for sel in selected_skills]
        ]

    # 确认卸载
    if not skip_confirm:
        print("\n将要卸载:")
        for skill, tool in selected:
            config = TOOL_CONFIGS[tool]
            print(f"  - {skill.name} (从 {config['name']})")

        if not confirm_yes_no("确认卸载?", default=True):
            print("\n已取消。")
            return 0

    # 执行卸载
    print("\n正在卸载...")
    results: list[UninstallResult] = []

    for skill, tool in selected:
        result = uninstall_skill(skill, tool)
        results.append(result)

    # 显示摘要
    show_uninstall_summary(results)

    return 0 if all(r.success for r in results) else 1


def main() -> int:
    """主函数"""
    # 检查 Python 版本
    if not check_python_version():
        return 1

    # 解析命令行参数
    args = parse_args()

    # 显示欢迎信息
    show_banner()

    try:
        # 确定运行模式
        if args.skills or args.tools:
            # 非交互模式
            if args.uninstall:
                return run_uninstall_flow(args.skills, args.tools, args.yes)
            else:
                return run_install_flow(args.skills, args.tools, args.yes)
        elif args.uninstall:
            # 交互式卸载
            return run_uninstall_flow(None, None, args.yes)
        else:
            # 交互式主菜单
            action = show_main_menu()
            if action == "install":
                return run_install_flow(None, None, args.yes)
            else:
                return run_uninstall_flow(None, None, args.yes)
    except RuntimeError as exc:
        print(f"\n❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
