#!/usr/bin/env python3
"""Generate product-first PRD documents from repository facts and optional frontend evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


COMMON_ROUTE_PREFIXES = {"api", "admin", "system", "v1", "v2", "v3"}
BUSINESS_MODULE_BOOST = {
    "orders": 12,
    "player": 11,
    "finance": 10,
    "finance-audit": 10,
    "statistics": 9,
    "supplier": 9,
    "supplier-config": 9,
    "announcement": 8,
    "marketing": 7,
    "greeting-card": 7,
    "activity-uploads": 7,
    "workflow": 6,
}
NON_PRODUCT_MODULE_PENALTY = {
    "demo": -12,
    "tool": -10,
    "monitor": -8,
    "tenant": -7,
    "user": -6,
    "resource": -6,
    "role": -6,
    "menu": -6,
    "dict": -5,
    "dept": -5,
    "config": -5,
}

MODULE_TITLES = {
    "orders": "订单运营",
    "player": "玩家订单",
    "finance": "财务审核",
    "finance-audit": "财务审核",
    "statistics": "经营看板",
    "supplier": "供应商订单",
    "supplier-config": "供应商配置",
    "announcement": "公告运营",
    "workflow": "个人任务",
}

MODULE_POSITIONING = {
    "orders": "负责后台订单池的查询、分派、处理推进、异常回退和状态维护。",
    "player": "承接终端用户的订单提交、查询、修改和配送确认。",
    "finance": "承接配送完成后的财务审核、通过、拒绝和重新提交。",
    "finance-audit": "承接配送完成后的财务审核、通过、拒绝和重新提交。",
    "statistics": "用指标卡和图表展示订单提交、处理、积压和渠道分布情况。",
    "supplier": "向供应商侧提供订单查看、履约跟踪和异常反馈入口。",
    "supplier-config": "用于配置供应商分单规则、展示字段、查询范围和商品映射。",
    "announcement": "用于向渠道或用户发布公告，并维护启用状态与主题表现。",
    "workflow": "用于展示待本人认领或待本人处理的订单任务，并支持快速接单和推进。",
    "community-activity": "用于管理社区活动上传记录、核实结果和导出处理结果。",
    "daily-delivery-orders": "用于按日查看配送订单清单，并支持市场角色导出配送结果。",
    "peripheral-order": "用于处理周边商品订单，包括配送推进、信息错误处理和补单。",
    "blue-bag-stock": "用于查看蓝包相关商品库存明细，辅助活动和履约判断。",
    "channel": "用于管理渠道定义、配置和关联范围，影响订单归属与统计口径。",
    "user": "用于维护后台用户账号、角色绑定、启停状态和组织归属。",
    "role": "用于维护角色、权限范围、菜单授权和数据权限。",
    "menu": "用于维护后台菜单结构、路由可见性和权限节点。",
    "dict": "用于维护字典类型和值，支撑页面枚举、标签和业务选项。",
    "dept": "用于维护组织主体、层级关系和归属结构。",
    "push": "用于维护推送配置、多语言内容和投放规则。",
    "file": "用于管理文件上传、对象存储配置和文件资源。",
    "operlog": "用于查看系统操作日志和行为追踪记录。",
    "orderoperlog": "用于查看订单操作日志、字段差异和历史变更。",
    "logininfor": "用于查看登录日志、访问结果和登录环境信息。",
}

MODULE_DEPENDENCIES = {
    "orders": ["上游来自玩家端订单或导入订单。", "下游会影响财务审核、供应商处理和经营统计。"],
    "player": ["上游面向终端用户。", "下游把订单交给后台订单运营模块继续处理。"],
    "finance": ["上游依赖订单进入可审核阶段。", "下游影响财务结论、异常回退和统计口径。"],
    "finance-audit": ["上游依赖订单进入可审核阶段。", "下游影响财务结论、异常回退和统计口径。"],
    "statistics": ["上游依赖订单、处理状态和审核结果。", "下游服务于运营监控和管理决策。"],
    "supplier": ["上游依赖供应商配置和待履约订单。", "下游影响履约完成状态和异常回写。"],
    "supplier-config": ["上游由运营或管理角色维护。", "下游决定供应商订单可见范围和分单逻辑。"],
    "announcement": ["上游由运营角色创建公告。", "下游影响渠道侧或用户侧的消息展示。"],
    "workflow": ["上游来自订单大厅或系统分配规则。", "下游会把个人处理结果回写到订单主链路和统计结果。"],
}

FIELD_MEANING_HINTS = {
    "订单号": "用于定位单笔业务订单，通常是最常用的检索键。",
    "系统订单编号": "平台内部生成的唯一订单编号，用于跨页面追踪同一订单。",
    "支付订单号": "用于核对支付链路或第三方支付结果。",
    "第三方订单ID": "用于关联外部平台或外部系统中的订单记录。",
    "玩家ID": "用于定位下单用户或玩家主体。",
    "商品活动ID": "用于定位活动、商品批次或营销活动。",
    "订单状态": "描述订单当前处于哪个业务阶段，并决定可执行动作。",
    "VIP等级": "用于判断用户重要度，并影响规则命中或处理优先级。",
    "商品等级": "用于区分不同商品层级或履约难度。",
    "渠道类型": "用于标识订单来自哪个渠道，并影响规则和统计归属。",
    "订单类型": "用于区分业务类型，决定后续处理方式。",
    "审核状态": "描述财务审核当前阶段，如待审核、已通过、已拒绝。",
    "财务审核状态": "描述财务审核当前阶段，如待审核、已通过、已拒绝。",
    "用户信息": "展示下单用户或收件人的识别信息。",
    "联系人": "收件或履约联系人。",
    "联系电话": "联系用户或收件人的电话。",
    "收货地址": "用于判断配送地址、地址异常和履约难度。",
    "联系地址": "供应商履约所需的联系地址。",
    "排队位置": "用于观察订单在处理队列中的相对位置。",
    "认领人": "当前负责处理该订单的人员。",
    "错误信息": "记录异常原因或处理失败信息。",
    "操作备注": "记录运营或处理人员的备注说明。",
    "用户备注": "记录用户提交的补充说明。",
    "发货时间": "反映订单进入履约阶段的时间点。",
    "收货时间": "反映订单完成收货的时间点。",
    "信息错误时间": "反映订单进入信息异常状态的时间点。",
    "附件查看": "用于查看用户或处理人员上传的附件材料。",
    "实际支付金额": "业务实际收取的金额，是财务审核的重要依据。",
    "AI识别金额": "AI 从附件或页面中识别出的金额，用于辅助复核。",
    "AI差值": "实际金额与 AI 识别金额的差异，用于提示异常。",
    "订单操作": "用于选择当前订单要执行的处理动作。",
    "货币": "用于明确金额对应的币种。",
    "重新分配处理人": "用于把订单重新指派给新的处理人员。",
    "订单附件": "用于上传支持审核或处理的凭证材料。",
    "供应商名称": "标识当前规则或订单归属的供应商。",
    "供应商id": "供应商配置的唯一标识。",
    "分单规则": "定义订单何时被路由给该供应商。",
    "查询范围配置": "定义供应商可查看哪些订单。",
    "字段展示配置": "定义供应商页面可看到哪些字段。",
    "是否开启分单": "控制该供应商规则是否参与分单。",
    "优先级": "多个供应商规则命中时的排序依据。",
    "商品配置": "定义供应商和商品、活动之间的对应关系。",
    "标题": "公告标题，用于在列表和详情中展示。",
    "状态": "用于标识当前对象是否启用，或处于哪一个业务处理阶段。",
    "主题颜色": "公告视觉主题色。",
    "渠道": "公告触达的渠道范围，或订单所属渠道。",
    "创建时间": "记录业务对象首次创建时间。",
    "更新时间": "记录业务对象最近一次更新时间。",
    "角色名称": "角色名称，用于区分不同权限组。",
    "权限字符": "权限字符，用于控制角色可访问的菜单与接口范围。",
    "显示顺序": "用于控制角色或菜单在页面中的排序。",
    "用户名称": "用于检索和识别后台账号。",
    "用户昵称": "用于补充展示账号的可读名称。",
    "主体": "用于标识账号所属主体或组织。",
    "手机号码": "用于联系用户并进行身份核验。",
    "邮箱": "用于补充账号联系信息或接收通知。",
    "权限范围": "用于限定角色可访问的数据边界。",
    "账号": "后台登录账号，用于唯一识别用户。",
    "用户密码": "用户登录系统时使用的口令。",
    "用户性别": "用于补充用户基础资料。",
    "新密码": "重置密码时输入的新登录口令。",
    "收件人": "用于展示收货人或履约联系人。",
    "挂起原因": "用于说明订单为什么被暂时挂起等待处理。",
    "配送备注": "用于补充配送阶段的处理说明。",
    "roleName": "角色名称，用于区分不同权限组。",
    "roleKey": "权限字符，用于控制角色可访问的菜单与接口范围。",
    "roleSort": "角色在列表中的显示顺序。",
    "roleNumber": "角色编号，用于唯一标识角色。",
    "userName": "用户名称，用于检索后台账号。",
    "nickName": "用户昵称，用于补充展示账号的可读名称。",
    "phoneNumber": "用户手机号，用于联系与身份核验。",
    "phonenumber": "用户手机号，用于联系与身份核验。",
    "deptName": "主体名称，用于标识账号归属组织。",
    "paymentOrderNo": "用于核对支付链路或第三方支付结果。",
    "activityId": "用于定位活动、商品批次或营销活动。",
    "productLevel": "用于区分不同商品层级或履约难度。",
    "queuePosition": "用于观察订单在处理队列中的相对位置。",
    "claimedByName": "当前负责处理该订单的人员。",
    "infoErrorTime": "反映订单进入信息异常状态的时间点。",
    "aiIdentifiedAmount": "AI 从附件或页面中识别出的金额，用于辅助复核。",
    "amountDifference": "实际金额与 AI 识别金额的差异，用于提示异常。",
    "financeAuditStatus": "描述财务审核当前阶段，如待审核、已通过、已拒绝。",
    "isSupplement": "用于标识订单是否属于补单场景。",
    "currency": "用于明确金额对应的币种。",
    "auditStatus": "描述当前审核阶段，如待审核、已通过、已拒绝。",
    "claimedBy": "当前认领或负责处理该对象的人员。",
    "aiCheckAddress": "AI 对地址相似度或地址匹配结果的检测值，用于辅助复核。",
    "resubmitReason": "重新提交审核时填写的原因说明。",
    "orderCreateTime": "订单最初创建的时间点。",
    "receivedTime": "订单完成收货的时间点。",
    "minOrderCount": "用于筛选达到最少订单数门槛的对象。",
}

FIELD_LABEL_HINTS = {
    "roleName": "角色名称 [推断]",
    "roleKey": "权限字符 [推断]",
    "roleSort": "显示顺序 [推断]",
    "roleNumber": "角色编号 [推断]",
    "userName": "用户名称 [推断]",
    "nickName": "用户昵称 [推断]",
    "phoneNumber": "手机号码 [推断]",
    "phonenumber": "手机号码 [推断]",
    "deptName": "主体名称 [推断]",
    "paymentOrderNo": "支付订单号 [推断]",
    "activityId": "商品活动 ID [推断]",
    "productLevel": "商品等级 [推断]",
    "queuePosition": "排队位置 [推断]",
    "claimedByName": "认领人 [推断]",
    "infoErrorTime": "信息错误时间 [推断]",
    "aiIdentifiedAmount": "AI 识别金额 [推断]",
    "amountDifference": "AI 差值 [推断]",
    "financeAuditStatus": "财务审核状态 [推断]",
    "isSupplement": "是否补单 [推断]",
    "currency": "货币 [推断]",
    "auditStatus": "审核状态 [推断]",
    "claimedBy": "认领人 [推断]",
    "aiCheckAddress": "AI 地址检测相似度 [推断]",
    "resubmitReason": "重新提交原因 [推断]",
    "orderCreateTime": "订单创建时间 [推断]",
    "receivedTime": "收货时间 [推断]",
    "minOrderCount": "最少订单数门槛 [推断]",
}

ACTION_PURPOSE_HINTS = {
    "查询": "根据筛选条件缩小范围，快速定位目标对象。",
    "搜索": "根据筛选条件缩小范围，快速定位目标对象。",
    "重置": "恢复默认筛选条件，重新查看完整数据。",
    "导出": "把当前结果导出为离线台账或报表。",
    "批量指派": "把多笔订单一次性分配给处理人，降低人工重复操作。",
    "批量通过": "批量完成审核通过，提升审核效率。",
    "批量拒绝": "批量完成审核拒绝，快速处理异常订单。",
    "新增供应商": "创建新的供应商规则或供应商主体。",
    "新增公告": "创建新的公告内容，并配置渠道、状态和视觉样式。",
    "编辑": "修改当前对象的业务配置或展示信息。",
    "商品配置": "维护供应商与商品、活动的映射关系。",
    "预览": "在正式发布前查看公告的展示效果。",
    "删除": "移除不再使用的业务对象。",
    "查看附件": "查看支持审核或处理的凭证、截图或材料。",
    "复制": "快速复制关键信息，便于跨系统协同。",
    "确定": "提交当前弹窗中的业务操作。",
    "启用": "让规则或公告正式生效。",
    "禁用": "让规则或公告停止生效。",
    "一键认领": "把公共订单池中的订单快速领取到个人待办中。",
    "重置密码": "为账号设置新的登录密码，恢复账户访问能力。",
    "取消授权": "移除当前用户与角色之间的授权关系。",
    "数据权限": "调整角色可查看的数据范围。",
}

PAGE_ROUTE_HINTS = {
    "订单": ["order", "orders"],
    "任务": ["claim", "task", "my-claimed"],
    "认领": ["claim", "assign"],
    "审核": ["audit", "approve", "reject"],
    "财务": ["finance", "audit"],
    "供应商": ["supplier"],
    "公告": ["announcement", "notice"],
    "渠道": ["channel", "code"],
    "用户": ["user"],
    "角色": ["role"],
    "菜单": ["menu"],
    "字典": ["dict"],
    "文件": ["file"],
    "活动": ["activity", "upload"],
    "配送": ["deliver", "delivery"],
    "状态": ["status"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "module"


def stable_key(value: str) -> str:
    slug = slugify(value)
    if slug != "module":
        return slug
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()[:8]
    return f"page-{digest}"


def titleize_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split("-"))


def meaningful_segments(route: str) -> list[str]:
    cleaned = re.sub(r"\{[^}]+\}", "", route or "")
    parts = [part for part in cleaned.strip("/").split("/") if part]
    while parts and parts[0].lower() in COMMON_ROUTE_PREFIXES:
        parts.pop(0)
    return parts


def module_key_from_route(route: str, controller_name: str) -> str:
    parts = meaningful_segments(route)
    if parts:
        return slugify(parts[0])
    base = re.sub(r"Controller$", "", controller_name or "")
    return slugify(base)


def module_key_from_page(page: dict[str, Any]) -> str:
    if page.get("module_hint"):
        return slugify(page["module_hint"])
    route = page.get("route") or ""
    parts = meaningful_segments(route.replace("#", "/"))
    return slugify(parts[0] if parts else page.get("title", "module"))


def unique_preserve_order(items: list[str]) -> list[str]:
    result: list[str] = []
    seen = set()
    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def humanize_identifier(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value.replace("_", " ")).strip()


def contains_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def display_field_name(name: str) -> str:
    if contains_chinese(name):
        return name
    return FIELD_LABEL_HINTS.get(name, f"{humanize_identifier(name)} [推断]")


def compact_pending(message: str) -> str:
    return f"[待确认] {message}"


def extract_request_path(url: str) -> str:
    parsed = urlparse(url or "")
    path = parsed.path or str(url or "")
    return re.sub(r"/{2,}", "/", path)


def normalize_path_segment(segment: str) -> str:
    cleaned = segment.strip()
    if not cleaned:
        return ""
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return "*"
    if cleaned.startswith("${") and cleaned.endswith("}"):
        return "*"
    if cleaned.startswith(":"):
        return "*"
    if re.fullmatch(r"\d+", cleaned):
        return "*"
    return cleaned


def path_segments_for_match(path: str) -> list[str]:
    parsed = urlparse(path or "")
    raw_path = parsed.path or str(path or "")
    parts = [normalize_path_segment(part) for part in raw_path.strip("/").split("/") if part]
    while parts and parts[0].lower() in COMMON_ROUTE_PREFIXES:
        parts.pop(0)
    return parts


def route_text(route: dict[str, Any], request: dict[str, Any] | None = None) -> str:
    parts = [str(route.get("route", "")), str(route.get("method_name", ""))]
    parts.extend(route.get("call_hints", []))
    if request:
        parts.append(str(request.get("url", "")))
    return " ".join(parts).lower()


def route_match_score(request_path: str, route_path: str) -> int:
    req_parts = path_segments_for_match(request_path)
    route_parts = path_segments_for_match(route_path)
    if not req_parts or not route_parts:
        return 0
    if len(req_parts) == len(route_parts) and all(left == right or "*" in {left, right} for left, right in zip(req_parts, route_parts)):
        return 100
    if len(req_parts) >= len(route_parts) and req_parts[-len(route_parts) :] == route_parts:
        return 95
    if len(route_parts) >= len(req_parts) and route_parts[-len(req_parts) :] == req_parts:
        return 90
    overlap = 0
    for left, right in zip(reversed(req_parts), reversed(route_parts)):
        if left != right:
            break
        overlap += 1
    if overlap >= 2:
        return 70 + overlap
    if req_parts[-1] == route_parts[-1]:
        return 55
    return 0


def is_valid_route_path(path: str) -> bool:
    cleaned = path.strip()
    if not cleaned:
        return False
    if "${" in cleaned:
        return False
    return True


def build_network_indexes(frontend: dict[str, Any] | None) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not frontend:
        return by_id, by_page
    for request in frontend.get("network_requests", []):
        request_id = str(request.get("id", "")).strip()
        if request_id:
            by_id[request_id] = request
        page_title = str(request.get("page_title", "")).strip()
        if page_title:
            by_page[page_title].append(request)
    return by_id, by_page


def collect_page_requests(page: dict[str, Any], frontend: dict[str, Any] | None) -> list[dict[str, Any]]:
    by_id, by_page = build_network_indexes(frontend)
    requests: list[dict[str, Any]] = []
    seen = set()
    for ref in page.get("network_refs", []):
        item = by_id.get(str(ref))
        if not item:
            continue
        key = (item.get("method"), item.get("url"))
        if key in seen:
            continue
        seen.add(key)
        requests.append(item)
    for item in by_page.get(page.get("title", ""), []):
        key = (item.get("method"), item.get("url"))
        if key in seen:
            continue
        seen.add(key)
        requests.append(item)
    return requests


def match_requests_to_routes(requests: list[dict[str, Any]], routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for request in requests:
        request_path = extract_request_path(str(request.get("url", "")))
        request_method = str(request.get("method", "")).upper()
        best_route = None
        best_score = 0
        for route in routes:
            if not is_valid_route_path(str(route.get("route", ""))):
                continue
            methods = [str(method).upper() for method in route.get("http_methods", [])]
            if request_method and methods and "ANY" not in methods and request_method not in methods:
                continue
            score = route_match_score(request_path, str(route.get("route", "")))
            if score > best_score:
                best_score = score
                best_route = route
        if best_route and best_score >= 55:
            matches.append({"request": request, "route": best_route, "score": best_score})
    return matches


def infer_backend_action(text: str) -> str:
    lowered = text.lower()
    if "/system/role/changestatus" in lowered:
        return "修改角色启用状态，并立即影响该角色是否继续可用。"
    if "/system/user/changestatus" in lowered:
        return "修改用户启用状态，并立即影响账号登录和使用权限。"
    if "/system/role/authuser/selectall" in lowered:
        return "批量把用户授权给当前角色。"
    if "/system/role/authuser/cancelall" in lowered or "/system/role/authuser/cancel" in lowered:
        return "取消用户与角色之间的授权关系。"
    if "/system/user/authrole" in lowered:
        return "调整用户拥有的角色集合。"
    if "/system/user/resetpwd" in lowered:
        return "重置用户密码，恢复账号访问能力。"
    if "order-realtime" in lowered:
        return "读取实时订单统计数据，用于展示经营看板。"
    if "order-production-sales" in lowered:
        return "读取订单产销统计数据，用于观察订单产消结构。"
    if "personal-order-processing" in lowered:
        return "读取个人处理效率与处理量数据，用于管理个人任务表现。"
    if "supplier-settlement" in lowered:
        return "读取供应商结算相关统计结果，用于核对结算口径。"
    if "changestatus" in lowered or "change-status" in lowered:
        return "修改对象启用状态或业务状态，并立即影响页面展示结果。"
    if "updatepwd" in lowered or "avatar" in lowered:
        return "更新用户资料类信息，并把结果回写到当前账户能力中。"
    if "authuser" in lowered or "datascope" in lowered or "menupermission" in lowered:
        return "修改授权范围、权限绑定或可见资源范围。"
    if any(token in lowered for token in ("list", "page", "query", "search", "select", "get", "find")):
        return "读取并返回页面所需的业务数据。"
    if any(token in lowered for token in ("status", "approve", "reject", "submit", "confirm", "claim", "assign", "dispatch")):
        return "写回处理动作并推动业务状态继续流转。"
    if any(token in lowered for token in ("create", "add", "insert", "save", "publish")):
        return "新增业务对象并让其进入后续生效链路。"
    if any(token in lowered for token in ("update", "edit", "modify", "reset")):
        return "更新已有业务对象的关键属性或处理结果。"
    if any(token in lowered for token in ("delete", "remove", "cancel")):
        return "终止、删除或撤回当前业务对象。"
    if any(token in lowered for token in ("export", "download")):
        return "把当前结果导出为离线文件，方便台账或人工复核。"
    if any(token in lowered for token in ("import", "upload")):
        return "接收外部输入并批量写入系统。"
    if any(token in lowered for token in ("history", "timeline", "log")):
        return "返回处理轨迹，帮助页面展示业务过程和追溯信息。"
    return "支撑当前页面的数据读取或处理提交。"


def summarize_call_hints(call_hints: list[str]) -> str:
    if not call_hints:
        return ""
    summaries = []
    for call in call_hints[:4]:
        summaries.append(infer_backend_action(call))
    summaries = unique_preserve_order(summaries)
    if not summaries:
        return ""
    return "；".join(summaries[:3])


def infer_business_result(text: str) -> str:
    lowered = text.lower()
    if "/system/role/changestatus" in lowered:
        return "角色会在启用和停用之间切换，并影响后续授权生效。"
    if "/system/user/changestatus" in lowered:
        return "用户账号状态会立即变化，并影响登录与操作权限。"
    if "/system/role/authuser/selectall" in lowered:
        return "选中的用户会获得该角色，可访问对应权限范围。"
    if "/system/role/authuser/cancelall" in lowered or "/system/role/authuser/cancel" in lowered:
        return "用户会失去当前角色授权，相关菜单与数据权限同步收回。"
    if "/system/user/authrole" in lowered:
        return "用户的角色集合会更新，影响后续权限范围。"
    if "/system/user/resetpwd" in lowered:
        return "用户可使用新密码重新登录。"
    if "order-realtime" in lowered:
        return "页面会展示实时订单走势和关键数量变化。"
    if "order-production-sales" in lowered:
        return "页面会展示订单产销对比，辅助判断供需情况。"
    if "personal-order-processing" in lowered:
        return "页面会展示个人处理效率和任务完成情况。"
    if "supplier-settlement" in lowered:
        return "页面会展示供应商结算相关统计结果。"
    if "changestatus" in lowered:
        return "页面中的启用状态会立即切换，并影响后续可执行动作。"
    if "updatepwd" in lowered or "avatar" in lowered:
        return "账户资料会更新，并影响当前用户后续使用体验。"
    if any(token in lowered for token in ("status", "approve", "reject", "confirm")):
        return "页面状态、审核结果或处理阶段会随之更新。"
    if any(token in lowered for token in ("claim", "assign", "dispatch")):
        return "对象会进入新的负责人或新的处理队列。"
    if any(token in lowered for token in ("query", "list", "search", "page", "get")):
        return "页面可以展示最新结果，供用户继续筛选或处理。"
    if any(token in lowered for token in ("create", "add", "insert", "save", "publish")):
        return "新对象会出现在列表、投放范围或后续处理链路中。"
    if any(token in lowered for token in ("export", "download")):
        return "结果会沉淀为离线文件，供后续复核或流转。"
    if any(token in lowered for token in ("history", "timeline", "log")):
        return "页面可展示处理轨迹，帮助用户理解前后步骤。"
    return "业务结果会回流到当前页面或相关上下游模块。"


def render_closure_table(rows: list[list[str]], fallback: str) -> str:
    return table(["页面动作", "系统处理", "业务结果", "证据摘要"], rows, fallback)


def render_route_index(module: dict[str, Any], frontend: dict[str, Any] | None) -> str:
    rows: list[list[str]] = []
    seen = set()
    page_requests = []
    for page in module.get("pages", []):
        page_requests.extend(collect_page_requests(page, frontend))
    matches = match_requests_to_routes(page_requests, module.get("routes", []))
    if not matches:
        matches = match_requests_to_routes(page_requests, module.get("all_routes", []))
    candidate_routes = [item["route"] for item in matches] if matches else []
    if not candidate_routes and page_requests:
        for request in page_requests[:12]:
            request_path = extract_request_path(str(request.get("url", "")))
            key = (str(request.get("method", "")).upper(), request_path)
            if key in seen:
                continue
            seen.add(key)
            pseudo_route = {
                "route": request_path,
                "method_name": str(request.get("method_name", "")),
                "call_hints": [],
                "http_methods": [str(request.get("method", "")).upper()],
            }
            rows.append(
                [
                    f"{str(request.get('method', '')).upper()} {request_path}",
                    infer_user_touchpoint({"title": module["title"]}, pseudo_route, request),
                    infer_backend_action(route_text(pseudo_route, request)),
                ]
            )
        return table(["接口", "页面关联动作", "一句话说明"], rows, "当前未识别到稳定的后端支撑索引。")
    if not candidate_routes:
        candidate_routes = module.get("routes", [])
    for route in candidate_routes:
        if not is_valid_route_path(str(route.get("route", ""))):
            continue
        key = (tuple(route.get("http_methods", [])), route.get("route", ""))
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            [
                "/".join(route.get("http_methods", [])),
                route.get("route", ""),
                infer_backend_action(route_text(route)),
            ]
        )
        if len(rows) >= 12:
            break
    return table(["Method", "Path", "业务说明"], rows, "当前未识别到稳定的后端支撑索引。")


def count_visible_leaf_pages(frontend: dict[str, Any] | None) -> int:
    if not frontend:
        return 0
    return len(iter_menu_leaf_pages(frontend))


def build_route_modules(facts: dict[str, Any]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    docs = facts.get("docs", [])
    artifacts = facts.get("code_artifacts", {})

    for route in facts.get("routes", []):
        key = module_key_from_route(route.get("route", ""), route.get("controller", ""))
        group = grouped.setdefault(
            key,
            {
                "key": key,
                "title": MODULE_TITLES.get(key, titleize_slug(key)),
                "routes": [],
                "docs": [],
                "artifacts": [],
                "pages": [],
                "state_machines": [],
                "all_routes": [],
            },
        )
        group["routes"].append(route)

    for key, group in grouped.items():
        token = key.replace("-", "").lower()
        for doc in docs:
            joined = f"{doc.get('title', '')} {doc.get('path', '')}".lower().replace("-", "")
            if token and token in joined:
                group["docs"].append(doc)
        for kind, items in artifacts.items():
            for item in items:
                joined = f"{item.get('name', '')} {item.get('path', '')}".lower().replace("-", "")
                if token and token in joined:
                    group["artifacts"].append({"kind": kind, **item})

    for machine in facts.get("state_machines", []):
        name = slugify(re.sub(r"status$", "", machine.get("name", ""), flags=re.I))
        candidates = [name, f"{name}s"]
        if name == "order":
            candidates.extend(["orders", "player"])
        if name == "finance-audit":
            candidates.extend(["finance", "finance-audit"])
        for candidate in candidates:
            if candidate in grouped:
                grouped[candidate]["state_machines"].append(machine)
                break

    return grouped


def normalize_items(items: list[Any], fallback_kind: str) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for item in items or []:
        if isinstance(item, str):
            normalized.append({"name": item, "type": fallback_kind, "purpose": ""})
            continue
        if isinstance(item, dict):
            normalized.append(
                {
                    "name": str(item.get("name", "")).strip(),
                    "type": str(item.get("type", fallback_kind)).strip() or fallback_kind,
                    "purpose": str(item.get("purpose", "")).strip(),
                }
            )
    return [item for item in normalized if item["name"]]


def normalize_dialogs(dialogs: list[Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for dialog in dialogs or []:
        if not isinstance(dialog, dict):
            continue
        results.append(
            {
                "name": str(dialog.get("name", "")).strip(),
                "description": str(dialog.get("description", "")).strip(),
                "fields": normalize_items(dialog.get("fields", []), "input"),
                "actions": normalize_items(dialog.get("actions", []), "action"),
            }
        )
    return [item for item in results if item["name"]]


def normalize_page(page: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "title": page.get("title", "未命名页面"),
        "route": page.get("route", ""),
        "breadcrumbs": page.get("breadcrumbs", []),
        "module_hint": module_key_from_page(page),
        "capture_status": str(page.get("capture_status", "full")).strip() or "full",
        "filters": normalize_items(page.get("filters", []), "text"),
        "table_columns": normalize_items(page.get("table_columns", []), "column"),
        "actions": normalize_items(page.get("actions", []), "action"),
        "bulk_actions": normalize_items(page.get("bulk_actions", []), "action"),
        "row_actions": normalize_items(page.get("row_actions", []), "action"),
        "metrics": normalize_items(page.get("metrics", []), "metric"),
        "charts": normalize_items(page.get("charts", []), "chart"),
        "statuses": unique_preserve_order([str(item) for item in page.get("statuses", [])]),
        "dialogs": normalize_dialogs(page.get("dialogs", [])),
        "empty_state": str(page.get("empty_state", "")).strip(),
        "description": str(page.get("description", "")).strip(),
        "network_refs": page.get("network_refs", []),
    }
    return normalized


def iter_menu_leaf_pages(frontend: dict[str, Any]) -> list[dict[str, Any]]:
    leaf_pages: list[dict[str, Any]] = []
    for menu in frontend.get("menus", []):
        title = str(menu.get("title", "")).strip()
        children = [str(child).strip() for child in menu.get("children", []) if str(child).strip()]
        if children:
            for child in children:
                leaf_pages.append(
                    {
                        "title": child,
                        "route": "",
                        "breadcrumbs": [title, child] if title else [child],
                        "module_hint": stable_key(child),
                        "capture_status": "menu_only",
                        "description": "该页面已在菜单中识别，但尚未完成页面级字段和操作采集。",
                        "filters": [],
                        "table_columns": [],
                        "actions": [],
                        "bulk_actions": [],
                        "row_actions": [],
                        "metrics": [],
                        "charts": [],
                        "statuses": [],
                        "dialogs": [],
                        "empty_state": "",
                        "network_refs": [],
                    }
                )
        elif title:
            leaf_pages.append(
                {
                    "title": title,
                    "route": "",
                    "breadcrumbs": [title],
                    "module_hint": stable_key(title),
                    "capture_status": "menu_only",
                    "description": "该页面已在菜单中识别，但尚未完成页面级字段和操作采集。",
                    "filters": [],
                    "table_columns": [],
                    "actions": [],
                    "bulk_actions": [],
                    "row_actions": [],
                    "metrics": [],
                    "charts": [],
                    "statuses": [],
                    "dialogs": [],
                    "empty_state": "",
                    "network_refs": [],
                }
            )
    return leaf_pages


def build_frontend_modules(frontend: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not frontend:
        return {}

    grouped: dict[str, dict[str, Any]] = {}
    seen_titles = set()
    for raw_page in frontend.get("pages", []):
        page = normalize_page(raw_page)
        key = page["module_hint"]
        seen_titles.add(page["title"])
        group = grouped.setdefault(
            key,
            {
                "key": key,
                "title": MODULE_TITLES.get(key, page["title"]),
                "pages": [],
                "routes": [],
                "docs": [],
                "artifacts": [],
                "state_machines": [],
                "all_routes": [],
            },
        )
        group["pages"].append(page)

    for raw_page in iter_menu_leaf_pages(frontend):
        if raw_page["title"] in seen_titles:
            continue
        page = normalize_page(raw_page)
        key = page["module_hint"]
        group = grouped.setdefault(
            key,
            {
                "key": key,
                "title": MODULE_TITLES.get(key, page["title"]),
                "pages": [],
                "routes": [],
                "docs": [],
                "artifacts": [],
                "state_machines": [],
                "all_routes": [],
            },
        )
        group["pages"].append(page)
    return grouped


def merge_modules(facts: dict[str, Any], frontend: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    route_modules = build_route_modules(facts)
    frontend_modules = build_frontend_modules(frontend)
    all_routes = facts.get("routes", [])

    if frontend_modules:
        merged = frontend_modules
        for key, group in merged.items():
            group["all_routes"] = all_routes
            if key in route_modules:
                group["routes"] = route_modules[key]["routes"]
                group["docs"] = route_modules[key]["docs"]
                group["artifacts"] = route_modules[key]["artifacts"]
                group["state_machines"] = route_modules[key]["state_machines"]
        return merged

    for group in route_modules.values():
        group["all_routes"] = all_routes
    return route_modules


def choose_priority_modules(modules: dict[str, dict[str, Any]], limit: int = 8) -> list[str]:
    def score(module: dict[str, Any]) -> tuple[int, int, int, int]:
        key = module["key"]
        weight = BUSINESS_MODULE_BOOST.get(key, 0) + NON_PRODUCT_MODULE_PENALTY.get(key, 0)
        return (
            weight,
            len(module.get("pages", [])),
            len(module.get("state_machines", [])),
            len(module.get("routes", [])),
        )

    ranked = sorted(modules.values(), key=score, reverse=True)
    return [module["key"] for module in ranked[:limit]]


def bullet_list(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def table(headers: list[str], rows: list[list[str]], fallback: str) -> str:
    if not rows:
        return fallback
    escaped_headers = [header.replace("|", "\\|") for header in headers]
    lines = [
        "| " + " | ".join(escaped_headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        escaped_row = [(cell or "-").replace("|", "\\|").replace("\n", "<br>") for cell in row]
        lines.append("| " + " | ".join(escaped_row) + " |")
    return "\n".join(lines)


def infer_field_meaning(name: str) -> str:
    for key, meaning in sorted(FIELD_MEANING_HINTS.items(), key=lambda item: len(item[0]), reverse=True):
        if key in name:
            return meaning
    if "AI" in name and "地址" in name and "检测" in name:
        return "AI检测收货地址是否存在异常，例如格式错误、信息缺失或疑似无效，用于提示处理人员重点核对。"
    if "V6以上" in name:
        return "用于标识 VIP 等级达到 V6 及以上的高价值用户或对应订单统计结果。"
    if "AI" in name and "检测" in name:
        return "AI 对相关信息进行异常识别后的结果，用于提示人工优先复核。"
    if "AI" in name:
        return "AI 辅助识别结果，用于和用户提交信息或人工录入结果进行比对。"
    if "检测" in name:
        return "用于提示该字段对应的信息是否存在异常，便于人工复核。"
    if "以上" in name:
        return "用于表示达到某个阈值以上的人群、订单或统计结果。"
    if "时间" in name:
        return "用于判断业务发生时间、处理时点或时间范围。"
    if "金额" in name:
        return "用于判断金额是否异常，以及是否需要审核或复核。"
    if "状态" in name:
        return "用于判断对象处于哪个阶段，并决定后续动作。"
    if "备注" in name:
        return "用于补充说明特殊情况或业务上下文。"
    if not contains_chinese(name):
        return compact_pending(f"当前根据字段名推断其与“{humanize_identifier(name)}”相关，具体业务口径仍需结合页面文案确认。")
    return compact_pending("当前只能确认该字段参与页面展示或处理判断，具体业务口径仍需结合页面文案或业务方补充。")


def infer_action_purpose(name: str) -> str:
    for key, meaning in sorted(ACTION_PURPOSE_HINTS.items(), key=lambda item: len(item[0]), reverse=True):
        if key in name:
            return meaning
    if "通过" in name:
        return "让对象进入通过后的下一阶段。"
    if "拒绝" in name or "驳回" in name:
        return "让对象进入异常分支，等待后续修正或重新提交。"
    if "查询" in name or "查看" in name:
        return "读取当前业务对象或结果集，帮助用户继续判断和处理。"
    if "新增" in name:
        return "创建新的业务对象并让其进入后续处理链路。"
    if "修改" in name or "更新" in name:
        return "修改当前对象的配置、状态或关键信息。"
    if "删除" in name:
        return "移除当前对象，避免继续参与后续流程。"
    if "导入" in name:
        return "把外部数据批量写入系统，减少人工录入。"
    return compact_pending("当前只能确认这是页面上的可执行操作，具体业务目的仍需结合页面交互补充。")


def normalize_action_display(item: dict[str, Any]) -> str:
    name = str(item.get("name", "")).strip()
    if contains_chinese(name):
        return name
    combined = " ".join(
        [
            name,
            str(item.get("method_name", "")),
            extract_request_path(str(item.get("url", ""))),
        ]
    )
    if "announcement" in combined.lower() and any(token in combined.lower() for token in ("list", "query", "get")):
        return "查询公告列表 [推断]"
    if "order-realtime" in combined.lower():
        return "查询实时订单报表 [推断]"
    if "order-production-sales" in combined.lower():
        return "查询订单产销报表 [推断]"
    if "personal-order-processing" in combined.lower():
        return "查询个人订单处理报表 [推断]"
    if "supplier-settlement" in combined.lower():
        return "查询供应商结算报表 [推断]"
    if "export" in combined.lower() and "peripheral" in combined.lower():
        return "导出周边订单 Excel [推断]"
    if "change" in combined.lower() and "status" in combined.lower():
        return "修改状态 [推断]"
    if "reset" in combined.lower() and "pwd" in combined.lower():
        return "重置密码 [推断]"
    if "authrole" in combined.lower():
        return "分配角色 [推断]"
    if "authuser" in combined.lower():
        return "分配用户 [推断]"
    if "import" in combined.lower():
        return "导入数据 [推断]"
    if "export" in combined.lower():
        return "导出结果 [推断]"
    if "delete" in combined.lower() or "remove" in combined.lower():
        return "删除对象 [推断]"
    if "update" in combined.lower() or "edit" in combined.lower():
        return "修改对象 [推断]"
    if "create" in combined.lower() or "add" in combined.lower():
        return "新增对象 [推断]"
    if any(token in combined.lower() for token in ("list", "query", "get", "page", "detail")):
        return "查询详情或列表 [推断]"
    return f"{humanize_identifier(name)} [推断]"


def render_state_summary(machine: dict[str, Any]) -> str:
    labels = [item.get("label", item.get("code", "")) for item in machine.get("states", []) if item.get("label") or item.get("code")]
    label_by_code = {item.get("code"): item.get("label", item.get("code", "")) for item in machine.get("states", [])}
    transitions = []
    for item in machine.get("transitions", [])[:8]:
        from_label = label_by_code.get(item.get("from"), item.get("from", ""))
        to_labels = [label_by_code.get(code, code) for code in item.get("to", [])]
        if from_label and to_labels:
            transitions.append(f"{from_label} -> {', '.join(to_labels)}")
    lines = []
    if labels:
        lines.append(f"状态集合：{'、'.join(labels[:12])}")
    if transitions:
        lines.append(f"关键流转：{'；'.join(transitions[:6])}")
    special_rules = [normalize_special_rule(rule) for rule in machine.get("special_rules", [])]
    special_rules = [rule for rule in special_rules if rule]
    if special_rules:
        lines.append(f"特别规则：{'；'.join(special_rules[:4])}")
    return "；".join(lines)


def normalize_special_rule(rule: str) -> str:
    if "终态候选" in rule:
        return "配送完成是订单主流程的终态。"
    if "可认领候选" in rule:
        return "已提交和信息修正后的订单可以重新进入认领池。"
    if "取消状态可重新回到已提交" in rule:
        return "取消后的订单仍可能回到已提交状态重新处理。"
    if re.search(r"[A-Z_]{3,}", rule):
        return ""
    return rule


def choose_initial_state(machine: dict[str, Any]) -> str | None:
    preferred = ["已提交", "待审核", "待处理", "排队发货中", "SUBMITTED", "PENDING"]
    states = machine.get("states", [])
    for target in preferred:
        for item in states:
            if item.get("label") == target or item.get("code") == target:
                return item.get("code") or item.get("label")
    final_states = set(machine.get("final_states", []))
    for item in states:
        code = item.get("code") or item.get("label")
        if code and code not in final_states:
            return code
    if states:
        return states[0].get("code") or states[0].get("label")
    return None


def build_state_diagram(machine: dict[str, Any]) -> str:
    states = machine.get("states", [])
    if not states:
        return "当前未识别到可绘制的状态机图。"

    aliases: dict[str, str] = {}
    label_by_code: dict[str, str] = {}
    lines = ["```mermaid", "stateDiagram-v2"]

    for index, item in enumerate(states, start=1):
        code = item.get("code") or item.get("label") or f"STATE_{index}"
        label = item.get("label") or code
        alias = f"S{index}"
        aliases[code] = alias
        label_by_code[code] = label
        lines.append(f'    state "{label}" as {alias}')

    initial = choose_initial_state(machine)
    if initial and initial in aliases:
        lines.append(f"    [*] --> {aliases[initial]}")

    seen = set()
    for transition in machine.get("transitions", []):
        from_code = transition.get("from")
        from_alias = aliases.get(from_code)
        if not from_alias:
            continue
        for to_code in transition.get("to", []):
            to_alias = aliases.get(to_code)
            if not to_alias:
                continue
            edge = (from_alias, to_alias)
            if edge in seen:
                continue
            seen.add(edge)
            lines.append(f"    {from_alias} --> {to_alias}")

    for final_code in machine.get("final_states", []):
        if final_code in aliases:
            lines.append(f"    {aliases[final_code]} --> [*]")

    if machine.get("name") == "OrderStatus":
        for code, label in label_by_code.items():
            alias = aliases[code]
            if label == "配送完成":
                lines.extend(
                    [
                        f"    note right of {alias}",
                        "        唯一终态",
                        "        进入财务审核",
                        "    end note",
                    ]
                )
            if label in {"已提交", "信息已修改"}:
                lines.extend(
                    [
                        f"    note right of {alias}",
                        "        可重新进入认领池",
                        "    end note",
                    ]
                )

    lines.append("```")
    return "\n".join(lines)


def collect_state_labels(module: dict[str, Any]) -> set[str]:
    labels = set()
    for page in module.get("pages", []):
        labels.update(page.get("statuses", []))
    for machine in module.get("state_machines", []):
        for item in machine.get("states", []):
            label = item.get("label")
            if label:
                labels.add(label)
    return labels


def infer_roles(module_key: str, module: dict[str, Any]) -> list[str]:
    if module_key == "orders":
        return ["后台运营人员", "订单处理人员", "财务协作人员"]
    if module_key == "workflow":
        return ["个人任务处理人员", "订单处理人员"]
    if module_key == "player":
        return ["终端用户", "玩家"]
    if module_key in {"finance", "finance-audit"}:
        return ["财务人员", "审核人员"]
    if module_key == "statistics":
        return ["运营管理者", "业务负责人"]
    if module_key.startswith("supplier"):
        return ["供应商管理人员", "供应商侧履约人员"]
    if module_key == "announcement":
        return ["运营人员"]
    inferred = []
    joined = " ".join(page["title"] for page in module.get("pages", []))
    if "供应商" in joined:
        inferred.append("供应商管理人员")
    if "公告" in joined:
        inferred.append("运营人员")
    return inferred or ["业务操作人员"]


def infer_module_goal(module_key: str, module: dict[str, Any]) -> str:
    explicit = MODULE_POSITIONING.get(module_key)
    if explicit:
        return explicit
    page_titles = [page["title"] for page in module.get("pages", [])]
    if page_titles:
        return f"围绕 {'、'.join(page_titles[:3])} 这些页面提供独立业务能力。"
    return f"围绕 {module['title']} 提供独立业务能力。"


def infer_business_objects(modules: dict[str, dict[str, Any]]) -> list[str]:
    objects = [
        "订单：贯穿提交、分派、处理、配送、异常和完成全过程的核心业务对象。",
        "订单状态：用于标记订单所处阶段，并决定后续可执行动作。",
        "财务审核结果：决定订单是否完成财务确认，是否需要重提或拒绝。",
        "供应商规则：定义订单如何分配给供应商，以及供应商可查看哪些字段。",
        "公告：用于向特定渠道发布运营通知，并维护启用状态与展示风格。",
    ]
    if "statistics" in modules:
        objects.append("经营指标：用于展示提交量、处理量、积压量、处理占比和渠道分布。")
    return objects


def infer_page_layout(page: dict[str, Any]) -> list[str]:
    layout = []
    if page.get("capture_status") == "menu_only":
        return ["当前仅识别到菜单入口，尚未完成页面级结构采集。"]
    if page.get("metrics"):
        layout.append("顶部包含关键指标卡，用于快速把握业务盘面。")
    if page.get("charts"):
        layout.append("页面包含图表区域，用于观察趋势、分布或结构变化。")
    if page.get("filters"):
        layout.append("页面顶部提供筛选区域，用于缩小目标范围。")
    if page.get("table_columns"):
        layout.append("页面主体为列表或表格，用于处理批量业务对象。")
    if page.get("dialogs"):
        layout.append("页面包含弹窗式处理入口，用于在不离开列表的情况下完成关键操作。")
    if page.get("empty_state"):
        layout.append(f"空结果时会提示：{page['empty_state']}")
    return layout or ["页面结构信息有限，当前只能确认其承担独立业务功能。"]


def infer_page_objective(page: dict[str, Any], module_key: str) -> str:
    if page.get("description"):
        return page["description"]
    title = page["title"]
    if "仪表盘" in title or "数据表" in title:
        return "帮助运营快速了解订单处理规模、积压和渠道分布。"
    if title == "订单大厅":
        return "帮助后台处理人员在订单池中定位目标订单，并执行认领、分派和处理推进。"
    if title == "订单查询":
        return "提供轻量查询入口，让用户按关键编号快速检索订单。"
    if "财务审核" in title:
        return "帮助财务快速筛选待审核订单，并完成通过或拒绝。"
    if "供应商配置" in title:
        return "帮助运营维护供应商规则、字段可见范围和商品映射。"
    if "供应商订单" in title:
        return "帮助运营或供应商查看分配后的订单并跟踪履约状态。"
    if "公告" in title:
        return "帮助运营创建、启停和预览公告。"
    return infer_module_goal(module_key, {"title": title, "pages": [page]})


def build_navigation_lines(frontend: dict[str, Any] | None, modules: dict[str, dict[str, Any]]) -> list[str]:
    if frontend and frontend.get("menus"):
        lines = []
        for menu in frontend["menus"]:
            children = menu.get("children", [])
            if children:
                lines.append(f"{menu.get('title', '未命名菜单')}：{', '.join(children)}")
            else:
                lines.append(menu.get("title", "未命名菜单"))
        return lines

    lines = []
    for key in choose_priority_modules(modules, limit=8):
        module = modules[key]
        if module.get("pages"):
            page_titles = ", ".join(page["title"] for page in module["pages"][:4])
            lines.append(f"{module['title']}：{page_titles}")
        else:
            lines.append(module["title"])
    return lines


def build_module_overview_lines(modules: dict[str, dict[str, Any]]) -> list[str]:
    lines = []
    for key in choose_priority_modules(modules, limit=10):
        module = modules[key]
        page_suffix = f"，覆盖页面：{', '.join(page['title'] for page in module.get('pages', [])[:3])}" if module.get("pages") else ""
        lines.append(f"{module['title']}：{infer_module_goal(key, module)}{page_suffix}")
    return lines


def build_status_lines(module: dict[str, Any]) -> list[str]:
    statuses = []
    for page in module.get("pages", []):
        statuses.extend(page.get("statuses", []))
    statuses = unique_preserve_order(statuses)
    lines = []
    if statuses:
        lines.append(f"页面上可见的关键状态包括：{'、'.join(statuses[:12])}。")
    for machine in module.get("state_machines", []):
        summary = render_state_summary(machine)
        if summary:
            lines.append(summary)
    if not lines and module["key"] == "orders":
        lines.append("订单状态至少覆盖已提交、已认领、配送中、配送完成、信息错误等阶段。")
    return lines


def module_flow_mermaid(module_key: str) -> str:
    if module_key == "orders":
        return """```mermaid
flowchart LR
    A["订单进入后台订单池"] --> B["按订单号 / 活动ID / 编号筛选"]
    B --> C["认领或批量指派"]
    C --> D["进入高级订单管理"]
    D --> E["维护联系人 / 地址 / 金额 / 附件 / 备注"]
    E --> F["推进订单状态"]
    F --> G["进入财务审核或继续供应商履约"]
```"""
    if module_key in {"finance", "finance-audit"}:
        return """```mermaid
flowchart LR
    A["进入待审核订单池"] --> B["按玩家 / 订单号 / 订单类型筛选"]
    B --> C["查看金额、AI差值、附件"]
    C --> D["审核通过"]
    C --> E["审核拒绝"]
    D --> F["更新审核状态并沉淀结果"]
    E --> G["进入异常或重提分支"]
```"""
    if module_key == "supplier-config":
        return """```mermaid
flowchart LR
    A["新增供应商"] --> B["设置分单规则"]
    B --> C["设置查询范围"]
    C --> D["设置字段展示范围"]
    D --> E["配置商品映射"]
    E --> F["启用规则并设置优先级"]
```"""
    if module_key == "supplier":
        return """```mermaid
flowchart LR
    A["订单命中供应商规则"] --> B["出现在供应商订单页"]
    B --> C["按供应商 / 订单号 / 状态筛选"]
    C --> D["查看联系人、地址、金额、备注"]
    D --> E["跟踪配送中 / 配送完成 / 已挂起等状态"]
```"""
    if module_key == "announcement":
        return """```mermaid
flowchart LR
    A["新增公告"] --> B["设置标题、颜色和渠道"]
    B --> C["预览公告效果"]
    C --> D["启用公告"]
    D --> E["渠道侧或用户侧可见"]
    E --> F["后续可编辑、停用或删除"]
```"""
    if module_key == "statistics":
        return """```mermaid
flowchart LR
    A["选择日期范围"] --> B["查看关键指标卡"]
    B --> C["阅读库存、产消、配送和状态分布图"]
    C --> D["定位异常积压或趋势变化"]
```"""
    return "待补充：当前只能确认该模块提供列表、表单或配置类能力，但还没有稳定恢复出高置信业务流程。"


def page_flow_mermaid(page: dict[str, Any], module_key: str) -> str:
    title = page["title"]
    if title == "订单大厅":
        return """```mermaid
flowchart LR
    A["筛选订单"] --> B["查看列表字段"]
    B --> C["认领或批量指派"]
    C --> D["打开高级订单管理"]
    D --> E["维护联系人 / 地址 / 金额 / 附件 / 备注"]
    E --> F["推进配送或异常状态"]
```"""
    if title == "订单查询":
        return """```mermaid
flowchart LR
    A["输入系统订单编号 / 玩家ID / 第三方订单ID"] --> B["执行搜索"]
    B --> C["返回订单结果"]
    B --> D["无结果时提示补充搜索条件"]
```"""
    if "财务审核" in title:
        return """```mermaid
flowchart LR
    A["筛选待审核订单"] --> B["核对金额和附件"]
    B --> C["审核通过"]
    B --> D["审核拒绝"]
    C --> E["更新审核结果"]
    D --> F["进入异常处理"]
```"""
    if title == "供应商配置":
        return """```mermaid
flowchart LR
    A["新增或编辑供应商"] --> B["设置分单规则"]
    B --> C["设置查询范围和字段展示"]
    C --> D["配置商品映射"]
    D --> E["启用并生效"]
```"""
    if title == "供应商订单":
        return """```mermaid
flowchart LR
    A["筛选供应商订单"] --> B["查看联系人、金额和地址"]
    B --> C["跟踪订单状态"]
    C --> D["识别配送完成、配送中或挂起订单"]
```"""
    if title == "公告管理":
        return """```mermaid
flowchart LR
    A["创建公告"] --> B["设置标题、状态、颜色和渠道"]
    B --> C["预览公告"]
    C --> D["启用公告"]
    D --> E["后续编辑或删除"]
```"""
    if "仪表盘" in title or "数据表" in title:
        return """```mermaid
flowchart LR
    A["选择日期范围"] --> B["刷新指标和图表"]
    B --> C["观察业务变化"]
    C --> D["定位异常积压或渠道结构变化"]
```"""
    fallback = module_flow_mermaid(module_key)
    return fallback


def render_field_table(items: list[dict[str, str]], fallback: str) -> str:
    rows = []
    for item in items:
        rows.append(
            [
                display_field_name(item["name"]),
                item.get("type", "-"),
                item.get("purpose") or infer_field_meaning(item["name"]),
            ]
        )
    return table(["字段", "类型", "产品含义"], rows, fallback)


def render_action_table(page: dict[str, Any]) -> str:
    rows = []
    for scope, items in (
        ("页面操作", page.get("actions", [])),
        ("批量操作", page.get("bulk_actions", [])),
        ("行内操作", page.get("row_actions", [])),
    ):
        for item in items:
            display_name = normalize_action_display(item)
            rows.append(
                [
                    display_name,
                    scope,
                    item.get("purpose") or infer_action_purpose(" ".join([display_name, str(item.get("url", "")), str(item.get("method_name", ""))])),
                ]
            )
    return table(["动作", "范围", "业务目的"], rows, "当前未采集到显式操作定义。")


def infer_user_touchpoint(page: dict[str, Any], route: dict[str, Any], request: dict[str, Any] | None = None) -> str:
    joined = route_text(route, request) + " " + page.get("title", "").lower()
    method = ""
    if request:
        method = str(request.get("method", "")).upper()
    elif route.get("http_methods"):
        method = str(route.get("http_methods", [""])[0]).upper()
    if "/api/admin/orders/my-claimed" in joined:
        return "查看个人已认领订单"
    if "/api/admin/orders/claim-next" in joined:
        return "一键认领订单"
    if "/api/admin/orders/" in joined and "/status" in joined:
        return "推进订单状态"
    if "/api/admin/orders/" in joined and "/attachments" in joined:
        return "更新订单附件"
    if "/system/role/changestatus" in joined:
        return "修改角色启用状态"
    if "/system/user/changestatus" in joined:
        return "修改用户启用状态"
    if "/system/role/authuser/selectall" in joined:
        return "批量给角色分配用户"
    if "/system/role/authuser/cancelall" in joined or "/system/role/authuser/cancel" in joined:
        return "取消角色授权用户"
    if "/system/user/authrole" in joined:
        return "给用户分配角色"
    if "/system/user/resetpwd" in joined:
        return "重置用户密码"
    if "order-realtime" in joined:
        return "查看实时订单报表"
    if "order-production-sales" in joined:
        return "查看订单产销报表"
    if "personal-order-processing" in joined:
        return "查看个人订单处理报表"
    if "supplier-settlement" in joined:
        return "查看供应商结算报表"
    if "changestatus" in joined:
        return "修改启用状态"
    if "export" in joined:
        return "导出当前结果"
    if any(token in joined for token in ("search", "query", "page", "list", "dashboard", "statistics")) and method in {"GET", ""}:
        return "进入页面或执行筛选查询"
    if any(token in joined for token in ("claim", "assign", "dispatch")):
        return "执行认领、分派或任务接单"
    if any(token in joined for token in ("approve", "reject", "audit")):
        return "执行审核通过、拒绝或复核"
    if any(token in joined for token in ("status", "confirm", "deliver")):
        return "推进订单或履约状态"
    if any(token in joined for token in ("create", "add", "save", "insert")):
        return "新增对象"
    if any(token in joined for token in ("edit", "update", "modify")):
        return "修改对象"
    if any(token in joined for token in ("delete", "remove", "cascade")):
        return "删除对象"
    if any(token in joined for token in ("authuser", "datascope", "menupermission")):
        return "调整权限或授权范围"
    if any(token in joined for token in ("detail", "history", "timeline", "log")):
        return "查看详情或历史记录"
    if any(token in joined for token in ("create", "add", "save", "publish")):
        return "提交新增、编辑或发布动作"
    if any(token in joined for token in ("history", "timeline", "log")):
        return "查看处理轨迹或历史记录"
    return "触发页面中的关键业务操作"


def page_semantic_tokens(page: dict[str, Any]) -> list[str]:
    tokens = [page.get("title", ""), page.get("route", "")]
    tokens.extend(item.get("name", "") for item in page.get("filters", []))
    tokens.extend(item.get("name", "") for item in page.get("table_columns", []))
    tokens.extend(item.get("name", "") for item in page.get("actions", []))
    tokens.extend(item.get("name", "") for item in page.get("bulk_actions", []))
    tokens.extend(item.get("name", "") for item in page.get("row_actions", []))
    return [token for token in tokens if token]


def semantic_route_score(page: dict[str, Any], route: dict[str, Any]) -> int:
    page_tokens = page_semantic_tokens(page)
    page_text = " ".join(page_tokens)
    route_text = " ".join(
        [str(route.get("route", "")), str(route.get("method_name", ""))] + route.get("call_hints", [])
    ).lower()
    score = 0

    for token in page_tokens:
        lowered = token.lower()
        if "mytasks" in lowered and any(hint in route_text for hint in ("my-claimed", "claim", "orders")):
            score += 6
        for zh_token, route_hints in PAGE_ROUTE_HINTS.items():
            if zh_token in token:
                score += sum(3 for hint in route_hints if hint in route_text)
        if "订单" in token and "order" in route_text:
            score += 4
        if "认领" in token and "claim" in route_text:
            score += 5
        if "审核" in token and any(hint in route_text for hint in ("audit", "approve", "reject")):
            score += 5
        if "供应商" in token and "supplier" in route_text:
            score += 5
    if "订单" in page_text and any(hint in route_text for hint in ("detail", "page", "list", "advanced-manage", "status")):
        score += 3
    if "导出" not in page_text and "export" in route_text:
        score -= 20
    if "导入" not in page_text and "import" in route_text:
        score -= 20
    if "贺卡" not in page_text and "greeting-card" in route_text:
        score -= 20
    if "公告" not in page_text and "announcement" in route_text:
        score -= 4
    if "供应商" not in page_text and "supplier" in route_text and "订单" in page_text:
        score -= 2
    return score


def find_semantic_routes_for_page(page: dict[str, Any], module: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = module.get("all_routes", []) or module.get("routes", [])
    scored: list[tuple[int, dict[str, Any]]] = []
    for route in candidates:
        score = semantic_route_score(page, route)
        if score < 8:
            continue
        scored.append((score, route))
    scored.sort(key=lambda item: item[0], reverse=True)
    results: list[dict[str, Any]] = []
    seen = set()
    for _, route in scored:
        key = (tuple(route.get("http_methods", [])), route.get("route", ""), route.get("method_name", ""))
        if key in seen:
            continue
        seen.add(key)
        results.append(route)
        if len(results) >= 6:
            break
    return results


def route_allowed_for_page(page: dict[str, Any], route: dict[str, Any]) -> bool:
    page_text = " ".join(page_semantic_tokens(page))
    route_text = " ".join([str(route.get("route", "")), str(route.get("method_name", ""))]).lower()
    if "导出" not in page_text and "export" in route_text:
        return False
    if "导入" not in page_text and "import" in route_text:
        return False
    if "贺卡" not in page_text and "greeting-card" in route_text:
        return False
    return True


def build_request_only_closure_rows(page: dict[str, Any], requests: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for request in requests[:8]:
        pseudo_route = {
            "route": extract_request_path(str(request.get("url", ""))),
            "method_name": str(request.get("method_name", "")) or str(request.get("id", "")),
            "call_hints": [],
            "http_methods": [str(request.get("method", "")).upper()],
        }
        text = route_text(pseudo_route, request)
        rows.append(
            [
                infer_user_touchpoint(page, pseudo_route, request),
                infer_backend_action(text),
                infer_business_result(text),
                f"{str(request.get('method', '')).upper()} {extract_request_path(str(request.get('url', '')))}",
            ]
        )
    return rows


def build_page_closure_rows(page: dict[str, Any], module: dict[str, Any], frontend: dict[str, Any] | None) -> list[list[str]]:
    requests = collect_page_requests(page, frontend)
    matches = match_requests_to_routes(requests, module.get("routes", []))
    if requests and not matches:
        matches = match_requests_to_routes(requests, module.get("all_routes", []))
    rows: list[list[str]] = []

    for item in matches[:8]:
        route = item["route"]
        request = item["request"]
        evidence = f"{str(request.get('method', '')).upper()} {extract_request_path(str(request.get('url', '')))}"
        system_bits = [infer_backend_action(" ".join([str(route.get("route", "")), str(route.get("method_name", ""))]))]
        hint_summary = summarize_call_hints(route.get("call_hints", []))
        if hint_summary:
            system_bits.append(hint_summary)
        rows.append(
            [
                infer_user_touchpoint(page, route, request),
                " ".join(unique_preserve_order(system_bits)),
                infer_business_result(" ".join([str(route.get("route", "")), str(route.get("method_name", ""))] + route.get("call_hints", []))),
                evidence,
            ]
        )

    if rows:
        return rows

    if requests:
        return build_request_only_closure_rows(page, requests)

    fallback_routes = module.get("routes", [])[:4]
    if not fallback_routes:
        fallback_routes = find_semantic_routes_for_page(page, module)
    elif page.get("capture_status") != "menu_only" and not requests:
        semantic_routes = find_semantic_routes_for_page(page, module)
        if semantic_routes:
            fallback_routes = semantic_routes

    fallback_routes = [route for route in fallback_routes if route_allowed_for_page(page, route)]
    for route in fallback_routes:
        system_bits = [infer_backend_action(" ".join([str(route.get("route", "")), str(route.get("method_name", ""))]))]
        hint_summary = summarize_call_hints(route.get("call_hints", []))
        if hint_summary:
            system_bits.append(hint_summary)
        rows.append(
            [
                infer_user_touchpoint(page, route),
                " ".join(unique_preserve_order(system_bits)),
                infer_business_result(" ".join([str(route.get("route", "")), str(route.get("method_name", ""))] + route.get("call_hints", []))),
                f"{'/'.join(route.get('http_methods', []))} {route.get('route', '')}",
            ]
        )
    return rows


def build_page_closure_summary(page: dict[str, Any], module: dict[str, Any], frontend: dict[str, Any] | None) -> list[str]:
    requests = collect_page_requests(page, frontend)
    matches = match_requests_to_routes(requests, module.get("routes", []))
    if requests and not matches:
        matches = match_requests_to_routes(requests, module.get("all_routes", []))
    lines: list[str] = []
    if requests:
        lines.append(f"当前页面已采集到 {len(requests)} 条运行时请求证据，可用于反推页面与后端的业务闭环。")
    if matches:
        lines.append(f"其中 {len(matches)} 条请求已成功映射到仓库中的后端路由，说明页面与后端职责可以形成闭环。")
    elif requests:
        lines.append("当前页面已经识别到真实请求，但仓库内暂未找到稳定的精确路由映射；闭环说明先以页面请求语义为准。")
    elif find_semantic_routes_for_page(page, module):
        lines.append("当前页面缺少足够的运行时请求证据，以下闭环说明主要根据页面语义与候选后端逻辑的相似度补足。")
    elif module.get("routes"):
        lines.append("当前页面缺少足够的运行时请求证据，以下闭环说明主要根据同模块后端路由和方法命名补足。")
    else:
        lines.append("当前尚未识别到稳定的页面到后端映射，闭环说明仍需补充页面请求证据。")
    if page.get("capture_status") == "menu_only":
        lines.append("该页面目前只有菜单证据，尚未形成字段级和请求级闭环。")
    return lines


def render_dialogs(dialogs: list[dict[str, Any]]) -> str:
    if not dialogs:
        return "当前未采集到弹窗或表单证据。"
    parts = []
    for dialog in dialogs:
        parts.append(f"### {dialog['name']}")
        if dialog.get("description"):
            parts.append(dialog["description"])
        parts.append("")
        parts.append(render_field_table(dialog.get("fields", []), "该弹窗没有采集到字段定义。"))
        if dialog.get("actions"):
            action_rows = []
            for item in dialog["actions"]:
                action_rows.append(
                    [
                        item["name"],
                        item.get("purpose") or infer_action_purpose(item["name"]),
                    ]
                )
            parts.append("")
            parts.append(table(["动作", "业务目的"], action_rows, ""))
        parts.append("")
    return "\n".join(parts).strip()


def render_metrics(page: dict[str, Any]) -> str:
    if not page.get("metrics"):
        return "当前页面没有采集到显式指标卡。"
    rows = []
    for metric in page["metrics"]:
        rows.append(
            [
                metric["name"],
                metric.get("purpose") or infer_field_meaning(metric["name"]),
            ]
        )
    return table(["指标", "产品含义"], rows, "")


def render_page_spec(page: dict[str, Any], module: dict[str, Any], roles: list[str], frontend: dict[str, Any] | None) -> str:
    module_key = module["key"]
    capture_note = (
        "当前仅识别到菜单入口，以下内容属于目录级占位说明，字段、操作和状态仍待页面级补采。"
        if page.get("capture_status") == "menu_only"
        else ""
    )
    sections = [
        f"## 页面规格：{page['title']}",
        "",
        "### 页面目标",
        "",
        infer_page_objective(page, module_key),
        "",
        "### 页面入口",
        "",
        bullet_list(
            [
                f"导航路径：{' > '.join(page['breadcrumbs'])}" if page.get("breadcrumbs") else f"路由入口：{page.get('route', '未记录')}",
                f"页面路由：{page.get('route', '未记录')}",
            ],
            "暂无页面入口信息。",
        ),
        "",
        "### 目标角色",
        "",
        bullet_list(roles, "当前角色仍需确认。"),
        "",
    ]
    if capture_note:
        sections.extend(
            [
                "### 采集状态",
                "",
                capture_note,
                "",
            ]
        )
    sections.extend(
        [
        "### 页面组成",
        "",
        bullet_list(infer_page_layout(page), "暂无页面组成信息。"),
        "",
        "### 筛选字段定义",
        "",
        render_field_table(page.get("filters", []), "当前页面未采集到筛选字段。"),
        "",
        "### 关键指标",
        "",
        render_metrics(page),
        "",
        "### 列表字段定义",
        "",
        render_field_table(page.get("table_columns", []), "当前页面未采集到列表字段。"),
        "",
        "### 核心操作",
        "",
        render_action_table(page),
        "",
        "### 关键弹窗或表单",
        "",
        render_dialogs(page.get("dialogs", [])),
        "",
        "### 可见状态",
        "",
        bullet_list(page.get("statuses", []), "当前页面未采集到显式状态词。"),
        "",
        "### 页面流程图",
        "",
        page_flow_mermaid(page, module_key),
        "",
        "### 前后端闭环说明",
        "",
        bullet_list(build_page_closure_summary(page, module, frontend), "当前尚未形成稳定的前后端闭环说明。"),
        "",
        "### 前后端闭环表",
        "",
        render_closure_table(
            build_page_closure_rows(page, module, frontend),
            "当前缺少足够的页面请求或模块路由证据，暂时无法生成闭环表。",
        ),
        "",
        ]
    )
    if page.get("empty_state"):
        sections.extend(
            [
                "### 空状态提示",
                "",
                page["empty_state"],
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def build_module_rules(module: dict[str, Any]) -> list[str]:
    rules = []
    page_titles = [page["title"] for page in module.get("pages", [])]
    if "订单大厅" in page_titles:
        rules.append("订单大厅以批量处理为主，说明该页面面向高频订单运营，而不是单笔客服查询。")
        rules.append("高级订单管理弹窗允许直接修改联系人、地址、金额、附件和备注，说明处理动作集中在同一个入口完成。")
    if any("财务审核" in title for title in page_titles):
        rules.append("财务审核页面把附件、金额、AI识别金额和差值放在同一行，说明审核重点是核对金额与凭证是否一致。")
        rules.append("页面同时提供批量通过和批量拒绝，说明审核流程存在规模化处理场景。")
    if "供应商配置" in page_titles:
        rules.append("供应商规则由分单规则、查询范围、字段展示和商品配置共同构成，说明供应商权限和可见性是可配置的。")
        rules.append("供应商支持优先级，说明多条规则同时命中时存在排序决策。")
    if "供应商订单" in page_titles:
        rules.append("供应商订单页展示的字段比后台订单页更聚焦履约，说明供应商只需要看到有限的订单信息。")
    if "公告管理" in page_titles:
        rules.append("公告包含状态、主题颜色和渠道，说明公告不仅有内容属性，还有投放范围和视觉属性。")
    if "订单仪表盘" in page_titles:
        rules.append("看板既有今日指标也有总体指标，说明系统同时关注短期波动和长期积压。")
    if "个人任务" in page_titles:
        rules.append("个人任务页面强调一键认领，说明系统希望把公共订单池快速转成个人待办。")
        rules.append("个人任务保留订单状态、联系人、地址和错误信息，说明个人处理阶段既要推进状态，也要处理异常。")

    return unique_preserve_order(rules)


def build_exception_scenarios(module: dict[str, Any]) -> str:
    labels = collect_state_labels(module)
    sections: list[str] = []

    if module["key"] == "orders" and "信息错误" in labels:
        sections.extend(
            [
                "### 信息错误场景",
                "",
                "1. 触发条件：配送时发现地址异常、联系人信息有误、电话无法联系，或其他履约关键信息不完整。",
                "2. 处理流程：订单进入“信息错误”后，需要人工联系用户或用户自行修正，修正完成后进入“信息已修改”或重新回到“已提交/排队发货中”。",
                "3. 业务规则：信息错误订单不会自动继续履约，必须人工介入后才能恢复流转。",
                "",
            ]
        )
    if module["key"] == "orders" and "订单异常" in labels:
        sections.extend(
            [
                "### 订单异常场景",
                "",
                "1. 触发条件：库存不足、商品不可履约、用户主动取消，或其他导致正常链路无法继续的异常。",
                "2. 处理流程：订单进入“订单异常”后，需要由认领人或运营人员手动判断是否重新分派、回退重提或终止处理。",
                "3. 业务规则：异常订单通常不应直接计入正常完成链路，需要单独跟踪和处理。",
                "",
            ]
        )
    if module["key"] in {"finance", "finance-audit"}:
        sections.extend(
            [
                "### 审核拒绝场景",
                "",
                "1. 触发条件：附件凭证不足、金额差异异常、地址或履约信息无法支撑通过结论。",
                "2. 处理流程：审核人员执行拒绝后，订单进入异常或重提分支，等待运营或相关责任人补充材料后再次提交。",
                "3. 业务规则：拒绝并不代表订单结束，而是进入需要补正的回流链路。",
                "",
            ]
        )
    if module["key"] == "supplier" and "已挂起" in labels:
        sections.extend(
            [
                "### 供应商履约挂起场景",
                "",
                "1. 触发条件：供应商暂时无法履约、信息待确认，或配送过程中出现阻塞。",
                "2. 处理流程：订单进入挂起状态后，需等待人工跟进处理，再决定是否恢复配送或继续异常处理。",
                "3. 业务规则：挂起状态用于暂停履约，不应被误判为完成。",
                "",
            ]
        )

    if not sections:
        return "当前未识别到高置信异常处理场景。"
    return "\n".join(sections).rstrip()


def build_module_pending(module: dict[str, Any], frontend_present: bool) -> list[str]:
    pending = []
    menu_only_count = sum(1 for page in module.get("pages", []) if page.get("capture_status") == "menu_only")
    if not module.get("pages") and frontend_present:
        pending.append("当前模块没有采集到页面细节，可能存在隐藏入口或权限限制。")
    if not module.get("pages") and not frontend_present:
        pending.append("当前没有运行中前端页面，页面级字段定义仍需后续补充。")
    if menu_only_count:
        pending.append(f"当前模块仍有 {menu_only_count} 个页面只完成了菜单级识别，初始化阶段应继续补采页面结构与请求证据。")
    if module["key"] == "orders":
        pending.append("订单状态之间的触发条件、角色限制和异常回流规则还可以继续细化。")
    if module["key"] in {"finance", "finance-audit"}:
        pending.append("通过、拒绝和重新提交的业务口径仍建议与财务方确认。")
    if module["key"] == "supplier-config":
        pending.append("分单规则表达式的完整语法和冲突解决策略仍需补充说明。")
    return unique_preserve_order(pending)


def render_ai_context(
    facts: dict[str, Any],
    frontend: dict[str, Any] | None,
    modules: dict[str, dict[str, Any]],
    report_date: str,
) -> str:
    priority_modules = choose_priority_modules(modules, limit=6)
    visible_leaf_count = count_visible_leaf_pages(frontend)
    fully_captured_count = sum(
        1
        for module in modules.values()
        for page in module.get("pages", [])
        if page.get("capture_status") != "menu_only"
    )
    menu_only_count = sum(
        1
        for module in modules.values()
        for page in module.get("pages", [])
        if page.get("capture_status") == "menu_only"
    )
    module_lines = []
    for key in priority_modules:
        module = modules[key]
        page_titles = ", ".join(page["title"] for page in module.get("pages", [])[:3])
        suffix = f"，重点页面：{page_titles}" if page_titles else ""
        module_lines.append(f"{module['title']}：{infer_module_goal(key, module)}{suffix}")

    status_lines = []
    for key in priority_modules:
        for line in build_status_lines(modules[key])[:2]:
            status_lines.append(f"{modules[key]['title']}：{line}")
    if not status_lines:
        status_lines.append("当前尚未识别出高置信状态流转。")

    evidence_lines = []
    if frontend and frontend.get("source_repo"):
        evidence_lines.append("本次文档优先使用前端源码作为产品表层证据，再结合后端代码补足业务规则。")
        evidence_lines.append("当前没有依赖浏览器逐页点击，因此覆盖更完整，但个别运行态文案仍可能需要页面校对。")
    elif frontend:
        evidence_lines.append("本次文档优先使用运行中前端页面作为产品表层证据。")
        evidence_lines.append("代码与仓库文档仅用于补足页面上看不到的业务规则和状态命名。")
    else:
        evidence_lines.append("本次没有接入运行中前端页面，文档只能根据代码与已有文档推断产品结构。")
        evidence_lines.append("字段定义、按钮文案和可视化流程的准确度会低于前端增强模式。")

    return f"""# {facts.get('repo_name', 'repository')} AI 产品速览

## 文档用途

这份速览文档面向 AI 产品经理 agent。它不是技术说明书，而是帮助 agent 用最短路径理解这个系统有哪些业务模块、应该先看哪些页面、核心流程怎么走。

## 一句话理解系统

这是一个围绕订单履约展开的运营后台，覆盖订单处理、财务审核、供应商协同、经营看板和公告运营等能力。

## 建议阅读顺序

- 先读 `./{report_date}-main-prd.md`，建立完整产品全景。
- 再按优先级阅读模块附录：{', '.join(priority_modules) if priority_modules else '暂无'}。
- 如果要深挖处理链路，优先看订单运营和财务审核。
- 如果要理解外部协同，优先看供应商配置和供应商订单。

## 高优先级模块

{bullet_list(module_lines, "暂无高优先级模块。")}

## 初始化覆盖检查

{bullet_list(
    [
        f"识别到的可见叶子页面数：{visible_leaf_count}。" if frontend else "本次没有运行中前端页面，无法进行叶子页面覆盖统计。",
        f"已完成页面级采集的页面数：{fully_captured_count}。",
        f"仍处于菜单级占位的页面数：{menu_only_count}。",
    ],
    "暂无覆盖检查结果。",
)}

## 最关键的状态流转

{bullet_list(status_lines, "暂无关键状态流转。")}

## 证据边界

{bullet_list(evidence_lines, "暂无证据边界说明。")}
"""


def render_main_prd(
    facts: dict[str, Any],
    frontend: dict[str, Any] | None,
    modules: dict[str, dict[str, Any]],
    report_date: str,
) -> str:
    all_module_keys = choose_priority_modules(modules, limit=len(modules))
    roles = unique_preserve_order(role for key in all_module_keys for role in infer_roles(key, modules[key]))
    if frontend and frontend.get("source_repo"):
        frontend_note = "本次文档优先根据前端源码整理页面、字段、弹窗和接口，再结合后端代码补足状态、规则与闭环。"
    elif frontend:
        frontend_note = "本次文档优先根据运行中的前端页面整理，代码和仓库文档只用于补足页面上看不到的规则。"
    else:
        frontend_note = "本次未接入运行中的前端页面，文档仅能根据代码命名、已有文档和源码路由推断产品结构。"

    page_index_lines = []
    closure_lines = []
    for key in all_module_keys:
        module = modules[key]
        for page in module.get("pages", []):
            page_index_lines.append(f"{module['title']} / {page['title']}：{page.get('route', '未记录')}")
            closure_lines.extend(build_page_closure_summary(page, module, frontend)[:1])

    key_flow_blocks = []
    if "orders" in modules:
        key_flow_blocks.append("### 订单处理主流程\n\n" + module_flow_mermaid("orders"))
    if "finance" in modules or "finance-audit" in modules:
        key_flow_blocks.append("### 财务审核流程\n\n" + module_flow_mermaid("finance"))
    if "supplier-config" in modules:
        key_flow_blocks.append("### 供应商规则生效流程\n\n" + module_flow_mermaid("supplier-config"))

    assumptions = []
    if not frontend:
        assumptions.append("字段定义和按钮文案缺少运行中页面佐证，建议后续接入前端补全。")
    if "orders" in modules:
        assumptions.append("订单状态的完整触发条件和角色限制仍建议进一步细化成状态机专题文档。")
    if not facts.get("docs"):
        assumptions.append("仓库自带业务文档较少，部分规则可能仍依赖隐性口径。")
    flow_section = "\n\n".join(key_flow_blocks) if key_flow_blocks else "当前未形成高置信的业务流程图。"
    status_section = bullet_list(
        unique_preserve_order(
            [line for key in all_module_keys for line in build_status_lines(modules[key])]
        ),
        "暂无关键状态与业务规则。",
    )
    state_diagram_blocks = []
    for key in choose_priority_modules(modules, limit=min(len(modules), 10)):
        module = modules[key]
        if module.get("state_machines"):
            state_diagram_blocks.append(f"### {module['title']}\n\n{build_state_diagram(module['state_machines'][0])}")
    state_diagram_section = "\n\n".join(state_diagram_blocks) if state_diagram_blocks else "当前未识别到可视化状态机图。"
    visible_leaf_count = count_visible_leaf_pages(frontend)
    fully_captured_count = sum(
        1
        for module in modules.values()
        for page in module.get("pages", [])
        if page.get("capture_status") != "menu_only"
    )
    menu_only_count = sum(
        1
        for module in modules.values()
        for page in module.get("pages", [])
        if page.get("capture_status") == "menu_only"
    )

    return f"""# {facts.get('repo_name', 'repository')} 产品需求文档

## 文档说明

{frontend_note}

## 产品定位

系统围绕“订单从提交到履约完成”的主链路展开，后台通过订单大厅完成日常处理，通过财务审核页面完成结果确认，通过供应商模块支撑外部履约，通过仪表盘观察整体经营表现，并用公告模块承担运营触达。

## 目标角色

{bullet_list(roles, "当前角色仍需确认。")}

## 顶层导航与信息架构

{bullet_list(build_navigation_lines(frontend, modules), "当前没有采集到明确的导航结构。")}

## 初始化覆盖检查

{bullet_list(
    [
        f"本次共识别到 {visible_leaf_count} 个可见叶子页面。" if frontend else "本次未接入运行中前端页面，无法进行菜单级覆盖检查。",
        f"其中 {fully_captured_count} 个页面已完成页面级采集，可直接用于字段、状态和操作反推。",
        f"其中 {menu_only_count} 个页面仍停留在菜单级占位，后续应继续打开页面并补采请求与交互。",
    ],
    "暂无初始化覆盖检查结果。",
)}

## 模块总览

{bullet_list(build_module_overview_lines(modules), "暂无模块总览。")}

## 核心业务对象

{bullet_list(infer_business_objects(modules), "暂无核心业务对象。")}

## 核心业务流程

{flow_section}

## 关键状态与业务规则

{status_section}

## 关键状态机图

{state_diagram_section}

## 前后端闭环说明

{bullet_list(unique_preserve_order(closure_lines), "当前还缺少足够的页面请求证据来证明完整闭环。")}

## 页面规格索引

{bullet_list(page_index_lines, "当前没有采集到页面规格。")}

## 假设与待确认

{bullet_list(assumptions, "暂无额外待确认项。")}
"""


def render_module_prd(module: dict[str, Any], frontend_present: bool, frontend: dict[str, Any] | None) -> str:
    roles = infer_roles(module["key"], module)
    state_diagrams = [build_state_diagram(machine) for machine in module.get("state_machines", [])]
    overview_lines = [
        infer_module_goal(module["key"], module),
        f"当前覆盖页面数：{len(module.get('pages', []))}。",
        f"推荐角色：{'、'.join(roles)}。",
    ]
    page_lines = []
    for page in module.get("pages", []):
        breadcrumb = " > ".join(page.get("breadcrumbs", [])) if page.get("breadcrumbs") else page.get("route", "未记录")
        page_lines.append(f"{page['title']}：{breadcrumb}")
    if not page_lines:
        page_lines.append("当前没有采集到运行中页面，模块规格只能维持在业务概览层。")

    sections = [
        f"# 模块附录：{module['title']}",
        "",
        "## 模块概览",
        "",
        bullet_list(overview_lines, "暂无模块概览。"),
        "",
        "## 覆盖页面",
        "",
        bullet_list(page_lines, "暂无覆盖页面。"),
        "",
    ]

    if module.get("pages"):
        for page in module["pages"]:
            sections.extend([render_page_spec(page, module, roles, frontend), ""])
    else:
        sections.extend(
            [
                "## 当前可确认的业务能力",
                "",
                bullet_list(
                    [
                        infer_module_goal(module["key"], module),
                        "尚未接入页面证据，字段定义和交互细节需要后续补充。",
                    ],
                    "暂无业务能力描述。",
                ),
                "",
                "## 模块流程图",
                "",
                module_flow_mermaid(module["key"]),
                "",
            ]
        )

    sections.extend(
        [
            "## 模块业务规则",
            "",
            bullet_list(build_module_rules(module), "当前未提取到显式业务规则。"),
            "",
            "## 后端支撑索引",
            "",
            render_route_index(module, frontend),
            "",
            "## 状态与流转",
            "",
            bullet_list(build_status_lines(module), "当前未提取到显式状态流转。"),
            "",
            "### 状态机图",
            "",
            "\n\n".join(state_diagrams) if state_diagrams else "当前未识别到可视化状态机图。",
            "",
            "## 异常处理场景",
            "",
            build_exception_scenarios(module),
            "",
            "## 与其他模块关系",
            "",
            bullet_list(MODULE_DEPENDENCIES.get(module["key"], ["上下游关系仍需结合业务侧口径确认。"]), "暂无上下游关系。"),
            "",
            "## 待确认项",
            "",
            bullet_list(build_module_pending(module, frontend_present), "暂无待确认项。"),
        ]
    )
    return "\n".join(sections).rstrip()


def write_outputs(
    facts: dict[str, Any],
    frontend: dict[str, Any] | None,
    output_dir: Path,
    report_date: str,
) -> list[Path]:
    modules = merge_modules(facts, frontend)
    output_dir.mkdir(parents=True, exist_ok=True)

    ai_context_path = output_dir / f"{report_date}-ai-context.md"
    main_path = output_dir / f"{report_date}-main-prd.md"
    ai_context_path.write_text(render_ai_context(facts, frontend, modules, report_date) + "\n")
    main_path.write_text(render_main_prd(facts, frontend, modules, report_date) + "\n")

    module_dir = output_dir / f"{report_date}-modules"
    module_dir.mkdir(parents=True, exist_ok=True)
    written = [ai_context_path, main_path]

    module_limit = len(modules)
    for index, key in enumerate(choose_priority_modules(modules, limit=module_limit), start=1):
        module = modules[key]
        module_path = module_dir / f"{index:02d}-{module['key']}.md"
        module_path.write_text(render_module_prd(module, frontend_present=frontend is not None, frontend=frontend) + "\n")
        written.append(module_path)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate product-first PRD markdown from extracted evidence.")
    parser.add_argument("--facts", required=True, help="Path to repo facts JSON")
    parser.add_argument("--frontend-evidence", help="Optional frontend evidence JSON path")
    parser.add_argument("--output-dir", required=True, help="Directory to write markdown outputs")
    parser.add_argument("--language", default="zh", choices=["zh", "en"], help="Output language")
    parser.add_argument("--date", dest="report_date", default=str(date.today()), help="Report date prefix")
    args = parser.parse_args()

    facts = load_json(Path(args.facts))
    frontend = load_json(Path(args.frontend_evidence)) if args.frontend_evidence else None
    written = write_outputs(facts, frontend, Path(args.output_dir), args.report_date)
    print(json.dumps({"written_files": [str(path) for path in written]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
