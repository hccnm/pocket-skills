# Minor Refund Analysis Minimal Calendar Enhancement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move the minimal calendar enrichment for `getUserBasicInfo` into `modo-api-service`, and make `minor-refund-analysis` consume only the enriched API fields.

**Architecture:** Keep the enhancement inside `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service` by adding a local offline calendar snapshot plus a lightweight enricher that only decorates `loginList[].time` and `rchgList[].reqTime`. On the `pocket-skills` side, remove the bundled weekday helper and tighten all skill docs/adapters so they only reference `weekdayCn`, `isHoliday`, `holidayName`, and `isAdjustedWorkday` returned by the API.

**Tech Stack:** Python 3.8+, FastAPI, Pydantic v2, requests, pytest/unittest, Markdown skill docs

---

## Working Directories

- Service repo: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service`
- Skill repo: `/Users/ethanhuang/Desktop/codespace/pocket-skills`

## Resolved Decisions

- Do not add a generic calendar model.
- Do not add `date`, `weekdayIndex`, `weekdayEn`, `isWeekend`, `isWorkday`, or `calendarStatus`.
- Keep the offline holiday snapshot inside the service repo and never fetch it during request handling.
- If a record time string cannot be parsed, keep the original record and fill the four added fields with safe defaults instead of failing the whole API.
- Use verified 2026 examples in tests:
  - `2026-02-15` is `春节`
  - `2026-02-14` is an adjusted workday
  - `2026-02-12` is `周四`
  - `2026-03-16 23:23:00` is `周一`

### Task 1: Lock The Service-Side Calendar Contract With Tests

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/tests/test_game_user_basic_info.py:62-229`
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/tests/test_game_user_basic_info.py:242-325`

**Step 1: Write the failing tests**

Add focused client-level tests before implementation:

```python
def test_get_user_basic_info_enriches_login_and_recharge_records(self, mock_post):
    mock_response.json.return_value = {
        "status": 1,
        "msg": "success",
        "data": {
            "uid": 12345,
            "cTime": "2026-03-01 09:00:00",
            "lTime": "2026-03-16 23:23:00",
            "lvl": 40,
            "dmd": 20,
            "rchgCnt": 2,
            "loginList": [{"time": "2026-03-16 23:23:00", "ip": "1.2.3.4"}],
            "rchgList": [{"rid": 1, "cny": 68, "reqTime": "2026-02-12 21:01:00"}],
        },
    }

    result = self.client.get_user_basic_info(game_id=1001, uid="12345")

    assert result["data"]["loginList"][0]["weekdayCn"] == "周一"
    assert result["data"]["rchgList"][0]["weekdayCn"] == "周四"


def test_get_user_basic_info_marks_holiday_name(self, mock_post):
    mock_response.json.return_value = {
        "status": 1,
        "msg": "success",
        "data": {
            "uid": 12345,
            "cTime": "2026-02-01 09:00:00",
            "lTime": "2026-02-15 10:00:00",
            "lvl": 1,
            "dmd": 0,
            "rchgCnt": 1,
            "loginList": [],
            "rchgList": [{"rid": 1, "cny": 6, "reqTime": "2026-02-15 10:00:00"}],
        },
    }

    result = self.client.get_user_basic_info(game_id=1001, uid="12345")

    assert result["data"]["rchgList"][0]["isHoliday"] is True
    assert result["data"]["rchgList"][0]["holidayName"] == "春节"


def test_get_user_basic_info_marks_adjusted_workday(self, mock_post):
    ...
    assert result["data"]["loginList"][0]["isAdjustedWorkday"] is True
```

Also tighten the API integration assertion so the endpoint contract explicitly checks all four added fields on both `loginList[]` and `rchgList[]`.

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -k "enriches_login_and_recharge_records or marks_holiday_name or marks_adjusted_workday or test_post_success" -v
```

Expected: FAIL with missing `weekdayCn` / `isHoliday` / `holidayName` / `isAdjustedWorkday`, or no enrichment happening inside `GameUserAPIClient.get_user_basic_info()`.

**Step 3: Keep the failing assertions small**

Do not add broad snapshot assertions. Only assert:

- weekday text for the two sample dates
- holiday name for `2026-02-15`
- adjusted workday flag for `2026-02-14`
- default values for a normal day

**Step 4: Re-run the same test command**

Run the exact same `pytest ... -k ...` command again after any cleanup to confirm the failures are deterministic.

**Step 5: Commit the failing-test checkpoint**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add tests/test_game_user_basic_info.py
git commit -m "test: lock minimal calendar enrichment contract"
```

### Task 2: Implement The Offline Calendar Snapshot And Enricher

**Files:**
- Create: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/calendar_snapshot.py`
- Create: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/calendar_enricher.py`
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/api_client.py:143-176`
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/modo_api_service/models.py:59-93`

**Step 1: Write the minimal snapshot module**

Put the local holiday data in a dedicated file so future yearly updates do not touch the enrichment logic:

```python
# modo_api_service/calendar_snapshot.py
HOLIDAY_BY_DATE = {
    "2026-01-01": "元旦",
    "2026-02-15": "春节",
    "2026-02-16": "春节",
    # ...
}

ADJUSTED_WORKDAY_DATES = {
    "2026-01-04",
    "2026-02-14",
    "2026-02-28",
    "2026-05-09",
    "2026-09-20",
    "2026-10-10",
}
```

Use data derived from the service-maintained China holiday snapshot. Keep it as plain constants; do not introduce runtime file I/O or third-party holiday packages in the request path.

**Step 2: Implement the enricher**

Add a small, pure function module:

```python
# modo_api_service/calendar_enricher.py
WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
SUPPORTED_FORMATS = ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S")


def enrich_user_basic_info_response(result: dict) -> dict:
    data = result.get("data")
    if not isinstance(data, dict):
        return result

    data["loginList"] = [_enrich_record(item, "time") for item in data.get("loginList", [])]
    data["rchgList"] = [_enrich_record(item, "reqTime") for item in data.get("rchgList", [])]
    return result
```

`_enrich_record()` should only add:

- `weekdayCn`
- `isHoliday`
- `holidayName`
- `isAdjustedWorkday`

Defaults for unparsable or non-hit dates:

```python
{
    "weekdayCn": "",
    "isHoliday": False,
    "holidayName": "",
    "isAdjustedWorkday": False,
}
```

**Step 3: Wire the client after downstream success**

Update `GameUserAPIClient.get_user_basic_info()` so the response flow becomes:

1. `requests.post(...)`
2. `response.json()`
3. fill `ms` if missing
4. call `enrich_user_basic_info_response(result)`
5. return the enriched result

Do not touch failure branches. Do not move the logic to `web_service.py`; the hook belongs in the client flow.

**Step 4: Extend the response models**

Update `LoginInfo` and `RechargeInfo` in `models.py`:

```python
weekday_cn: str = Field(default="", description="中文星期", alias="weekdayCn")
is_holiday: bool = Field(default=False, description="是否法定节假日", alias="isHoliday")
holiday_name: str = Field(default="", description="节假日名称", alias="holidayName")
is_adjusted_workday: bool = Field(default=False, description="是否调休补班日", alias="isAdjustedWorkday")
```

This is required so FastAPI `response_model=GetUserBasicInfoResponse` stops dropping the added fields.

**Step 5: Run the service tests until they pass**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py -v
```

Expected: PASS for the new enrichment tests plus the old compatibility tests.

**Step 6: Commit the service implementation**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add modo_api_service/calendar_snapshot.py modo_api_service/calendar_enricher.py modo_api_service/api_client.py modo_api_service/models.py tests/test_game_user_basic_info.py
git commit -m "feat: add minimal calendar enrichment to getUserBasicInfo"
```

### Task 3: Sync The Service Documentation

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/docs/GET_USER_BASIC_INFO_API.md:17-204`
- Modify: `/Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service/README.md:49-141`

**Step 1: Update the interface description**

Document that `modo-api-service` enriches only `loginList[]` and `rchgList[]`, and that each record now includes:

```json
{
  "weekdayCn": "周一",
  "isHoliday": false,
  "holidayName": "",
  "isAdjustedWorkday": false
}
```

**Step 2: Update the processing flow**

Change the internal flow description from “透传下游响应” to “下游成功响应后进行本地日历增强，再返回给调用方”.

**Step 3: Update the response tables and examples**

Add the four fields to both nested response tables and expand the success example JSON accordingly. Also state explicitly that:

- `weekdayCn` is `周一` to `周日`
- `holidayName` is empty when `isHoliday=false`
- no extra weekend/workday status fields are returned in v1

**Step 4: Update the README summary**

In the top-level feature list and the `getUserBasicInfo` section, add one short note that the service now performs offline calendar enhancement for refund-analysis consumers.

**Step 5: Smoke-check the docs diff**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
rg -n "weekdayCn|isHoliday|holidayName|isAdjustedWorkday|周末|calendarStatus" README.md docs/GET_USER_BASIC_INFO_API.md
```

Expected:

- the four new fields appear in both docs
- `calendarStatus` does not appear
- no doc claims that the service returns a dedicated `周末` field

**Step 6: Commit the doc sync**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git add README.md docs/GET_USER_BASIC_INFO_API.md
git commit -m "docs: document minimal calendar enrichment fields"
```

### Task 4: Add Pocket-Skills Contract Checks Before Removing The Local Helper

**Files:**
- Create: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/tests/test_contract_docs.py`

**Step 1: Write the failing contract test**

Create a lightweight repo-local guard that reads the skill docs and adapter files as text:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MinorRefundAnalysisContractTests(unittest.TestCase):
    def test_docs_reference_api_calendar_fields_only(self):
        files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "api.md",
            ROOT / "references" / "analysis-rules.md",
            ROOT / "platforms" / "codex" / "SKILL.md",
            ROOT / "platforms" / "claude-code" / "SKILL.md",
            ROOT / "platforms" / "cursor" / "SKILL.md",
            ROOT / "platforms" / "cursor" / ".cursorrules",
            ROOT / "platforms" / "gemini-code" / "SKILL.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in files)

        self.assertIn("weekdayCn", text)
        self.assertIn("isHoliday", text)
        self.assertIn("holidayName", text)
        self.assertIn("isAdjustedWorkday", text)
        self.assertNotIn("weekday_info.py", text)
        self.assertNotIn("isWeekend", text)
```

**Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
python3 -m unittest discover -s skills/minor-refund-analysis/tests -p 'test_contract_docs.py' -v
```

Expected: FAIL because the current docs and adapters still reference `weekday_info.py` and do not mention the new API fields.

**Step 3: Keep the contract narrow**

Only assert the behavior that matters for this migration:

- required API fields are named
- local helper references are gone
- unsupported fields such as `isWeekend` are gone

Do not build a generic markdown linter.

**Step 4: Re-run the same command**

Run the same `python3 -m unittest discover -s ... -p 'test_contract_docs.py' -v` command again to make sure the failure is stable before editing the docs.

**Step 5: Commit the failing-test checkpoint**

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
git add skills/minor-refund-analysis/tests/test_contract_docs.py
git commit -m "test: add minor refund analysis contract checks"
```

### Task 5: Remove The Local Weekday Helper And Rewrite Skill Guidance

**Files:**
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/SKILL.md:23-43`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/references/api.md:25-49`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/references/analysis-rules.md:3-135`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/claude-code/SKILL.md:11-25`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/codex/SKILL.md:11-25`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/cursor/SKILL.md:11-25`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/cursor/.cursorrules:1-12`
- Modify: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/platforms/gemini-code/SKILL.md:11-25`
- Delete: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/scripts/weekday_info.py`
- Delete: `/Users/ethanhuang/Desktop/codespace/pocket-skills/skills/minor-refund-analysis/tests/test_weekday_info.py`

**Step 1: Rewrite the main skill contract**

Update `SKILL.md` so the execution rule becomes:

```md
5. 如需引用日期语义，只能使用接口返回的 `weekdayCn`、`isHoliday`、`holidayName`、`isAdjustedWorkday`，不允许本地脚本计算，也不允许 AI 自行推断。
```

Also update the hard constraints section to say:

- `weekdayCn` can be quoted directly
- `isHoliday=true` is required before writing “节假日”
- `isAdjustedWorkday=true` is required before writing “调休补班”
- no separate “周末” field exists in v1

**Step 2: Rewrite the API reference**

In `references/api.md`, replace the old note about calling `scripts/weekday_info.py` with a contract table for the four enriched fields.

Suggested snippet:

```md
`loginList[]` / `rchgList[]` 额外返回：

- `weekdayCn`
- `isHoliday`
- `holidayName`
- `isAdjustedWorkday`

AI 只能引用接口已返回的日期标签，不能自行补充 `周末`、`weekdayEn`、`isWeekend` 等字段。
```

**Step 3: Rewrite the analysis rules**

Update `references/analysis-rules.md` to remove all mentions of:

- `scripts/weekday_info.py`
- `周末`
- `weekday_en`
- “另有脚本判断”

Replace them with a new “日期字段使用规则” section:

```md
- 写“周几”时，只看 `weekdayCn`
- 写“节假日”时，必须 `isHoliday=true`
- 写“调休补班”时，必须 `isAdjustedWorkday=true`
- 若字段缺失，只能降级为不引用日期语义，不能自行推断
```

Also revise the sample correction section so no example claims unsupported “周末/假期” labels without the backing fields.

**Step 4: Rewrite all platform adapters**

For the four adapter `SKILL.md` files plus Cursor `.cursorrules`:

- remove `../../scripts/weekday_info.py`
- remove “call the bundled weekday helper”
- add “use only enriched fields returned by the API”

Gemini’s compatibility line should no longer mention an external weekday helper.

**Step 5: Delete the obsolete helper**

Delete both:

- `skills/minor-refund-analysis/scripts/weekday_info.py`
- `skills/minor-refund-analysis/tests/test_weekday_info.py`

Only delete them after all doc and adapter references are updated.

**Step 6: Run the new contract test**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
python3 -m unittest discover -s skills/minor-refund-analysis/tests -p 'test_contract_docs.py' -v
```

Expected: PASS.

**Step 7: Run a repo grep audit**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
rg -n "weekday_info.py|isWeekend|weekdayEn|weekday_index|周末" skills/minor-refund-analysis
```

Expected:

- no matches for `weekday_info.py`, `isWeekend`, `weekdayEn`, `weekday_index`
- any remaining `周末` mention must be in a prohibition sentence, not as a supported output field

**Step 8: Commit the skill-side cleanup**

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
git add skills/minor-refund-analysis
git commit -m "refactor: consume calendar enrichment fields from api only"
```

### Task 6: Final Cross-Repo Verification

**Files:**
- Verify only; no planned file edits

**Step 1: Run the full service regression**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
pytest tests/test_game_user_basic_info.py tests/test_api_client.py -v
```

Expected: PASS. `test_game_user_basic_info.py` covers the new contract, and `test_api_client.py` confirms no unrelated client regression.

**Step 2: Run the full skill-side regression**

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
python3 -m unittest discover -s skills/minor-refund-analysis/tests -p 'test_*.py' -v
```

Expected: PASS.

**Step 3: Perform the final grep audit in both repos**

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
rg -n "calendarStatus|weekdayEn|isWeekend|isWorkday" modo_api_service README.md docs/GET_USER_BASIC_INFO_API.md tests/test_game_user_basic_info.py
```

Expected: no matches.

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
rg -n "weekday_info.py|weekdayEn|isWeekend|weekday_index" skills/minor-refund-analysis
```

Expected: no matches.

**Step 4: Review the git diff repo by repo**

Run:

```bash
cd /Users/ethanhuang/Desktop/codespace/dify_pytools/modo-api-service
git status --short
git diff -- modo_api_service/api_client.py modo_api_service/models.py modo_api_service/calendar_snapshot.py modo_api_service/calendar_enricher.py docs/GET_USER_BASIC_INFO_API.md README.md tests/test_game_user_basic_info.py
```

and:

```bash
cd /Users/ethanhuang/Desktop/codespace/pocket-skills
git status --short
git diff -- skills/minor-refund-analysis
```

Expected: only the planned files changed; no surprise churn.

**Step 5: Create the final commit(s) if you deferred any**

If docs or verification fixes were deferred, create one last commit in the affected repo with a scoped message, for example:

```bash
git commit -m "chore: finish minor refund calendar enhancement rollout"
```

## Handoff Notes

- `web_service.py` should not need logic changes because the enrichment hook sits in `api_client.get_user_basic_info()`.
- The service response model must be updated before trusting endpoint-level tests, otherwise FastAPI may silently drop the added fields.
- Keep the pocket-skill migration strict: if the API fields are absent, the skill must degrade gracefully and avoid making date claims.
- Do not broaden scope into school-term tagging, English weekday names, or natural-weekend classification in this plan.
