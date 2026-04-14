# Minor Refund Analysis Metrics Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 `getUserBasicInfo` 响应中新增纯计算型 `analysisMetrics` 字段，并让 `minor-refund-analysis` skill 强依赖该字段输出未成年人退款行为分析文案。

**Architecture:** 保持 `modo-api-service` 继续负责下游转发与日历增强，再增加一个纯函数式 metrics builder，对 `loginList` 和 `rchgList` 做无业务判断的分桶统计。`pocket-skills` 侧不再自行从明细聚合，而是消费 `analysisMetrics` 做阈值判断、窗口合并和结论生成，从而把“计算”与“判定”严格拆开。

**Tech Stack:** Python 3.8+、FastAPI、Pydantic、pytest/unittest、Markdown skill docs

---

### Task 1: 锁定服务端 `analysisMetrics` 契约测试

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/tests/test_game_user_basic_info.py:241-430`
- Test: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/tests/test_game_user_basic_info.py`

**Step 1: 写失败测试，锁定 client 侧 metrics 输出**

在 `TestGameUserApiClient` 里追加一个新测试，覆盖登录小时桶、充值关键时段桶、缺失时间计数：

```python
@patch.dict(
    "os.environ",
    {
        "GAME.1001.COMMON_KEY": "key-1001",
        "GET_USER_BASIC_INFO_URL": "https://global.example.com/user",
        "GET_USER_BASIC_INFO_ENV": "test-sdk",
    },
    clear=False,
)
@patch("modo_api_service.api_client.requests.post")
def test_get_user_basic_info_adds_analysis_metrics(self, mock_post):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": 1,
        "msg": "success",
        "data": {
            "uid": 12345,
            "cTime": "2026-03-01 09:00:00",
            "lTime": "2026-03-16 23:23:00",
            "lvl": 40,
            "dmd": 20,
            "rchgCnt": 3,
            "loginList": [
                {"time": "2026-03-16 23:23:00", "ip": "1.2.3.4"},
                {"time": "2026-03-16 23:58:00", "ip": "1.2.3.4"},
                {"time": "2026-03-16 10:01:00", "ip": "1.2.3.4"},
            ],
            "rchgList": [
                {"rid": 1, "cny": 68, "reqTime": "2026-02-12 22:05:00"},
                {"rid": 2, "cny": 6, "reqTime": "2026-02-12 23:57:00"},
                {"rid": 3, "cny": 30, "reqTime": None},
            ],
        },
        "ms": 1710000000999,
    }
    mock_post.return_value = mock_response

    result = self.client.get_user_basic_info(game_id=1001, uid="12345")

    metrics = result["data"]["analysisMetrics"]
    assert metrics["version"] == "minor_refund_metrics_v1"
    assert metrics["counts"]["loginRecordCount"] == 3
    assert metrics["counts"]["rechargeRecordCount"] == 3
    assert metrics["counts"]["rechargeRecordWithTimeCount"] == 2
    assert metrics["counts"]["rechargeRecordMissingTimeCount"] == 1
    assert metrics["login"]["hourBuckets"] == {"10": 1, "23": 2}
    assert metrics["recharge"]["hourBuckets"] == {"22": 1, "23": 1}
    assert metrics["recharge"]["keyWindowBuckets"] == {
        "08:00-09:00": 0,
        "12:00-13:00": 0,
        "22:00-24:00": 2,
    }
```

**Step 2: 写失败测试，锁定 API 响应透传**

在 `TestGameUserBasicInfoApi.test_post_success` 中补充 `analysisMetrics` 断言：

```python
self.assertEqual(
    response.json()["data"]["analysisMetrics"]["version"],
    "minor_refund_metrics_v1",
)
self.assertEqual(
    response.json()["data"]["analysisMetrics"]["counts"]["loginRecordCount"],
    1,
)
self.assertEqual(
    response.json()["data"]["analysisMetrics"]["recharge"]["keyWindowBuckets"]["22:00-24:00"],
    0,
)
```

同时把 mocked downstream 响应保持为**不包含** `analysisMetrics`，确保该字段由本服务生成而不是下游透传。

**Step 3: 运行测试确认失败**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -k "analysis_metrics or test_post_success" -v
```

Expected: FAIL，提示 `analysisMetrics` 缺失。

**Step 4: 再跑一次确认失败稳定**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -k "analysis_metrics or test_post_success" -v
```

Expected: 同样 FAIL，错误稳定在缺失字段而不是其他环境问题。

**Step 5: 提交测试检查点**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add tests/test_game_user_basic_info.py
git commit -m "test: lock analysis metrics contract"
```

### Task 2: 实现纯计算型 metrics builder

**Files:**
- Create: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/user_basic_info_metrics.py`
- Test: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/tests/test_game_user_basic_info.py`

**Step 1: 写最小纯函数模块骨架**

创建新文件：

```python
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

SUPPORTED_FORMATS = ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S")
KEY_WINDOWS = (
    ("08:00-09:00", 8),
    ("12:00-13:00", 12),
    ("22:00-24:00", 22, 23),
)


def build_user_basic_info_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    ...
```

**Step 2: 先写时间解析与小时桶最小实现**

```python
def _parse_hour(raw: Any) -> Optional[str]:
    if not isinstance(raw, str) or not raw:
        return None
    for fmt in SUPPORTED_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%H")
        except ValueError:
            continue
    return None


def _build_hour_buckets(records: Iterable[Dict[str, Any]], time_key: str) -> Dict[str, int]:
    counter = Counter()
    for record in records:
        hour = _parse_hour(record.get(time_key))
        if hour is not None:
            counter[hour] += 1
    return dict(sorted(counter.items()))
```

**Step 3: 补关键时段桶与缺失计数实现**

```python
def _build_key_window_buckets(hour_buckets: Dict[str, int]) -> Dict[str, int]:
    return {
        "08:00-09:00": hour_buckets.get("08", 0),
        "12:00-13:00": hour_buckets.get("12", 0),
        "22:00-24:00": hour_buckets.get("22", 0) + hour_buckets.get("23", 0),
    }


def build_user_basic_info_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    login_list = data.get("loginList") if isinstance(data.get("loginList"), list) else []
    recharge_list = data.get("rchgList") if isinstance(data.get("rchgList"), list) else []

    login_hour_buckets = _build_hour_buckets(login_list, "time")
    recharge_hour_buckets = _build_hour_buckets(recharge_list, "reqTime")
    recharge_with_time = sum(1 for item in recharge_list if _parse_hour(item.get("reqTime")) is not None)

    return {
        "version": "minor_refund_metrics_v1",
        "counts": {
            "loginRecordCount": len(login_list),
            "rechargeRecordCount": len(recharge_list),
            "rechargeRecordWithTimeCount": recharge_with_time,
            "rechargeRecordMissingTimeCount": len(recharge_list) - recharge_with_time,
        },
        "login": {
            "hourBuckets": login_hour_buckets,
        },
        "recharge": {
            "hourBuckets": recharge_hour_buckets,
            "keyWindowBuckets": _build_key_window_buckets(recharge_hour_buckets),
        },
    }
```

**Step 4: 运行服务测试确认通过**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -k "analysis_metrics or test_post_success" -v
```

Expected: PASS。

**Step 5: 提交 metrics builder**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add modo_api_service/user_basic_info_metrics.py tests/test_game_user_basic_info.py
git commit -m "feat: add user basic info metrics builder"
```

### Task 3: 接入 `getUserBasicInfo` 流程并补 response model

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/api_client.py:144-178`
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/models.py:80-99`
- Test: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/tests/test_game_user_basic_info.py`

**Step 1: 写失败测试，锁定 response model 不丢字段**

在 `test_post_success` 里新增更细一层断言，确保 FastAPI response model 不会把 `analysisMetrics` 丢掉：

```python
self.assertIn("analysisMetrics", response.json()["data"])
self.assertEqual(
    sorted(response.json()["data"]["analysisMetrics"]["login"]["hourBuckets"].keys()),
    ["23"],
)
```

**Step 2: 在 client 中串联 metrics builder**

修改 `api_client.py`：

```python
from .user_basic_info_metrics import build_user_basic_info_metrics

...
result = response.json()
if "ms" not in result:
    result["ms"] = int(time.time() * 1000)
result = enrich_user_basic_info_response(result)
data = result.get("data")
if isinstance(data, dict):
    data["analysisMetrics"] = build_user_basic_info_metrics(data)
return result
```

要求：
- 只在 `data` 为 `dict` 时追加字段。
- 失败分支不改。
- 先做日历增强，再做 metrics，保持后续若有日期相关统计也能复用增强结果。

**Step 3: 在 Pydantic 模型中补字段**

在 `models.py` 中增加模型，避免响应模型丢字段：

```python
class UserBasicInfoCounts(BaseModel):
    login_record_count: int = Field(..., alias="loginRecordCount")
    recharge_record_count: int = Field(..., alias="rechargeRecordCount")
    recharge_record_with_time_count: int = Field(..., alias="rechargeRecordWithTimeCount")
    recharge_record_missing_time_count: int = Field(..., alias="rechargeRecordMissingTimeCount")


class HourBucketMetrics(BaseModel):
    hour_buckets: Dict[str, int] = Field(default_factory=dict, alias="hourBuckets")


class RechargeMetrics(BaseModel):
    hour_buckets: Dict[str, int] = Field(default_factory=dict, alias="hourBuckets")
    key_window_buckets: Dict[str, int] = Field(default_factory=dict, alias="keyWindowBuckets")


class AnalysisMetrics(BaseModel):
    version: str
    counts: UserBasicInfoCounts
    login: HourBucketMetrics
    recharge: RechargeMetrics
```

并在 `UserBasicInfoData` 下新增：

```python
analysis_metrics: Optional[AnalysisMetrics] = Field(
    default=None,
    alias="analysisMetrics",
    description="未成年人退款分析用纯计算汇总",
)
```

**Step 4: 跑完整相关测试**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -v
```

Expected: PASS，无字段被 response model 丢弃。

**Step 5: 提交 API 接入与模型更新**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add modo_api_service/api_client.py modo_api_service/models.py tests/test_game_user_basic_info.py
git commit -m "feat: expose analysis metrics in get user basic info"
```

### Task 4: 更新 API 文档，明确“只计算不判定”

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/docs/GET_USER_BASIC_INFO_API.md:141-225`
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/README.md:52-111`

**Step 1: 在接口文档中新增字段表**

在 `data` 字段说明后新增 `analysisMetrics` 小节，明确：

- 这是服务端聚合的纯计算结果
- 不代表未成年人结论
- 不包含阈值判断、中文文案、风险等级

示例文案：

```md
| `analysisMetrics` | `object` | 未成年人退款分析所需的纯计算型汇总，不包含业务判定 |
```

**Step 2: 在文档中写清子字段**

补充：

```md
| `version` | `string` | 汇总结构版本，当前固定为 `minor_refund_metrics_v1` |
| `counts.loginRecordCount` | `int` | 当前返回登录记录条数 |
| `counts.rechargeRecordMissingTimeCount` | `int` | 当前返回充值记录中缺失或不可解析时间的条数 |
| `login.hourBuckets` | `object` | 登录记录按小时聚合后的计数 |
| `recharge.hourBuckets` | `object` | 充值记录按小时聚合后的计数 |
| `recharge.keyWindowBuckets` | `object` | 充值关键时段计数，仅含 `08:00-09:00`、`12:00-13:00`、`22:00-24:00` |
```

**Step 3: 在 README 同步一句总览说明**

把现有“离线日历增强”描述扩成：

```md
- **基础信息请求转发**: 支持中台通过 `/modo/api/getUserBasicInfo` 查询游戏用户基础信息，并对 `loginList` / `rchgList` 做离线日历增强，同时附带 `analysisMetrics` 纯计算型汇总供 skill 使用
```

**Step 4: 目视检查文档内容**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
rg -n "analysisMetrics|纯计算|不包含业务判定" docs/GET_USER_BASIC_INFO_API.md README.md
```

Expected: 命中新增文案，无“风险等级”“结论”等误导表述。

**Step 5: 提交文档更新**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add docs/GET_USER_BASIC_INFO_API.md README.md
git commit -m "docs: describe analysis metrics contract"
```

### Task 5: 更新 skill 文档，改为强依赖 `analysisMetrics`

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/SKILL.md:23-45`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/references/api.md`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/references/analysis-rules.md`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/codex/SKILL.md`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/claude-code/SKILL.md`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/cursor/SKILL.md`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/gemini-code/SKILL.md`

**Step 1: 先写文档契约测试**

扩展现有 `test_contract_docs.py`，增加对 `analysisMetrics` 的断言：

```python
self.assertIn("analysisMetrics", text)
self.assertIn("loginRecordCount", text)
self.assertIn("keyWindowBuckets", text)
```

并加禁止项：

```python
self.assertNotIn("skill 自行聚合", text)
self.assertNotIn("本地脚本计算登录高频", text)
```

**Step 2: 跑 skill 契约测试确认失败**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
python -m unittest skills.minor-refund-analysis.tests.test_contract_docs
```

Expected: FAIL，因为文档尚未提到 `analysisMetrics`。

**Step 3: 修改主 skill 文档**

把执行流程改成：

```md
1. 调用 `getUserBasicInfo` 接口获取玩家数据。
2. 读取接口返回的 `data.analysisMetrics` 做行为判断。
3. 结合 `data.uid`、`cTime`、`lTime`、`lvl`、`dmd` 输出统一模板。
4. 如 `analysisMetrics` 缺失、版本不匹配或关键字段缺失，输出“当前接口返回的行为摘要不足，暂无法形成有效判断”。
```

**Step 4: 修改规则文档**

在 `references/analysis-rules.md` 中：

- 字段映射表新增 `analysisMetrics.*`
- 登录分析规则改为“依据 `login.hourBuckets` 进行阈值判断与连续小时合并”
- 充值分析规则改为“依据 `recharge.keyWindowBuckets` 判断关键时段是否集中”
- 明确 skill 不再从 `loginList/rchgList` 自己计数

建议加入示例：

```md
| 登录小时分布 | `data.analysisMetrics.login.hourBuckets` | 服务端纯计算汇总 |
| 充值关键时段分布 | `data.analysisMetrics.recharge.keyWindowBuckets` | 服务端纯计算汇总 |
| 缺失充值时间数 | `data.analysisMetrics.counts.rechargeRecordMissingTimeCount` | 服务端纯计算汇总 |
```

**Step 5: 修改平台适配器文档**

各平台 `SKILL.md` 统一改成：

```md
- use `data.analysisMetrics` as the source of truth for aggregation
- do not re-aggregate `loginList` or `rchgList` locally
- if `analysisMetrics` is missing, treat the data as insufficient
```

**Step 6: 跑契约测试确认通过**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
python -m unittest skills.minor-refund-analysis.tests.test_contract_docs
```

Expected: PASS。

**Step 7: 提交 skill 文档更新**

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
git add skills/minor-refund-analysis
git commit -m "docs: require analysis metrics for refund analysis"
```

### Task 6: 用真实 UID 做联调验收

**Files:**
- Verify only: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service`
- Verify only: `/Users/ethanhuang/Desktop/codespace/pocket-skills`

**Step 1: 启动或确认 API 服务可用**

Run:

```bash
curl -s -X POST "http://127.0.0.1:8004/modo/api/getUserBasicInfo" \
  -H "Content-Type: application/json" \
  -d '{"game_id":160,"uid":"623100001"}' | jq '.status'
```

Expected: 输出 `1`。

**Step 2: 用真实 UID 核验 `analysisMetrics` 结构**

Run:

```bash
for uid in 623100001 100001 16100001 210100001 1100001 43100001; do
  echo "UID=$uid"
  curl -s -X POST "http://127.0.0.1:8004/modo/api/getUserBasicInfo" \
    -H "Content-Type: application/json" \
    -d "{\"game_id\":160,\"uid\":\"$uid\"}" | \
    jq '{uid:.data.uid,analysisMetrics:.data.analysisMetrics}'
done
```

Expected:
- 每个 UID 都有 `analysisMetrics.version`
- `623100001` 的 `recharge.keyWindowBuckets["22:00-24:00"]` 为非零
- `623100001` 的 `counts.rechargeRecordMissingTimeCount` 为 `4`
- `100001` / `210100001` / `43100001` 的 `login.hourBuckets` 中至少有小时值达到 20 以上

**Step 3: 用 skill 规则手工 spot-check 一条输出**

以 `623100001` 为例，确认 skill 只用 `analysisMetrics` 判断，最终仍输出：

- 登录情况：未发现达到展示阈值的高频登录时段
- 充值情况：主要集中在 `22:00-24:00`
- 综合判定：存在部分重合特征，而不是直接年龄定性

**Step 4: 跑两侧最终测试**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -v

cd /Users/ethanhuang/Desktop/codespace/pocket-skills
python -m unittest skills.minor-refund-analysis.tests.test_contract_docs
```

Expected: 全部 PASS。

**Step 5: 提交验收记录**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git status --short

cd /Users/ethanhuang/Desktop/codespace/pocket-skills
git status --short
```

Expected: 只有本计划涉及的文件变更，无额外脏改动。
