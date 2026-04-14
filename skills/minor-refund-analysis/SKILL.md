---
name: minor-refund-analysis
description: Use when handling 未成年人退款、退款审核、行为判定 requests for a specific player account in a known game context after a player ID is available. Generate a standardized behavior summary from downstream-returned data without directly determining the player's real age.
---

# 未成年人退款行为分析

## 目标

- 仅做行为特征分析，不直接判定玩家真实年龄。
- 所有结论必须基于接口返回数据；没有数据就明确说明“数据不足”，不得补充主观推断。
- 输出必须使用统一模板，重点是“摘要化、证据化、可回写”。

## 输入

- 必填：`uid`
- `game_id` 处理方式：
  - 用户明确提供时，直接使用。
  - 若当前上下文已明确为单一游戏环境，可使用业务侧预设值。
  - 若上下文不明确且无预设值，再补问 `game_id`。
- 时间范围不由当前 skill 传入，由下游接口或业务流程控制返回的数据范围；AI 只分析返回结果，不自行裁剪时间窗口。

## 执行流程

1. 调用 `getUserBasicInfo` 接口获取玩家数据，接口说明见 [references/api.md](./references/api.md)。
2. 读取接口返回的 `data.analysisMetrics` 做行为判断（登录小时分布、充值关键时段分布、缺失计数等）。
3. 结合 `data.uid`、`cTime`、`lTime`、`lvl`、`dmd` 输出统一模板。
4. 如 `analysisMetrics` 缺失、版本不匹配或关键字段缺失，输出"当前接口返回的行为摘要不足，暂无法形成有效判断"。
5. 如需引用日期语义，只能使用接口返回的 `weekdayCn`、`isHoliday`、`holidayName`、`isAdjustedWorkday`，不允许本地脚本计算，也不允许 AI 自行推断。

## 输出要求

- 登录分析：按小时聚合，只展示达到阈值的高频时段。
- 充值分析：只聚焦 `08:00-09:00`、`12:00-13:00`、`22:00-24:00` 三个关键时段。
- 聊天记录：当前接口未返回时，固定输出默认文案。
- 综合判定：只能写“未见明显重合特征”“存在部分/较多重合特征，建议进一步核查”“数据不足无法判断”这类结论，不得直接给出年龄定性。

## 硬性约束

- 禁止使用：`冲动消费`、`偷玩`、`缺乏消费理性`、`极其异常`、`典型未成年模式` 等带心理推断或定性倾向的措辞。
- 禁止在没有日历依据时写”周末/假期”；`isHoliday=true` 时才允许写”节假日”，`isAdjustedWorkday=true` 时才允许写”调休补班”。
- `weekdayCn` 可直接引用；v1 版本不存在单独的”周末”字段。
- 禁止因为单一维度数据异常就直接下“未成年人充值”结论。
- 当登录数据缺失时，综合判定必须降低结论强度。

## 标准输出模板

```text
玩家ID：{uid}
账号创建时间：{cTime}
最后登录时间：{lTime}
当前游戏等级：{lvl}级；剩余元宝：{dmd}
充值情况：
{充值分析}
登录情况：
{登录分析}
聊天记录情况：
当前聊天记录中未发现涉及年龄相关的聊天信息。
综合判定：
{综合判定}
```
