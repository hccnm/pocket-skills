#!/usr/bin/env python3
"""Extract frontend source evidence from a React/TypeScript codebase."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAGE_TITLE_HINTS = {
    "MyTasks": "个人任务",
    "OrderHall": "订单大厅",
    "OrderSearch": "订单查询",
    "FinanceAuditOrders": "财务审核订单",
    "Announcement": "公告管理",
    "DailyDeliveryOrders": "每日配送订单",
    "CommunityActivity": "社区活动管理",
    "PeripheralOrder": "周边订单大厅",
    "blueBagStock": "蓝包查询",
    "OrderDashboard": "订单仪表盘",
    "ReportCenter": "数据表",
    "settings": "供应商配置",
    "order": "供应商订单",
    "channel": "渠道管理",
    "user": "用户管理",
    "role": "角色管理",
    "push": "推送管理",
    "menu": "菜单管理",
    "dept": "主体管理",
    "dict": "字典管理",
    "oss": "文件管理",
}

MODULE_HINTS = {
    "MyTasks": "workflow",
    "OrderHall": "orders",
    "OrderSearch": "orders",
    "FinanceAuditOrders": "finance",
    "Announcement": "announcement",
    "DailyDeliveryOrders": "daily-delivery-orders",
    "CommunityActivity": "community-activity",
    "PeripheralOrder": "peripheral-order",
    "blueBagStock": "blue-bag-stock",
    "OrderDashboard": "statistics",
    "ReportCenter": "statistics",
    "settings": "supplier-config",
    "order": "supplier",
    "channel": "channel",
    "user": "user",
    "role": "role",
    "push": "push",
    "menu": "menu",
    "dept": "dept",
    "dict": "dict",
    "oss": "file",
}

COMMON_HELPER_LABELS = {
    "getOrderNoColumn": "订单号",
    "getSystemOrderNoColumn": "系统订单编号",
    "getDidColumn": "玩家ID",
    "getContactNameColumn": "联系人",
    "getVipLevelColumn": "VIP等级",
    "getOrderStatusColumn": "订单状态",
    "getChannelTypeColumn": "渠道类型",
    "getOrderOriginColumn": "订单来源",
    "getThirdOrderIdColumn": "第三方订单ID",
    "getReceiverNameColumn": "收件人",
    "getContactPhoneColumn": "联系电话",
    "getRemarkColumn": "操作备注",
    "getUserRemarkColumn": "用户备注",
    "getErrorMessageColumn": "错误信息",
    "getCreatedAtColumn": "创建时间",
    "getUpdatedAtColumn": "更新时间",
    "getDeliveryTimeColumn": "配送时间",
    "getActualPaymentAmountColumn": "实际支付金额",
    "getPaymentStatusColumn": "支付状态",
    "getAttachmentColumn": "附件",
}

MODAL_NAME_HINTS = {
    "AdvancedManage": "高级订单管理",
    "BatchAssign": "批量指派订单",
    "ResubmitFinanceAudit": "重新提交财务审核",
    "SupplementOrder": "创建补单",
    "StartDelivery": "开始订单配送",
    "MarkInfoError": "标记信息错误",
    "StatusManage": "状态管理",
    "AttachmentManage": "管理附件",
    "RoleForm": "新增/编辑角色",
    "UserForm": "新增/编辑用户",
    "DataScope": "数据权限配置",
    "ResetPassword": "重置密码",
    "AddUser": "添加用户",
}

ROUTE_ACTION_HINTS = {
    "order-realtime": "查询实时订单报表",
    "order-production-sales": "查询订单产销报表",
    "personal-order-processing": "查询个人订单处理报表",
    "supplier-settlement": "查询供应商结算报表",
    "my-claimed": "查看个人已认领订单",
    "claim-next": "一键认领订单",
    "advanced-manage": "高级订单管理",
    "batch-assign": "批量指派订单",
    "export-excel": "导出订单大厅 Excel",
    "dataScope": "配置数据权限",
    "changeStatus": "修改启用状态",
    "resetPwd": "重置密码",
    "importTemplate": "下载导入模板",
    "importData": "导入数据",
    "optionselect": "获取下拉选项",
    "deptTree": "获取主体树",
    "authRole": "分配角色",
    "authUser": "分配用户",
    "allocatedList": "查询已授权用户列表",
    "unallocatedList": "查询未授权用户列表",
    "detail": "查看详情",
    "timeline": "查看处理时间线",
    "history": "查看历史记录",
    "attachments": "更新订单附件",
    "supplement": "创建补单",
}

ENTITY_LABEL_HINTS = {
    "announcement": "公告",
    "order": "订单",
    "orders": "订单",
    "supplier": "供应商",
    "role": "角色",
    "user": "用户",
    "menu": "菜单",
    "dict": "字典",
    "dept": "主体",
    "channel": "渠道",
    "push": "推送",
    "file": "文件",
    "oss": "文件",
    "activity": "活动",
    "stock": "库存",
    "report": "报表",
}

IGNORE_PAGE_DIRS = {"components", "hooks", "config", "types", "utils", "columns", "services"}
SERVICE_CALL_RE = re.compile(
    r"(?P<comment>/\*\*.*?\*/)?\s*(?P<method>\w+)\s*:\s*async\s*\([^)]*\)\s*:\s*Promise<.*?>\s*=>\s*\{\s*return\s+await\s+network\.(?P<http>Get|Post|Put|Delete|Patch)\(\s*[`'\"](?P<url>[^`'\"]+)",
    re.S,
)
HELPER_CALL_RE = re.compile(r"(?P<helper>get[A-Za-z0-9]+Column)\s*<[^>]*>\s*\(.*?(?P<options>\{.*?\})?\)", re.S)
TITLE_LITERAL_RE = re.compile(r"title\s*:\s*[`'\"](?P<title>[^`'\"]+)[`'\"]")
TITLE_T_RE = re.compile(r"title\s*:\s*t\([`'\"](?P<key>[^`'\"]+)[`'\"]\)")
FIELD_LABEL_RE = re.compile(r"label\s*=\s*[\"'`](?P<label>[^\"'`]+)[\"'`]")
DIALOG_TITLE_RE = re.compile(r"title\s*=\s*[\"'`](?P<title>[^\"'`]+)[\"'`]")
COMMENT_TITLE_RE = re.compile(r"/\*\*.*?\*\s*(?P<title>[^*\n]+页面(?:组件)?)", re.S)
BUTTON_LITERAL_RE = re.compile(r">\s*(?P<label>[\u4e00-\u9fffA-Za-z0-9]+)\s*<")
T_EXPR_RE = re.compile(r"t\([`'\"](?P<key>[^`'\"]+)[`'\"]\)")
LABEL_T_RE = re.compile(r"label\s*=\s*\{?\s*t\([`'\"](?P<key>[^`'\"]+)[`'\"]\)\s*\}?")
MODAL_TITLE_LITERAL_RE = re.compile(r"<Modal[^>]*title\s*=\s*[\"'`](?P<title>[^\"'`]+)[\"'`]", re.S)
MODAL_TITLE_T_EXPR_RE = re.compile(r"<Modal[^>]*title\s*=\s*\{?\s*t\([`'\"](?P<key>[^`'\"]+)[`'\"]\)\s*\}?", re.S)
MODAL_TITLE_CONDITIONAL_T_RE = re.compile(
    r"<Modal[^>]*title\s*=\s*\{[^}]*t\([`'\"](?P<first>[^`'\"]+)[`'\"]\)[^}]*t\([`'\"](?P<second>[^`'\"]+)[`'\"]\)[^}]*\}",
    re.S,
)
FORM_ITEM_LITERAL_RE = re.compile(r"<(?:ProForm\w+|Form\.Item)[^>]*label\s*=\s*[\"'`](?P<label>[^\"'`]+)[\"'`]", re.S)
FORM_ITEM_T_RE = re.compile(r"<(?:ProForm\w+|Form\.Item)[^>]*label\s*=\s*\{?\s*t\([`'\"](?P<key>[^`'\"]+)[`'\"]\)\s*\}?", re.S)


def safe_read(path: Path) -> str:
    try:
        return path.read_text()
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def locale_namespace_parts(path: Path, root: Path) -> list[str]:
    parts = list(path.relative_to(root).with_suffix("").parts)
    if parts and parts[-1] == "index":
        parts.pop()
    return parts


def flatten_locale_translations(text: str, prefix: list[str]) -> dict[str, str]:
    translations: dict[str, str] = {}
    stack: list[str] = []
    value_re = re.compile(r"(?P<key>[A-Za-z0-9_]+)\s*:\s*(?P<quote>['\"])(?P<value>.*?)(?<!\\)(?P=quote)\s*,?$")
    object_start_re = re.compile(r"(?P<key>[A-Za-z0-9_]+)\s*:\s*\{\s*,?$")

    for raw_line in text.splitlines():
        line = re.sub(r"//.*", "", raw_line).strip()
        if not line:
            continue
        value_match = value_re.match(line)
        if value_match:
            key = value_match.group("key")
            value = value_match.group("value").strip()
            translations[".".join(prefix + stack + [key])] = value
            continue
        object_match = object_start_re.match(line)
        if object_match:
            stack.append(object_match.group("key"))
            continue
        close_count = line.count("}")
        while close_count > 0 and stack:
            stack.pop()
            close_count -= 1
    return translations


def load_translation_hints(frontend_repo: Path) -> dict[str, str]:
    translations: dict[str, str] = {}
    locales_root = frontend_repo / "apps/admin/src/locales/langs/zh-cn"
    if not locales_root.exists():
        return translations
    for path in locales_root.rglob("*.ts"):
        text = safe_read(path)
        translations.update(flatten_locale_translations(text, locale_namespace_parts(path, locales_root)))
    return translations


def translate_key(key: str, translations: dict[str, str]) -> str:
    if key in translations:
        return translations[key]
    leaf = key.split(".")[-1]
    candidates = [value for candidate_key, value in translations.items() if candidate_key == leaf or candidate_key.endswith(f".{leaf}")]
    unique = list(dict.fromkeys(candidates))
    if len(unique) == 1:
        return unique[0]
    return leaf


def humanize_camel(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value).replace("-", " ").replace("_", " ").strip()


def path_route(relative_dir: Path) -> str:
    return "#/" + "/".join(relative_dir.parts)


def infer_title(relative_dir: Path, index_text: str) -> str:
    for part in reversed(relative_dir.parts):
        if part in PAGE_TITLE_HINTS:
            return PAGE_TITLE_HINTS[part]
    comment_match = COMMENT_TITLE_RE.search(index_text)
    if comment_match:
        title = comment_match.group("title").strip()
        title = title.replace("页面组件", "").replace("页面", "").strip()
        if title:
            return title
    return humanize_camel(relative_dir.name)


def infer_module_hint(relative_dir: Path) -> str:
    for part in reversed(relative_dir.parts):
        if part in MODULE_HINTS:
            return MODULE_HINTS[part]
    return relative_dir.name


def infer_menu_title(relative_dir: Path) -> tuple[str, list[str]]:
    parts = list(relative_dir.parts)
    if not parts:
        return "", []
    if parts[0] == "Dashboard":
        parent = "仪表盘"
    elif parts[0] == "Supplier":
        parent = "供应商管理"
    elif parts[0] == "system":
        parent = "系统管理"
    else:
        parent = ""
    title = PAGE_TITLE_HINTS.get(parts[-1], humanize_camel(parts[-1]))
    breadcrumbs = [parent, title] if parent else [title]
    return title, breadcrumbs


def extract_request_path(url: str) -> str:
    return re.sub(r"/{2,}", "/", url.split("?")[0].strip())


def looks_like_noise_comment(comment: str) -> bool:
    if not comment:
        return True
    lowered = comment.lower()
    if any(lowered.startswith(prefix) for prefix in ("说明：", "todo", "fixme", "//")):
        return True
    if "全局拦截" in comment or "code/msg" in lowered:
        return True
    return False


def clean_comment_text(comment: str) -> str:
    cleaned = re.sub(r"\s+", " ", comment).strip()
    cleaned = cleaned.replace("接口服务", "").replace("接口", "").strip()
    cleaned = cleaned.replace("修改保存", "修改").replace("状态修改", "修改状态").strip()
    if cleaned.startswith("获取") and ("列表" in cleaned or "报表" in cleaned):
        cleaned = "查询" + cleaned[2:]
    return cleaned


def entity_label_from_path(path: str) -> str:
    segments = [segment for segment in extract_request_path(path).strip("/").split("/") if segment]
    for segment in reversed(segments):
        if segment in ENTITY_LABEL_HINTS:
            return ENTITY_LABEL_HINTS[segment]
    return ""


def action_from_route(method_name: str, url: str, http_method: str) -> str:
    path = extract_request_path(url)
    lowered_path = path.lower()
    for token, label in ROUTE_ACTION_HINTS.items():
        if token.lower() in lowered_path or token.lower() in method_name.lower():
            return label

    entity = entity_label_from_path(lowered_path)
    lowered_method = method_name.lower()
    if lowered_method.startswith(("get", "list", "query", "fetch")):
        return f"查询{entity}列表" if entity else "执行查询"
    if lowered_method.startswith(("create", "add")):
        return f"新增{entity}" if entity else "执行新增"
    if lowered_method.startswith(("update", "edit", "save", "modify")):
        return f"修改{entity}" if entity else "执行修改"
    if lowered_method.startswith(("delete", "remove")):
        return f"删除{entity}" if entity else "执行删除"
    if lowered_method.startswith("export"):
        return f"导出{entity}列表" if entity else "导出结果"
    if lowered_method.startswith("import"):
        return f"导入{entity}数据" if entity else "导入数据"
    if http_method == "GET":
        return f"查询{entity}信息" if entity else "读取页面数据"
    if http_method == "POST":
        return f"新增{entity}" if entity else "提交业务操作"
    if http_method in {"PUT", "PATCH"}:
        return f"修改{entity}" if entity else "更新业务对象"
    if http_method == "DELETE":
        return f"删除{entity}" if entity else "删除业务对象"
    return humanize_camel(method_name)


def normalize_action_name(method_name: str, url: str, http_method: str, raw_comment: str) -> str:
    comment = clean_comment_text(raw_comment)
    if comment and not looks_like_noise_comment(comment):
        return comment
    return action_from_route(method_name, url, http_method)


def parse_service_requests(service_text: str, page_title: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    requests: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for idx, match in enumerate(SERVICE_CALL_RE.finditer(service_text), start=1):
        raw_comment = match.group("comment") or ""
        comment_lines = []
        for line in raw_comment.splitlines():
            cleaned = line.strip().lstrip("/*").strip()
            if not cleaned or cleaned.startswith("@") or cleaned.startswith("说明：") or cleaned.startswith("TODO") or cleaned.startswith("FIXME"):
                continue
            comment_lines.append(cleaned)
        comment = comment_lines[-1] if comment_lines else ""
        method_name = match.group("method")
        http_method = match.group("http").upper()
        url = match.group("url")
        action_name = normalize_action_name(method_name, url, http_method, comment)
        request_id = f"{page_title}-{method_name}-{idx}".replace(" ", "-")
        requests.append(
            {
                "id": request_id,
                "method": http_method,
                "url": url,
                "page_title": page_title,
            }
        )
        actions.append(
            {
                "name": action_name or humanize_camel(method_name),
                "type": "action",
                "purpose": "",
                "method_name": method_name,
                "method": http_method,
                "url": url,
            }
        )
    return requests, actions


def classify_column(title: str, searchable: bool) -> dict[str, str]:
    return {"name": title, "type": "text" if searchable else "column", "purpose": ""}


def parse_helper_columns(text: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    filters: list[dict[str, str]] = []
    columns: list[dict[str, str]] = []
    for match in HELPER_CALL_RE.finditer(text):
        helper = match.group("helper")
        label = COMMON_HELPER_LABELS.get(helper)
        if not label:
            continue
        options = match.group("options") or ""
        searchable = "searchable: true" in options
        target = filters if searchable else columns
        target.append(classify_column(label, searchable))
        if searchable:
            columns.append({"name": label, "type": "column", "purpose": ""})
    return filters, columns


def parse_inline_columns(text: str, translations: dict[str, str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    filters: list[dict[str, str]] = []
    columns: list[dict[str, str]] = []
    titles: list[tuple[str, int]] = []
    for match in TITLE_LITERAL_RE.finditer(text):
        titles.append((match.group("title").strip(), match.start()))
    for match in TITLE_T_RE.finditer(text):
        key = match.group("key").strip()
        label = translate_key(key, translations)
        titles.append((label, match.start()))
    titles.sort(key=lambda item: item[1])
    for title, start in titles:
        if not title:
            continue
        window = text[start : start + 260]
        searchable = "search: false" not in window and "hideInSearch: true" not in window and "searchable: false" not in window
        if searchable:
            filters.append(classify_column(title, True))
        columns.append({"name": title, "type": "column", "purpose": ""})
    return filters, columns


def dedupe_items(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    result = []
    for item in items:
        key = item["name"]
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def is_noise_filter_label(name: str) -> bool:
    if not name:
        return True
    if name in {"操作", "operation", "action"}:
        return True
    if name in {"标记信息错误", "挂起订单", "查看附件"}:
        return True
    if re.fullmatch(r"[a-z][A-Za-z0-9]+", name):
        return True
    return False


def is_noise_dialog_label(name: str) -> bool:
    if not name:
        return True
    if name.startswith(("请输入", "请选择", "请说明", "请详细", "确认")):
        return True
    if name in {"提交", "取消", "确定", "重置"}:
        return True
    return False


def parse_dialogs(components_dir: Path, translations: dict[str, str]) -> list[dict[str, Any]]:
    dialogs: list[dict[str, Any]] = []
    if not components_dir.exists():
        return dialogs
    for modal in sorted(components_dir.rglob("*Modal.tsx")):
        text = safe_read(modal)
        stem = modal.stem.replace("Modal", "")
        title = MODAL_NAME_HINTS.get(stem, PAGE_TITLE_HINTS.get(stem, humanize_camel(stem)))
        labels = [m.group("label").strip() for m in FORM_ITEM_LITERAL_RE.finditer(text)]
        labels.extend(translate_key(m.group("key"), translations) for m in FORM_ITEM_T_RE.finditer(text))
        conditional_title = MODAL_TITLE_CONDITIONAL_T_RE.search(text)
        literal_title = MODAL_TITLE_LITERAL_RE.search(text)
        translated_title = MODAL_TITLE_T_EXPR_RE.search(text)
        if conditional_title:
            first = translate_key(conditional_title.group("first"), translations)
            second = translate_key(conditional_title.group("second"), translations)
            if first and second:
                title = f"{second}/{first}" if first != second else first
        elif literal_title:
            title = literal_title.group("title").strip()
        elif translated_title:
            title = translate_key(translated_title.group("key"), translations)
        unique_labels: list[str] = []
        seen_labels = set()
        for label in labels:
            if is_noise_dialog_label(label) or label in seen_labels:
                continue
            seen_labels.add(label)
            unique_labels.append(label)
        dialogs.append(
            {
                "name": title,
                "description": "",
                "fields": [{"name": label, "type": "input", "purpose": ""} for label in unique_labels[:20]],
                "actions": [],
            }
        )
    return dialogs


def parse_status_terms(texts: list[str]) -> list[str]:
    joined = "\n".join(texts)
    hits = re.findall(r"ORDER_STATUS(?:_[A-Z]+)?\.([A-Z_]+)", joined)
    mapping = {
        "SUBMITTED": "已提交",
        "CLAIMED": "已认领",
        "DELIVERING": "配送中",
        "COMPLETED": "配送完成",
        "INFO_ERROR": "信息错误",
        "INFO_MODIFIED": "信息已修改",
        "SUSPENDED": "已挂起",
        "PENDING": "待审核",
    }
    results = []
    for hit in hits:
        results.append(mapping.get(hit, hit))
    return list(dict.fromkeys(results))


def parse_empty_state(index_text: str) -> str:
    if "Empty" in index_text:
        literals = BUTTON_LITERAL_RE.findall(index_text)
        for label in literals:
            if "暂无" in label or "无数据" in label:
                return label
    return ""


def find_pages_root(frontend_repo: Path) -> Path:
    candidates = [
        frontend_repo / "apps/admin/src/pages",
        frontend_repo / "src/pages",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Unable to locate frontend pages root")


def build_page_record(pages_root: Path, page_dir: Path, translations: dict[str, str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    relative_dir = page_dir.relative_to(pages_root)
    index_path = page_dir / "index.tsx"
    service_path = page_dir / "services" / "index.ts"
    primary_columns = [
        page_dir / "columns" / "index.tsx",
        page_dir / "columns" / "index.ts",
        page_dir / "columns.tsx",
        page_dir / "columns.ts",
    ]
    columns_candidates = [path for path in primary_columns if path.exists()]
    if not columns_candidates:
        columns_candidates = [path for path in page_dir.glob("columns/*.tsx") if path.name == "index.tsx"]
    config_candidates = list(page_dir.glob("config/*.ts")) + list(page_dir.glob("config/index.ts"))
    index_text = safe_read(index_path)
    service_text = safe_read(service_path)
    columns_text = "\n".join(safe_read(path) for path in columns_candidates)
    config_text = "\n".join(safe_read(path) for path in config_candidates)
    title = infer_title(relative_dir, index_text)
    _, breadcrumbs = infer_menu_title(relative_dir)
    network_requests, service_actions = parse_service_requests(service_text, title)
    helper_filters, helper_columns = parse_helper_columns(columns_text)
    inline_filters, inline_columns = parse_inline_columns(columns_text, translations)
    filters = dedupe_items(helper_filters + inline_filters)
    if "search={false}" in index_text or "search: false" in index_text:
        filters = []
    else:
        filters = [item for item in filters if not is_noise_filter_label(item["name"])]
    table_columns = dedupe_items(helper_columns + inline_columns)
    dialogs = parse_dialogs(page_dir / "components", translations)
    statuses = parse_status_terms([index_text, columns_text, config_text])

    page = {
        "title": title,
        "route": path_route(relative_dir),
        "breadcrumbs": breadcrumbs,
        "module_hint": infer_module_hint(relative_dir),
        "capture_status": "full",
        "filters": filters,
        "table_columns": table_columns,
        "actions": dedupe_items(service_actions),
        "bulk_actions": [],
        "row_actions": [],
        "metrics": [],
        "charts": [],
        "statuses": statuses,
        "dialogs": dialogs,
        "empty_state": parse_empty_state(index_text),
        "description": "",
        "network_refs": [item["id"] for item in network_requests],
    }
    return page, network_requests


def build_menus(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[str]] = {}
    for page in pages:
        breadcrumbs = page.get("breadcrumbs", [])
        if len(breadcrumbs) > 1:
            grouped.setdefault(breadcrumbs[0], []).append(page["title"])
        else:
            grouped.setdefault(page["title"], [])
    menus = []
    for title, children in grouped.items():
        menus.append({"title": title, "children": list(dict.fromkeys(children))})
    return menus


def extract(frontend_repo: Path) -> dict[str, Any]:
    pages_root = find_pages_root(frontend_repo)
    translations = load_translation_hints(frontend_repo)
    pages: list[dict[str, Any]] = []
    network_requests: list[dict[str, Any]] = []
    for index_path in sorted(pages_root.rglob("index.tsx")):
        page_dir = index_path.parent
        if any(part in IGNORE_PAGE_DIRS for part in page_dir.parts):
            continue
        if page_dir.name in IGNORE_PAGE_DIRS:
            continue
        page, requests = build_page_record(pages_root, page_dir, translations)
        pages.append(page)
        network_requests.extend(requests)

    return {
        "base_url": "",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": str(frontend_repo.resolve()),
        "pages": pages,
        "menus": build_menus(pages),
        "network_requests": network_requests,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract frontend source evidence for PRD generation.")
    parser.add_argument("--frontend-repo", required=True, help="Frontend repository root")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    payload = extract(Path(args.frontend_repo).resolve())
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
