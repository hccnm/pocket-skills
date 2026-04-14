---
name: minor-refund-analysis
description: Gemini Code adapter for minor-refund-analysis. 基于下游返回的玩家行为数据生成统一格式的未成年人退款行为分析说明，日期语义仅引用接口已返回的日历增强字段。
license: MIT
compatibility: Agent-native workflow; calendar fields are enriched by the API, no external scripts required
metadata:
  author: pocket-skills
  version: "1.1"
---

# Minor Refund Analysis

- `../../references/api.md`
- `../../references/analysis-rules.md`

Use this skill to generate a standardized 未成年人退款行为分析说明.

Rules:

- do not determine the player's real age directly
- analyze only the data actually returned by downstream services
- do not invent or trim time ranges locally
- use only enriched calendar fields returned by the API (`weekdayCn`, `isHoliday`, `holidayName`, `isAdjustedWorkday`); do not compute dates locally
- do not write unsupported labels such as `周末` or `假期` unless the corresponding API field confirms it
- use `data.analysisMetrics` as the source of truth for aggregation (loginRecordCount, keyWindowBuckets, etc.)
- do not re-aggregate `loginList` or `rchgList` locally
- if `analysisMetrics` is missing, treat the data as insufficient
