# Bedrock Anthropic 模型事实（model-facts）

> 本文件为后续更新任务（示例脚本 / test_all.py / README.md）的**唯一真实事实来源**。
> 所有条目均来自下列 AWS 官方页面抓取，**不得**沿用仓库现有的虚构/过期条目。
> 无法从权威页面核实的细节，统一标注 **【待确认】**，严禁臆造。

## 抓取说明

- **权威总览页**：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-anthropic.html>
- **抓取方式**：本运行环境可联网（`curl` 对总览页及 19 个模型卡子页均返回 HTTP 200）。
  每个模型卡同时抓取了 `.html` 与 `.md`（文档站提供的 “View a markdown version” 版本），
  以 `.md` 版本的字段表为准（更结构化、含图标 yes/no 标记）。
- **抓取时间（UTC）**：2026-10-14T01:14Z
- **页面标题**：`Anthropic - Amazon Bedrock`
- **总览页面包含的 Billing notes**：对所有在 `bedrock-mantle` 上的 Anthropic 模型，
  推理开始前被内容分类器拒绝的请求不计费；流式开始后触发的中途拒绝按已消耗 token 计费；
  两类拒绝都返回 `stop_reason: "refusal"`。

### 重要校正（相对仓库现有 README 的虚构/错误条目）

1. 总览页**当前**列出的模型已包含 **Claude 5.5 家族（Haiku/Sonnet/Opus 5.5）、Fable 5.1、
   Mythos 5.1、Opus 5、Sonnet 5**，仓库现有 README 完全缺失这些，属“过期”。
2. **Fable 5 的数据保留模式是 `aws_review`**（不是 README 写的 `provider_data_share`）。
   `provider_data_share` 仅适用于 **Mythos 5 / Mythos 5.1**。
3. **Mantle 端点仅支持 Messages API**（Converse / Invoke 在 mantle 上均为“不支持”）。
   README“Mantle = Anthropic Messages API”方向正确，但不要在 mantle 上演示 Converse/Invoke。
4. **5.5 家族、Fable 5/5.1、Opus 4.7/4.8 等在 `bedrock-runtime` 上同时支持 Messages API**
   （不只 Converse/Invoke）。
5. **4.x 模型卡（Sonnet 4.6 / Opus 4.6 / Opus 4.5 / Haiku 4.5 / Sonnet 4.5）只写
   “Reasoning: Supported”**，并未给出 `budget_tokens` / `effort` / `adaptive` 的具体规则。
   README 中对这些模型的 thinking 细则（如“Sonnet4.5/Haiku4.5 用 enabled+budget_tokens”“Opus4.5
   首发 effort”）**无法从权威模型卡核实** → 标注【待确认】，不得作为既定事实写入文档。
6. **Haiku 4.5 的 `bedrock-runtime` 基础 Model ID 为 N/A**：按需吞吐必须用 geo/global 推理档 ID；
   单区推理需走 `bedrock-mantle` 裸 ID `anthropic.claude-haiku-4-5`。

## 通用规则（来自各模型卡 Programmatic Access 段）

- **两个端点**：
  - `bedrock-runtime`（经典）：In-Region URL `https://bedrock-runtime.{region}.amazonaws.com`。
  - `bedrock-mantle`（新）：URL `https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages`，
    使用**裸 Model ID**（不带 `us.`/`global.` 前缀），仅 Messages API。
- **跨区推理前缀（仅 `bedrock-runtime`，加在基础 ID 前）**：
  - Geo 地理围栏：`us.` / `eu.` / `au.` / `jp.` / `in.` / `apac.` / `us-gov.`（各模型支持的地理前缀不同，见下表）。
  - Global 全球路由：`global.`（部分旧模型为 N/A）。
- **Prompt 缓存**：所有列出的模型 `Explicit Prompt Caching = Yes`，`Max checkpoints = 4`，
  `TTL = 5 minutes, 1 hour`，作用字段 `system, messages, and tools`。最小 token 数见各模型。

---

## 当前模型清单（19 个，按总览页顺序）

> 字段来源：各模型卡 Model Details / Endpoints and APIs / Programmatic Access / Prompt caching 段。
> `runtime API` 列顺序为 Messages / Converse / Invoke（均为模型卡 “APIs supported on bedrock-runtime”）。
> mantle 仅 Messages，故只标 mantle 是否支持。

### 1. Claude Haiku 5.5
- 基础 Model ID：`anthropic.claude-haiku-5-5`（mantle 裸 ID 同名）
- 发布：2026-10-07 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：June 2026
- 端点：bedrock-runtime ✅、bedrock-mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.` `eu.` `au.` `jp.`；global：`global.anthropic.claude-haiku-5-5`
- Reasoning：Supported（adaptive thinking 默认开、**可关**；effort = low/medium/high/xhigh/max，默认 medium；thinking 关闭时 effort 上限为 high）。**首个带 effort 的 Haiku**。
- 采样参数：模型卡未单列 Sampling parameters 段 → 【待确认】是否有限制
- Prompt 缓存：最小 512 tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html>

### 2. Claude Sonnet 5.5
- 基础 Model ID：`anthropic.claude-sonnet-5-5`（mantle 同名）
- 发布：2026-09-28 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：June 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.` `eu.` `au.`；global：`global.anthropic.claude-sonnet-5-5`
- Reasoning：Supported（adaptive thinking 默认开；effort = low/medium/high/xhigh/max，默认 high）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 512 tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5-5.html>

### 3. Claude Opus 5.5
- 基础 Model ID：`anthropic.claude-opus-5-5`（mantle 同名）
- 发布：2026-09-22 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：June 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.` `eu.` `au.` `jp.`；global：`global.anthropic.claude-opus-5-5`
- Reasoning：Supported（adaptive thinking **始终开、不可关**；effort = low/medium/high/xhigh/max，默认 medium）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 512 tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5-5.html>

### 4. Claude Fable 5.1
- 基础 Model ID：`anthropic.claude-fable-5-1`（mantle 同名）
- 发布：2026-09-01 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：June 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.`；global：`global.anthropic.claude-fable-5-1`
- Reasoning：Supported（adaptive thinking **始终开、不可关**；effort = low/medium/high/xhigh/max，默认 high）
- 采样参数：temperature 必须 1.0 或不传；top_p 必须 0.99 或不传；temperature 与 top_p 不可同传；top_k 不支持
- Prompt 缓存：最小 512 tokens
- 数据保留：须用 Data Retention API 将模式设为 **`aws_review`** 方可使用
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5-1.html>

### 5. Claude Mythos 5.1
- 基础 Model ID：`anthropic.claude-mythos-5-1`（mantle 同名；示例用 `global.` 前缀）
- 发布：2026-09-01 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：June 2026
- 端点：runtime ✅（**mantle 未列为支持**，mantle 行缺失）
- runtime API：**【待确认】** 模型卡“Endpoint support”仅列 bedrock-runtime；API 行需复核（Mythos 5.1 为网安/生科双用途，受限）
- 跨区前缀：`us.`；global：`global.anthropic.claude-mythos-5-1`
- Reasoning：Supported（adaptive thinking **始终开、不可关**；effort = low/medium/high/xhigh/max，默认 high）
- 采样参数：temperature 必须 1.0 或不传；top_p 必须 0.99 或不传；temperature 与 top_p 不可同传；top_k 不支持
- Prompt 缓存：最小 512 tokens
- 限制：**Preview / Beta Service**；访问**受限（gated）**——通过 Anthropic trusted access 向经审核的组织开放；数据保留须设为 **`provider_data_share`**
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5-1.html>

### 6. Claude Opus 5
- 基础 Model ID：`anthropic.claude-opus-5`（mantle 同名）
- 发布：2026-07-24 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：May 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages / Converse / Invoke（具体行见模型卡；mantle Messages ✅）
- 跨区前缀：`us.` `eu.` `au.` `in.`；global：`global.anthropic.claude-opus-5`
- Reasoning：Supported（adaptive thinking 默认开、**可关**；thinking 关闭时 effort 上限为 high）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 512 tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html>

### 7. Claude Sonnet 5
- 基础 Model ID：`anthropic.claude-sonnet-5`（mantle 同名）
- 发布：2026-06-30 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：January 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages / Converse / Invoke（mantle Messages ✅）
- 跨区前缀：`us.` `eu.` `au.` `in.`；global：`global.anthropic.claude-sonnet-5`
- Reasoning：Supported（adaptive thinking 默认开，含省略 `thinking` 字段的请求；effort 可配置；可用 `"thinking": {"type": "disabled"}` 关闭）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 **1,024** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html>

### 8. Claude Mythos 5
- 基础 Model ID：`anthropic.claude-mythos-5`（mantle 裸 ID；示例 `model="anthropic.claude-mythos-5"`）
- 发布：2026-06-09 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：January 2026
- 端点：**bedrock-runtime ❌、bedrock-mantle ✅（唯一通道）**
- runtime API：全部 ❌ ｜ mantle：Messages ✅
- 跨区前缀：N/A（mantle 裸 ID）
- Reasoning：Supported（adaptive thinking 始终开、不可关；effort 可配置）
- 采样参数：temperature 必须 1.0 或不传；top_p 须 ≥ 0.99 且 < 1.0 或不传；top_k 不支持
- Prompt 缓存：最小 512 tokens
- 限制：**Preview / Beta Service**；数据保留须设为 **`provider_data_share`**
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5.html>

### 9. Claude Fable 5
- 基础 Model ID：`anthropic.claude-fable-5`（mantle 同名；示例用 `global.` 前缀）
- 发布：2026-06-09 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：January 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.`；global：`global.anthropic.claude-fable-5`
- Reasoning：Supported（adaptive thinking 始终开、不可关；effort 可配置）
- 采样参数：temperature 必须 1.0 或不传；top_p 须 ≥ 0.99 且 < 1.0 或不传；top_k 不支持
- Prompt 缓存：最小 512 tokens
- 数据保留：须将模式设为 **`aws_review`** 方可使用（**注意：不是 `provider_data_share`**）
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html>

### 10. Claude Opus 4.8
- 基础 Model ID：`anthropic.claude-opus-4-8`（mantle 同名）
- 发布：2026-05-28 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：January 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.` `eu.` `jp.` `au.` `us-gov.`；global：`global.anthropic.claude-opus-4-8`
- Reasoning：Supported（**仅** `thinking.type: "adaptive"`）
- 采样参数：模型卡未单列 → 【待确认】（README 现称 4.7/4.8 全移除采样参数，权威卡未写明 → 待确认）
- Prompt 缓存：最小 **1,024** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-8.html>

### 11. Claude Opus 4.7
- 基础 Model ID：`anthropic.claude-opus-4-7`（mantle 同名）
- 发布：2026-04-16 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：January 2026
- 端点：runtime ✅、mantle ✅
- runtime API：Messages / Converse / Invoke（mantle Messages ✅）
- 跨区前缀：`us.` `eu.` `jp.` `au.`；global：`global.anthropic.claude-opus-4-7`
- Reasoning：Supported（**仅** `thinking.type: "adaptive"`）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 **4,096** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html>

### 12. Claude Sonnet 4.6
- 基础 Model ID：`anthropic.claude-sonnet-4-6`
- 发布：2026-02-17 ｜ 上下文：1M ｜ 最大输出：64K ｜ 知识截止：Aug 2025
- 端点：runtime ✅、**mantle ❌**
- runtime API：Messages ❌ / Converse ✅ / Invoke ✅ ｜ mantle：—
- 跨区前缀：`us.` `eu.` `au.` `jp.`；global：`global.anthropic.claude-sonnet-4-6`
- Reasoning：Supported（**模型卡未给 thinking 模式/effort/budget 细则** → 具体 thinking 写法【待确认】）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 **1,024** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html>

### 13. Claude Opus 4.6
- 基础 Model ID：`anthropic.claude-opus-4-6-v1`（**注意 `-v1` 后缀**）
- 发布：2026-02-05 ｜ 上下文：1M ｜ 最大输出：128K ｜ 知识截止：【待确认】
- 端点：runtime ✅、**mantle ❌**
- runtime API：Converse ✅ / Invoke ✅（Messages 行见模型卡）
- 跨区前缀：`us.` `eu.` `au.`；global：`global.anthropic.claude-opus-4-6-v1`
- Reasoning：Supported（thinking 细则**未在模型卡写明** → 【待确认】）
- 采样参数：模型卡未单列 → 【待确认】
- Prompt 缓存：最小 **4,096** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-6.html>

### 14. Claude Opus 4.5
- 基础 Model ID：`anthropic.claude-opus-4-5-20251101-v1:0`（旧式日期 + `-v1:0`）
- 发布：2025-11-24 ｜ 上下文：200K ｜ 最大输出：64K
- 端点：runtime ✅、**mantle ❌**
- runtime API：Messages ❌ / Converse ✅ / Invoke ✅
- 跨区前缀：`us.` `eu.`；global：`global.anthropic.claude-opus-4-5-20251101-v1:0`
- Reasoning：Supported（thinking 细则/effort 首发**未在模型卡写明** → 【待确认】）
- Prompt 缓存：最小 **4,096** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-5.html>

### 15. Claude Haiku 4.5
- 基础 Model ID：runtime **N/A**（按需吞吐需 geo/global 推理档 ID）；mantle 裸 ID `anthropic.claude-haiku-4-5`
- 发布：2025-10-16 ｜ 上下文：200K ｜ 最大输出：64K
- 端点：runtime ✅（需推理档）、mantle ✅
- runtime API：Messages ✅ / Converse ✅ / Invoke ✅ ｜ mantle：Messages ✅
- 跨区前缀：`us.` `eu.` `au.` `jp.` `in.` + `20251001-v1:0`；global：`global.anthropic.claude-haiku-4-5-20251001-v1:0`
- Reasoning：Supported（thinking 细则**未在模型卡写明** → 【待确认】）
- Prompt 缓存：最小 **4,096** tokens
- 说明：单区推理（数据驻留）用 mantle 裸 ID；runtime 裸 ID 不支持按需吞吐
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html>

### 16. Claude Sonnet 4.5
- 基础 Model ID：`anthropic.claude-sonnet-4-5-20250929-v1:0`
- 发布：2025-09-30 ｜ 上下文：200K ｜ 最大输出：64K
- 端点：runtime ✅、**mantle ❌**
- runtime API：Converse ✅ / Invoke ✅（Messages 行见模型卡）
- 跨区前缀：`us.` `eu.` `au.` `jp.`；global：`global.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Reasoning：Supported（thinking 细则 **enabled+budget_tokens** 等**未在模型卡写明** → 【待确认】）
- Prompt 缓存：最小 **1,024** tokens
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-5.html>

### 17. Claude Opus 4.1
- 基础 Model ID：`anthropic.claude-opus-4-1-20250805-v1:0`
- 发布：2025-08-05 ｜ 上下文：200K ｜ 最大输出：32K
- 端点：runtime ✅、**mantle ❌**
- 跨区前缀：`us.`；global：N/A
- Reasoning：Supported（细则【待确认】）
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-1.html>

### 18. Claude Sonnet 4
- 基础 Model ID：`anthropic.claude-sonnet-4-20250514-v1:0`
- 发布：2025-05-23 ｜ 上下文：200K ｜ 最大输出：64K
- 端点：runtime ✅、**mantle ❌**
- 跨区前缀：`us.` `eu.` `apac.`；global：`global.anthropic.claude-sonnet-4-20250514-v1:0`
- Reasoning：Supported（extended thinking with tool use；细则【待确认】）
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4.html>

### 19. Claude 3 Haiku
- 基础 Model ID：`anthropic.claude-3-haiku-20240307-v1:0`
- 发布：2024-03-13 ｜ 上下文：200K ｜ 最大输出：4K
- 端点：runtime ✅
- In-Region URL：`https://bedrock-runtime.{region}.amazonaws.com`
- 跨区前缀：`us.` `eu.`；global：N/A
- Reasoning：模型卡未列（Claude 3 代无 extended thinking）
- 来源：<https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-3-haiku.html>

---

## 支持矩阵（速查）

| 模型 | 基础 Model ID | runtime | mantle | 发布 | 上下文/输出 | thinking 细则来源 |
|------|---------------|---------|--------|------|-------------|-------------------|
| Haiku 5.5 | `anthropic.claude-haiku-5-5` | ✅ | ✅ | 2026-10-07 | 1M/128K | 卡内明确 |
| Sonnet 5.5 | `anthropic.claude-sonnet-5-5` | ✅ | ✅ | 2026-09-28 | 1M/128K | 卡内明确 |
| Opus 5.5 | `anthropic.claude-opus-5-5` | ✅ | ✅ | 2026-09-22 | 1M/128K | 卡内明确 |
| Fable 5.1 | `anthropic.claude-fable-5-1` | ✅ | ✅ | 2026-09-01 | 1M/128K | 卡内明确 |
| Mythos 5.1 | `anthropic.claude-mythos-5-1` | ✅(gated) | 待确认 | 2026-09-01 | 1M/128K | 卡内明确 |
| Opus 5 | `anthropic.claude-opus-5` | ✅ | ✅ | 2026-07-24 | 1M/128K | 卡内明确 |
| Sonnet 5 | `anthropic.claude-sonnet-5` | ✅ | ✅ | 2026-06-30 | 1M/128K | 卡内明确 |
| Mythos 5 | `anthropic.claude-mythos-5` | ❌ | ✅ | 2026-06-09 | 1M/128K | 卡内明确 |
| Fable 5 | `anthropic.claude-fable-5` | ✅ | ✅ | 2026-06-09 | 1M/128K | 卡内明确 |
| Opus 4.8 | `anthropic.claude-opus-4-8` | ✅ | ✅ | 2026-05-28 | 1M/128K | adaptive only |
| Opus 4.7 | `anthropic.claude-opus-4-7` | ✅ | ✅ | 2026-04-16 | 1M/128K | adaptive only |
| Sonnet 4.6 | `anthropic.claude-sonnet-4-6` | ✅ | ❌ | 2026-02-17 | 1M/64K | 【待确认】 |
| Opus 4.6 | `anthropic.claude-opus-4-6-v1` | ✅ | ❌ | 2026-02-05 | 1M/128K | 【待确认】 |
| Opus 4.5 | `anthropic.claude-opus-4-5-20251101-v1:0` | ✅ | ❌ | 2025-11-24 | 200K/64K | 【待确认】 |
| Haiku 4.5 | runtime N/A（需推理档）/ mantle `anthropic.claude-haiku-4-5` | ✅ | ✅ | 2025-10-16 | 200K/64K | 【待确认】 |
| Sonnet 4.5 | `anthropic.claude-sonnet-4-5-20250929-v1:0` | ✅ | ❌ | 2025-09-30 | 200K/64K | 【待确认】 |
| Opus 4.1 | `anthropic.claude-opus-4-1-20250805-v1:0` | ✅ | ❌ | 2025-08-05 | 200K/32K | 【待确认】 |
| Sonnet 4 | `anthropic.claude-sonnet-4-20250514-v1:0` | ✅ | ❌ | 2025-05-23 | 200K/64K | 【待确认】 |
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | ✅ | ❌ | 2024-03-13 | 200K/4K | 无 |

## 对实施任务的建议（供 task-2/3/4 参考，非本任务交付范围）

- 示例应覆盖**当前真实模型**；仓库现有脚本名基本可复用（Fable 5 / Mythos 5 / Opus 4.8/4.7/4.6/4.5 /
  Sonnet 4.6 / Haiku 4.5 均仍真实存在），但应补充 5.5 家族与 5 代（Opus 5 / Sonnet 5）示例，
  或在 README 的模型总览中补齐这些新模型。
- Mantle 示例只演示 **Messages API**（`AnthropicBedrockMantle` + `messages.create`）；
  不要在 mantle 上演示 Converse/Invoke（卡内均为不支持）。
- Fable 5 数据保留 CLI 从 README 的 `provider_data_share` 改为 **`aws_review`**（仅 Mythos 用 `provider_data_share`）。
- 4.x 模型的 thinking 具体写法（budget_tokens vs adaptive+effort）**无法从模型卡核实**；
  实施/文档如需写明，须另找权威依据（如 Adaptive thinking 文档页或各模型 anthropic service card），
  否则保持【待确认】而非照抄仓库旧说法。

## 待确认 / 缺口清单

1. 多数模型卡的 **Sampling parameters** 段仅在 Fable/Mythos 系列出现；其余模型是否有采样限制未写明。→【待确认】
2. **4.x 系列（Sonnet 4.6 / Opus 4.6 / Opus 4.5 / Haiku 4.5 / Sonnet 4.5 / Opus 4.1 / Sonnet 4）thinking 模式细则**
   （adaptive / enabled+budget_tokens / effort）在模型卡 Model Details 中仅标 “Reasoning: Supported”。→【待确认】
3. **Mythos 5.1 的 bedrock-runtime API 行**（Messages/Converse/Invoke 具体支持）需复核；总览仅列端点支持。→【待确认】
4. 本清单基于 2026-10-14 抓取快照；AWS 页面会更新，后续任务应以实施当日抓取为准。
