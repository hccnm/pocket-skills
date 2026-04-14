# getUserBasicInfo 接口文档

- 路径：`POST /modo/api/getUserBasicInfo`
- 本地地址：`http://127.0.0.1:8004/modo/api/getUserBasicInfo`
- Content-Type：`application/json`

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| game_id | int/string | 是 | 游戏 ID |
| uid | string | 是 | 玩家 ID |
| cl_id | int/string | 否 | 渠道 ID |

sign、ms、env 由服务内部处理，无需传入。

## 请求示例

```bash
curl -X POST "http://127.0.0.1:8004/modo/api/getUserBasicInfo" \
  -H "Content-Type: application/json" \
  -d '{"game_id": 160, "uid": "623100001"}'
```

## 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| status | int | 1=成功，0=失败 |
| msg | string | 消息 |
| data.uid | int/string | 玩家 ID |
| data.cTime | string | 账号创建时间 |
| data.lTime | string | 最后登录时间 |
| data.lvl | int | 游戏等级 |
| data.dmd | int/float | 剩余元宝/钻石 |
| data.rchgCnt | int | 充值次数 |
| data.loginList | array | 登录记录 [{time, ip, weekdayCn, isHoliday, holidayName, isAdjustedWorkday}] |
| data.rchgList | array | 充值记录 [{rid, cny, reqTime, weekdayCn, isHoliday, holidayName, isAdjustedWorkday}] |

`loginList[]` / `rchgList[]` 额外返回（由 modo-api-service 本地增强）：

| 字段 | 类型 | 说明 |
|------|------|------|
| weekdayCn | string | 中文星期（周一至周日） |
| isHoliday | bool | 是否法定节假日 |
| holidayName | string | 节假日名称，`isHoliday=false` 时为空 |
| isAdjustedWorkday | bool | 是否调休补班日 |

`analysisMetrics` 字段（由 modo-api-service 纯计算生成，不包含业务判定）：

| 字段 | 类型 | 说明 |
|------|------|------|
| data.analysisMetrics.version | string | 结构版本，当前为 `minor_refund_metrics_v1` |
| data.analysisMetrics.counts.loginRecordCount | int | 登录记录条数 |
| data.analysisMetrics.counts.rechargeRecordCount | int | 充值记录条数 |
| data.analysisMetrics.counts.rechargeRecordWithTimeCount | int | 充值记录中有可解析时间的条数 |
| data.analysisMetrics.counts.rechargeRecordMissingTimeCount | int | 充值记录中缺失或不可解析时间的条数 |
| data.analysisMetrics.login.hourBuckets | object | 登录按小时聚合计数，键为两位小时字符串 |
| data.analysisMetrics.recharge.hourBuckets | object | 充值按小时聚合计数 |
| data.analysisMetrics.recharge.keyWindowBuckets | object | 充值关键时段计数（`08:00-09:00`、`12:00-13:00`、`22:00-24:00`） |

AI 只能引用接口已返回的日期标签，不能自行补充额外的日期语义字段。

## 前置条件

- modo-api-service 需运行在 8004 端口
- `.env` 中需配置对应 game_id 的 COMMON_KEY

## 分析窗口说明

- 该接口当前仅接收 `game_id`、`uid`（以及可选 `cl_id`），**不直接接收时间范围参数**。
- 分析窗口由下游服务或业务流程控制接口返回结果，当前 skill 不负责传递或裁剪时间范围。
- AI 只分析接口实际返回的数据；日期语义（周几、节假日、调休）已由接口直接返回，无需本地计算。
