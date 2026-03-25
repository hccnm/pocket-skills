#!/usr/bin/env python3
"""Extract repository facts for PRD generation."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from detect_stack import detect_stack


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

MAX_TEXT_BYTES = 300_000
JAVA_ROUTE_ANNOTATION = re.compile(
    r"(?P<annotation>@(?:Get|Post|Put|Delete|Patch|Request)Mapping\s*\((?P<params>.*?)\))",
    re.S,
)
TS_CONTROLLER_BLOCK = re.compile(
    r"@Controller\s*\((?P<params>.*?)\)\s*export\s+class\s+(?P<class_name>\w+)",
    re.S,
)
TS_METHOD_BLOCK = re.compile(
    r"(?P<annotations>(?:\s*@(?:Get|Post|Put|Delete|Patch|All)\s*\(.*?\)\s*)+)"
    r"\s*(?:async\s+)?(?P<method>\w+)\s*\(",
    re.S,
)
EXPRESS_ROUTE_BLOCK = re.compile(r"\b(?:router|app)\.(get|post|put|delete|patch|all)\(\s*['\"]([^'\"]+)['\"]")


def safe_read_text(path: Path, max_bytes: int = MAX_TEXT_BYTES) -> str:
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


def iter_repo_files(repo_root: Path, suffixes: tuple[str, ...] | None = None) -> Iterable[Path]:
    for path in repo_root.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if suffixes and path.suffix.lower() not in suffixes:
            continue
        yield path


def relpath(path: Path, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve()))


def first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def parse_pom_modules(repo_root: Path) -> list[str]:
    pom_xml = repo_root / "pom.xml"
    if not pom_xml.exists():
        return []
    text = safe_read_text(pom_xml)
    return sorted(set(re.findall(r"<module>(.*?)</module>", text)))


def extract_java_class_info(content: str) -> tuple[str, str]:
    package_match = re.search(r"package\s+([\w\.]+)\s*;", content)
    class_match = re.search(r"\bclass\s+(\w+)", content)
    return (
        package_match.group(1) if package_match else "",
        class_match.group(1) if class_match else "",
    )


def extract_annotation_paths(params: str) -> list[str]:
    explicit = re.findall(r"(?:value|path)\s*=\s*\"([^\"]+)\"", params)
    if explicit:
        return explicit
    bare = re.findall(r"\"([^\"]+)\"", params)
    return bare or [""]


def extract_request_methods(params: str) -> list[str]:
    methods = re.findall(r"RequestMethod\.([A-Z]+)", params)
    return methods or ["ANY"]


def join_routes(class_path: str, method_path: str) -> str:
    segments = []
    for part in (class_path, method_path):
        if not part:
            continue
        normalized = "/" + part.strip().strip("/")
        if normalized == "/":
            continue
        segments.append(normalized)
    if not segments:
        return "/"
    merged = "".join(segments)
    return re.sub(r"//+", "/", merged)


def extract_call_hints_from_body(body: str) -> list[str]:
    hints = re.findall(
        r"\b(\w+(?:Service|Facade|Manager|Validator|Processor|Mapper|Repository|Client))\s*\.\s*(\w+)\s*\(",
        body,
    )
    cleaned = []
    seen = set()
    for owner, method in hints:
        joined = f"{owner}.{method}"
        if joined in seen:
            continue
        seen.add(joined)
        cleaned.append(joined)
    return cleaned[:12]


def extract_method_body(lines: list[str], start_index: int) -> str:
    collected: list[str] = []
    brace_depth = 0
    started = False
    for index in range(start_index, min(len(lines), start_index + 160)):
        line = lines[index]
        collected.append(line)
        open_count = line.count("{")
        close_count = line.count("}")
        if open_count:
            started = True
        brace_depth += open_count
        brace_depth -= close_count
        if started and brace_depth <= 0:
            break
    return "\n".join(collected)


def extract_java_class_mapping(content: str, class_name: str) -> list[str]:
    if not class_name:
        return [""]
    class_index = content.find(f"class {class_name}")
    header = content[:class_index] if class_index >= 0 else content
    matches = list(JAVA_ROUTE_ANNOTATION.finditer(header))
    if not matches:
        return [""]
    annotation = matches[-1]
    if "RequestMapping" not in annotation.group("annotation"):
        return [""]
    return extract_annotation_paths(annotation.group("params"))


def parse_java_controllers(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    controllers: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []

    for path in iter_repo_files(repo_root, (".java",)):
        relative = relpath(path, repo_root)
        if "controller" not in relative.lower():
            continue
        content = safe_read_text(path)
        if "@RequestMapping" not in content and "Mapping(" not in content:
            continue
        package_name, class_name = extract_java_class_info(content)
        class_paths = extract_java_class_mapping(content, class_name)
        controller_record = {
            "language": "java",
            "framework": "spring",
            "path": relative,
            "package": package_name,
            "class_name": class_name or path.stem,
            "base_paths": class_paths,
        }
        controllers.append(controller_record)

        in_class_body = False
        annotation_buffer: list[str] = []
        lines = content.splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not in_class_body and f"class {controller_record['class_name']}" in stripped:
                in_class_body = True
                annotation_buffer.clear()
                continue
            if not in_class_body:
                continue
            if stripped.startswith("@"):
                annotation_buffer.append(stripped)
                continue
            method_match = re.search(r"\b(public|protected|private)\b.*?\b(\w+)\s*\(", stripped)
            if not method_match:
                if stripped:
                    annotation_buffer.clear()
                continue
            method_name = method_match.group(2)
            annotation_block = "\n".join(annotation_buffer)
            annotation_buffer.clear()
            if "Mapping(" not in annotation_block:
                continue
            method_body = extract_method_body(lines, index)
            call_hints = extract_call_hints_from_body(method_body)
            for annotation in JAVA_ROUTE_ANNOTATION.finditer(annotation_block):
                annotation_text = annotation.group("annotation")
                params = annotation.group("params")
                if "@GetMapping" in annotation_text:
                    methods = ["GET"]
                elif "@PostMapping" in annotation_text:
                    methods = ["POST"]
                elif "@PutMapping" in annotation_text:
                    methods = ["PUT"]
                elif "@DeleteMapping" in annotation_text:
                    methods = ["DELETE"]
                elif "@PatchMapping" in annotation_text:
                    methods = ["PATCH"]
                else:
                    methods = extract_request_methods(params)
                paths = extract_annotation_paths(params)
                for class_path in class_paths:
                    for method_path in paths:
                        routes.append(
                            {
                                "language": "java",
                                "framework": "spring",
                                "controller": controller_record["class_name"],
                                "path": relative,
                                "method_name": method_name,
                                "http_methods": methods,
                                "route": join_routes(class_path, method_path),
                                "call_hints": call_hints,
                            }
                        )

    return controllers, routes


def parse_ts_controllers(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    controllers: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []

    for path in iter_repo_files(repo_root, (".ts", ".tsx")):
        relative = relpath(path, repo_root)
        content = safe_read_text(path)
        if "@Controller" in content:
            for controller_match in TS_CONTROLLER_BLOCK.finditer(content):
                class_name = controller_match.group("class_name")
                class_paths = extract_annotation_paths(controller_match.group("params"))
                controller_record = {
                    "language": "typescript",
                    "framework": "nestjs",
                    "path": relative,
                    "package": "",
                    "class_name": class_name,
                    "base_paths": class_paths,
                }
                controllers.append(controller_record)
                for method_match in TS_METHOD_BLOCK.finditer(content):
                    annotation_block = method_match.group("annotations")
                    method_name = method_match.group("method")
                    method_body_start = method_match.end()
                    method_body = content[method_body_start : method_body_start + 2500]
                    call_hints = extract_call_hints_from_body(method_body)
                    verb_map = {
                        "@Get": "GET",
                        "@Post": "POST",
                        "@Put": "PUT",
                        "@Delete": "DELETE",
                        "@Patch": "PATCH",
                        "@All": "ANY",
                    }
                    for verb_token, verb in verb_map.items():
                        if verb_token not in annotation_block:
                            continue
                        method_paths = extract_annotation_paths(annotation_block)
                        for class_path in class_paths:
                            for method_path in method_paths:
                                routes.append(
                                    {
                                        "language": "typescript",
                                        "framework": "nestjs",
                                        "controller": class_name,
                                        "path": relative,
                                        "method_name": method_name,
                                        "http_methods": [verb],
                                        "route": join_routes(class_path, method_path),
                                        "call_hints": call_hints,
                                    }
                                )
        if "router." in content or "app." in content:
            controller_name = path.stem
            controllers.append(
                {
                    "language": "javascript",
                    "framework": "express-like",
                    "path": relative,
                    "package": "",
                    "class_name": controller_name,
                    "base_paths": [""],
                }
            )
            for method, route_path in EXPRESS_ROUTE_BLOCK.findall(content):
                routes.append(
                    {
                        "language": "javascript",
                        "framework": "express-like",
                        "controller": controller_name,
                        "path": relative,
                        "method_name": method,
                        "http_methods": [method.upper()],
                        "route": route_path,
                        "call_hints": [],
                    }
                )

    return controllers, routes


def extract_frontend_source_routes(repo_root: Path) -> list[dict[str, Any]]:
    candidates = []
    for path in iter_repo_files(repo_root, (".ts", ".tsx", ".js", ".jsx")):
        relative = relpath(path, repo_root)
        lowered = relative.lower()
        if not any(token in lowered for token in ("router", "route", "menu", "navigation")):
            continue
        content = safe_read_text(path)
        if "path" not in content and "routes" not in lowered:
            continue
        paths = re.findall(r"path\s*:\s*['\"]([^'\"]+)['\"]", content)
        titles = re.findall(r"(?:title|name)\s*:\s*['\"]([^'\"]+)['\"]", content)
        if not paths:
            continue
        candidates.append(
            {
                "path": relative,
                "route_count": len(paths),
                "sample_paths": paths[:20],
                "sample_titles": titles[:20],
            }
        )
    return candidates[:20]


def classify_code_artifacts(repo_root: Path) -> dict[str, list[dict[str, str]]]:
    buckets = defaultdict(list)
    suffixes = (".java", ".kt", ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs")
    for path in iter_repo_files(repo_root, suffixes):
        relative = relpath(path, repo_root)
        lowered = relative.lower()
        if "/src/test/" in lowered:
            continue
        name = path.stem
        for kind in (
            "controller",
            "service",
            "facade",
            "entity",
            "enum",
            "dto",
            "vo",
            "bo",
            "validator",
            "listener",
            "scheduler",
            "queue",
            "processor",
            "mapper",
        ):
            if f"/{kind}/" in lowered or name.lower().endswith(kind):
                buckets[kind].append({"name": name, "path": relative})
    return {key: value[:400] for key, value in buckets.items()}


def extract_integrations(repo_root: Path) -> list[dict[str, str]]:
    config_files = []
    for path in iter_repo_files(repo_root):
        relative = relpath(path, repo_root)
        lowered = relative.lower()
        if path.name in {"pom.xml", "build.gradle", "build.gradle.kts", "package.json"}:
            config_files.append((relative, safe_read_text(path)))
        elif lowered.endswith((".yml", ".yaml", ".properties", ".toml", ".json")) and any(
            token in lowered for token in ("application", "config", "settings")
        ):
            config_files.append((relative, safe_read_text(path)))
    joined = "\n".join(text for _, text in config_files).lower()
    integration_map = {
        "redis": ("redis", "缓存/消息或分布式组件"),
        "mysql": ("mysql", "关系型数据库"),
        "postgres": ("postgres", "关系型数据库"),
        "mongodb": ("mongodb", "文档数据库"),
        "kafka": ("kafka", "消息流"),
        "rabbitmq": ("rabbitmq", "消息队列"),
        "rocketmq": ("rocketmq", "消息队列"),
        "s3": ("s3", "对象存储"),
        "oss": ("oss", "对象存储"),
        "minio": ("minio", "对象存储"),
        "email": ("email", "邮件服务"),
        "mail": ("mail", "邮件服务"),
        "sms": ("sms", "短信服务"),
        "oauth": ("oauth", "第三方登录/授权"),
        "websocket": ("websocket", "实时通信"),
        "openapi": ("openapi", "接口文档"),
        "springdoc": ("springdoc", "接口文档"),
        "jwt": ("jwt", "令牌认证"),
        "sa-token": ("sa-token", "鉴权框架"),
    }
    findings = []
    for keyword, (name, description) in integration_map.items():
        if keyword in joined:
            findings.append({"name": name, "description": description})
    deduped = {}
    for item in findings:
        deduped[item["name"]] = item
    return list(deduped.values())


def extract_markdown_docs(repo_root: Path) -> list[dict[str, str]]:
    docs = []
    for path in iter_repo_files(repo_root, (".md",)):
        relative = relpath(path, repo_root)
        lowered = relative.lower()
        if any(part in IGNORE_DIRS for part in Path(relative).parts):
            continue
        if relative.startswith("."):
            continue
        if lowered.startswith("docs/prd") or "/docs/prd" in lowered:
            continue
        if ".codex/skills" in lowered:
            continue
        text = safe_read_text(path)
        docs.append(
            {
                "path": relative,
                "title": first_heading(text) or path.stem,
            }
        )
    return docs[:400]


def extract_permissions_and_security(repo_root: Path) -> list[dict[str, str]]:
    patterns = {
        "auth": r"@RequestMapping\(\"/auth|/auth/|login|logout|oauth",
        "permission": r"permission|role|tenant|dept",
        "encryption": r"encrypt|decrypt|aes|rsa|sm2",
        "xss": r"\bxss\b",
        "captcha": r"captcha|验证码",
    }
    findings = []
    for path in iter_repo_files(repo_root):
        relative = relpath(path, repo_root)
        lowered = relative.lower()
        if not lowered.endswith((".java", ".kt", ".ts", ".js", ".yml", ".yaml", ".properties", ".md")):
            continue
        text = safe_read_text(path)
        text_lower = text.lower()
        for name, pattern in patterns.items():
            if re.search(pattern, text_lower, re.I):
                findings.append({"name": name, "path": relative})
    deduped = {}
    for item in findings:
        deduped.setdefault(item["name"], item)
    return list(deduped.values())


def extract_scheduler_signals(repo_root: Path) -> list[dict[str, str]]:
    findings = []
    for path in iter_repo_files(repo_root):
        relative = relpath(path, repo_root)
        lowered = relative.lower()
        if "/scheduler/" in lowered or "@scheduled" in safe_read_text(path).lower():
            findings.append({"path": relative, "type": "scheduler"})
        elif "/queue/" in lowered or "/listener/" in lowered or "/consumer/" in lowered:
            findings.append({"path": relative, "type": "async"})
    deduped = []
    seen = set()
    for item in findings:
        key = (item["path"], item["type"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:200]


def extract_java_state_machines(repo_root: Path) -> list[dict[str, Any]]:
    machines: list[dict[str, Any]] = []
    for path in iter_repo_files(repo_root, (".java",)):
        if not path.name.endswith("Status.java"):
            continue
        content = safe_read_text(path)
        if " enum " not in content or "canTransitionTo" not in content:
            continue

        relative = relpath(path, repo_root)
        enum_match = re.search(r"enum\s+(\w+)\s*\{", content)
        if not enum_match:
            continue
        enum_name = enum_match.group(1)

        header_start = enum_match.end()
        header_end = content.find(";", header_start)
        if header_end < 0:
            continue
        header_block = content[header_start:header_end]

        states = []
        for line in header_block.splitlines():
            stripped = line.strip().rstrip(",")
            if not stripped or stripped.startswith("*") or stripped.startswith("/"):
                continue
            match = re.match(r"([A-Z0-9_]+)\((\d+),\s*\"([^\"]+)\"", stripped)
            if match:
                states.append(
                    {
                        "code": match.group(1),
                        "value": int(match.group(2)),
                        "label": match.group(3),
                    }
                )

        final_states = []
        final_method = re.search(r"boolean\s+isFinalStatus\s*\(\)\s*\{(.*?)\n\s*\}", content, re.S)
        if final_method:
            final_states = re.findall(r"return\s+this\s*==\s*([A-Z0-9_]+)", final_method.group(1))

        claimable_states = []
        claimable_method = re.search(r"boolean\s+isClaimable\s*\(\)\s*\{(.*?)\n\s*\}", content, re.S)
        if claimable_method:
            claimable_states = re.findall(
                r"this\s*==\s*([A-Z0-9_]+)", claimable_method.group(1)
            )
        transitions = []
        for case_name, body in re.findall(r"case\s+([A-Z0-9_]+)\s*:\s*(.*?)\s*(?=case\s+[A-Z0-9_]+\s*:|default\s*:)", content, re.S):
            target_codes = re.findall(r"targetStatus\s*==\s*([A-Z0-9_]+)", body)
            if target_codes:
                transitions.append({"from": case_name, "to": target_codes})

        special_rules = []
        if final_states:
            special_rules.append(f"终态候选：{', '.join(sorted(set(final_states)))}")
        if claimable_states:
            special_rules.append(f"可认领候选：{', '.join(sorted(set(claimable_states)))}")
        if "CANCELLED状态现在可以转换回SUBMITTED" in content:
            special_rules.append("取消状态可重新回到已提交。")
        if "DELIVERED是唯一的终态状态" in content:
            special_rules.append("配送完成被设计为唯一终态。")

        machines.append(
            {
                "name": enum_name,
                "path": relative,
                "states": states,
                "transitions": transitions,
                "final_states": sorted(set(final_states)),
                "special_rules": special_rules,
            }
        )

    return machines


def summarize_repo_modules(repo_root: Path) -> list[str]:
    modules = parse_pom_modules(repo_root)
    if modules:
        return modules
    top_level = []
    for child in repo_root.iterdir():
        if child.name in IGNORE_DIRS or child.name.startswith("."):
            continue
        if child.is_dir():
            top_level.append(child.name)
    return sorted(top_level)


def build_payload(repo_root: Path) -> dict[str, Any]:
    stack_info = detect_stack(repo_root)
    java_controllers, java_routes = parse_java_controllers(repo_root)
    ts_controllers, ts_routes = parse_ts_controllers(repo_root)
    controllers = java_controllers + ts_controllers
    routes = java_routes + ts_routes
    route_counter = Counter()
    for route in routes:
        route_counter[route["route"]] += 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root.resolve()),
        "repo_name": repo_root.resolve().name,
        "stack": stack_info,
        "repo_modules": summarize_repo_modules(repo_root),
        "docs": extract_markdown_docs(repo_root),
        "controllers": controllers,
        "routes": routes,
        "frontend_source_routes": extract_frontend_source_routes(repo_root),
        "code_artifacts": classify_code_artifacts(repo_root),
        "integrations": extract_integrations(repo_root),
        "security_signals": extract_permissions_and_security(repo_root),
        "scheduler_signals": extract_scheduler_signals(repo_root),
        "state_machines": extract_java_state_machines(repo_root),
        "stats": {
            "controller_count": len(controllers),
            "route_count": len(routes),
            "document_count": len(extract_markdown_docs(repo_root)),
            "duplicate_route_count": sum(1 for count in route_counter.values() if count > 1),
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract code facts from a repository.")
    parser.add_argument("--repo", required=True, help="Repository root path")
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    payload = build_payload(repo_root)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty or args.output else None)

    if args.output:
        Path(args.output).write_text(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
