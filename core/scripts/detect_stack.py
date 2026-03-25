#!/usr/bin/env python3
"""Detect likely stacks and framework signals for a repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


IGNORE_DIRS = {
    ".git",
    ".idea",
    ".next",
    ".nuxt",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "target",
    "vendor",
}


def safe_read_text(path: Path, max_bytes: int = 250_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return ""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return ""


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def repo_signal(repo_root: Path, relative_path: str, label: str) -> dict[str, str]:
    return {"path": relative_path, "label": label}


def detect_stack(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    stacks: list[dict[str, Any]] = []
    signals: list[dict[str, str]] = []
    languages: set[str] = set()
    package_managers: set[str] = set()
    frontend_entry_hints: list[str] = []

    pom_xml = repo_root / "pom.xml"
    gradle = repo_root / "build.gradle"
    gradle_kts = repo_root / "build.gradle.kts"
    package_json = repo_root / "package.json"
    pyproject = repo_root / "pyproject.toml"
    requirements_txt = repo_root / "requirements.txt"
    cargo_toml = repo_root / "Cargo.toml"
    go_mod = repo_root / "go.mod"

    if pom_xml.exists():
        languages.add("java")
        package_managers.add("maven")
        pom_text = safe_read_text(pom_xml)
        label = "maven"
        if "spring-boot" in pom_text.lower():
            label = "spring-boot"
        signals.append(repo_signal(repo_root, "pom.xml", label))
        stacks.append(
            {
                "kind": "backend",
                "name": "spring-boot" if "spring-boot" in pom_text.lower() else "java-maven",
                "confidence": "high",
                "signals": ["pom.xml", "spring-boot" if "spring-boot" in pom_text.lower() else "maven"],
            }
        )

    if gradle.exists() or gradle_kts.exists():
        languages.add("java")
        package_managers.add("gradle")
        gradle_file = gradle if gradle.exists() else gradle_kts
        gradle_text = safe_read_text(gradle_file)
        label = "gradle"
        if "spring-boot" in gradle_text.lower():
            label = "spring-boot"
        signals.append(repo_signal(repo_root, gradle_file.name, label))
        stacks.append(
            {
                "kind": "backend",
                "name": "spring-boot" if "spring-boot" in gradle_text.lower() else "java-gradle",
                "confidence": "high",
                "signals": [gradle_file.name, label],
            }
        )

    if package_json.exists():
        languages.update({"javascript", "typescript"})
        package_managers.add("npm")
        package_data = load_json(package_json)
        deps = {
            **package_data.get("dependencies", {}),
            **package_data.get("devDependencies", {}),
        }
        dep_names = {name.lower() for name in deps}
        signals.append(repo_signal(repo_root, "package.json", "node"))

        if "pnpm-lock.yaml" in {item.name for item in repo_root.iterdir() if item.exists()}:
            package_managers.add("pnpm")
        if (repo_root / "yarn.lock").exists():
            package_managers.add("yarn")

        if "@nestjs/core" in dep_names or "@nestjs/common" in dep_names:
            stacks.append(
                {
                    "kind": "backend",
                    "name": "nestjs",
                    "confidence": "high",
                    "signals": ["package.json", "@nestjs/common"],
                }
            )
        elif "express" in dep_names:
            stacks.append(
                {
                    "kind": "backend",
                    "name": "express",
                    "confidence": "medium",
                    "signals": ["package.json", "express"],
                }
            )
        elif "fastify" in dep_names:
            stacks.append(
                {
                    "kind": "backend",
                    "name": "fastify",
                    "confidence": "medium",
                    "signals": ["package.json", "fastify"],
                }
            )

        if "next" in dep_names:
            stacks.append(
                {
                    "kind": "frontend",
                    "name": "nextjs",
                    "confidence": "high",
                    "signals": ["package.json", "next"],
                }
            )
            frontend_entry_hints.append("app/")
            frontend_entry_hints.append("pages/")
        elif "react" in dep_names:
            stacks.append(
                {
                    "kind": "frontend",
                    "name": "react-spa",
                    "confidence": "medium",
                    "signals": ["package.json", "react"],
                }
            )
            frontend_entry_hints.append("src/router/")
        elif "vue" in dep_names:
            stacks.append(
                {
                    "kind": "frontend",
                    "name": "vue-spa",
                    "confidence": "medium",
                    "signals": ["package.json", "vue"],
                }
            )
            frontend_entry_hints.append("src/router/")
        elif "@angular/core" in dep_names:
            stacks.append(
                {
                    "kind": "frontend",
                    "name": "angular",
                    "confidence": "high",
                    "signals": ["package.json", "@angular/core"],
                }
            )
            frontend_entry_hints.append("src/app/")
        elif "svelte" in dep_names:
            stacks.append(
                {
                    "kind": "frontend",
                    "name": "svelte",
                    "confidence": "medium",
                    "signals": ["package.json", "svelte"],
                }
            )

    if pyproject.exists() or requirements_txt.exists():
        languages.add("python")
        package_managers.add("pip")
        signals.append(repo_signal(repo_root, "pyproject.toml" if pyproject.exists() else "requirements.txt", "python"))
        py_text = safe_read_text(pyproject if pyproject.exists() else requirements_txt)
        if "fastapi" in py_text.lower():
            stacks.append({"kind": "backend", "name": "fastapi", "confidence": "high", "signals": ["python", "fastapi"]})
        elif "django" in py_text.lower():
            stacks.append({"kind": "backend", "name": "django", "confidence": "medium", "signals": ["python", "django"]})
        elif "flask" in py_text.lower():
            stacks.append({"kind": "backend", "name": "flask", "confidence": "medium", "signals": ["python", "flask"]})

    if cargo_toml.exists():
        languages.add("rust")
        package_managers.add("cargo")
        signals.append(repo_signal(repo_root, "Cargo.toml", "rust"))
        stacks.append({"kind": "backend", "name": "rust", "confidence": "medium", "signals": ["Cargo.toml"]})

    if go_mod.exists():
        languages.add("go")
        package_managers.add("go")
        signals.append(repo_signal(repo_root, "go.mod", "go"))
        stacks.append({"kind": "backend", "name": "go", "confidence": "medium", "signals": ["go.mod"]})

    for candidate in ("src/router", "src/routes", "src/pages", "src/app", "app", "pages", "web", "frontend"):
        if (repo_root / candidate).exists():
            frontend_entry_hints.append(candidate)

    has_frontend_source = any(frontend_entry_hints)
    if has_frontend_source and not any(stack["kind"] == "frontend" for stack in stacks):
        stacks.append(
            {
                "kind": "frontend",
                "name": "frontend-source-present",
                "confidence": "low",
                "signals": sorted(set(frontend_entry_hints))[:4],
            }
        )

    normalized_stacks: list[dict[str, Any]] = []
    seen = set()
    for stack in stacks:
        key = (stack["kind"], stack["name"])
        if key in seen:
            continue
        seen.add(key)
        normalized_stacks.append(stack)

    return {
        "repo_root": str(repo_root),
        "repo_name": repo_root.name,
        "languages": sorted(languages),
        "package_managers": sorted(package_managers),
        "has_frontend_source": has_frontend_source,
        "frontend_entry_hints": sorted(set(frontend_entry_hints)),
        "signals": signals,
        "stacks": normalized_stacks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect repository stack signals.")
    parser.add_argument("--repo", required=True, help="Repository root path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    payload = detect_stack(Path(args.repo))
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
