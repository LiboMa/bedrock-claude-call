# Amazon Bedrock Anthropic Claude 模型调用指南

在 Amazon Bedrock 上调用 Anthropic Claude 全系列模型（Claude 5.5 家族 / Fable · Mythos 5.x / Opus · Sonnet 5 / Opus 4.x / Sonnet 4.x / Haiku 4.5 / 更早模型）的可运行示例与说明。

> 内容依据 AWS 官方 [Anthropic 模型卡总览](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-anthropic.html) 及各模型卡子页整理（抓取快照 **2026-10-14**，事实清单见 `.octopus/model-facts.md`）。AWS 页面会持续更新，以官方页面为准。
>
> 标注 **【待确认】** 的内容表示模型卡未写明、本仓库无法核实；对应示例只演示一种写法并在失败时打印错误，**不代表该写法已被官方确认**。

图文版使用说明（安装 / 认证 / 运行示例 / 测试 / Model ID 速查）：用浏览器打开 `docs/usage.html`。

姊妹仓库：[bedrock-openai-gpt](https://github.com/LiboMa/bedrock-openai-gpt)。

## 模型总览

总览页当前共列出 19 个 Anthropic 模型（按总览页顺序）：

| 模型 | 基础 Model ID | 发布 | 上下文 | 最大输出 | 备注 |
|------|----------|------|--------|----------|------|
| **Claude Haiku 5.5** | `anthropic.claude-haiku-5-5` | 2026-10-07 | 1M | 128K | 首个带 effort 的 Haiku；thinking 可关 |
| **Claude Sonnet 5.5** | `anthropic.claude-sonnet-5-5` | 2026-09-28 | 1M | 128K | |
| **Claude Opus 5.5** | `anthropic.claude-opus-5-5` | 2026-09-22 | 1M | 128K | thinking 始终开启 |
| **Claude Fable 5.1** | `anthropic.claude-fable-5-1` | 2026-09-01 | 1M | 128K | 需数据保留模式 `aws_review` |
| **Claude Mythos 5.1** | `anthropic.claude-mythos-5-1` | 2026-09-01 | 1M | 128K | **Preview，受限访问**；网络安全 / 生命科学双用途 |
| **Claude Opus 5** | `anthropic.claude-opus-5` | 2026-07-24 | 1M | 128K | thinking 默认开启 |
| **Claude Sonnet 5** | `anthropic.claude-sonnet-5` | 2026-06-30 | 1M | 128K | thinking 默认开启（含省略 `thinking`） |
| **Claude Mythos 5** | `anthropic.claude-mythos-5` | 2026-06-09 | 1M | 128K | **Preview**；仅 Mantle |
| **Claude Fable 5** | `anthropic.claude-fable-5` | 2026-06-09 | 1M | 128K | 需数据保留模式 `aws_review` |
| **Claude Opus 4.8** | `anthropic.claude-opus-4-8` | 2026-05-28 | 1M | 128K | 仅 adaptive thinking |
| **Claude Opus 4.7** | `anthropic.claude-opus-4-7` | 2026-04-16 | 1M | 128K | 仅 adaptive thinking |
| **Claude Sonnet 4.6** | `anthropic.claude-sonnet-4-6` | 2026-02-17 | 1M | 64K | 无 Mantle |
| **Claude Opus 4.6** | `anthropic.claude-opus-4-6-v1` | 2026-02-05 | 1M | 128K | 注意 `-v1` 后缀；无 Mantle |
| **Claude Opus 4.5** | `anthropic.claude-opus-4-5-20251101-v1:0` | 2025-11-24 | 200K | 64K | 旧式带日期 ID；无 Mantle |
| **Claude Haiku 4.5** | runtime：N/A（必须用推理档 ID）<br>mantle：`anthropic.claude-haiku-4-5` | 2025-10-16 | 200K | 64K | 单区推理走 Mantle 裸 ID |
| **Claude Sonnet 4.5** | `anthropic.claude-sonnet-4-5-20250929-v1:0` | 2025-09-30 | 200K | 64K | 旧式带日期 ID；无 Mantle |
| **Claude Opus 4.1** | `anthropic.claude-opus-4-1-20250805-v1:0` | 2025-08-05 | 200K | 32K | 无 `global.` 推理档 |
| **Claude Sonnet 4** | `anthropic.claude-sonnet-4-20250514-v1:0` | 2025-05-23 | 200K | 64K | 支持 `apac.` 推理档 |
| **Claude 3 Haiku** | `anthropic.claude-3-haiku-20240307-v1:0` | 2024-03-13 | 200K | 4K | 有 In-Region；无 extended thinking |

> 生命周期 / EOL 日期不在本仓库已核实的事实范围内【待确认】，规划迁移前请查看各模型卡。

## 两种端点、三种 API

| | bedrock-runtime（经典） | bedrock-mantle（新） |
|---|---|---|
| API | Converse / InvokeModel / Anthropic Messages（视模型而定） | **仅** Anthropic Messages API |
| SDK | `boto3`（Converse / Invoke）；`anthropic`（Messages，`base_url=.../anthropic`） | `anthropic[bedrock]`（`AnthropicBedrockMantle`） |
| 认证（示例写法） | SigV4 或 Bedrock API Key（`AWS_BEARER_TOKEN_BEDROCK`）；Messages 示例用 `aws-bedrock-token-generator` 生成短期 API Key | SigV4 或 Bedrock API Key |
| URL | `https://bedrock-runtime.{region}.amazonaws.com` | `https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages` |
| Model ID | 推理档 ID（`us.` / `global.` 等前缀） | 裸 ID（不带任何前缀） |

各模型支持矩阵（以各模型卡 “Endpoints and APIs supported” 表为准）：

| 模型 | runtime Converse | runtime Invoke | runtime Messages | Mantle Messages |
|------|:---:|:---:|:---:|:---:|
| Haiku 5.5 / Sonnet 5.5 / Opus 5.5 | ✅ | ✅ | ✅ | ✅ |
| Fable 5.1 | ✅ | ✅ | ✅ | ✅ |
| Mythos 5.1 | 【待确认】 | 【待确认】 | 【待确认】 | 未列出 |
| Opus 5 / Sonnet 5 | 列出¹ | 列出¹ | 列出¹ | ✅ |
| Mythos 5 | ❌ | ❌ | ❌ | ✅（**唯一通道**） |
| Fable 5 | ✅ | ✅ | ✅ | ✅ |
| Opus 4.8 | ✅ | ✅ | ✅ | ✅ |
| Opus 4.7 | 列出¹ | 列出¹ | 列出¹ | ✅ |
| Sonnet 4.6 / Opus 4.5 | ✅ | ✅ | ❌ | ❌ |
| Opus 4.6 / Sonnet 4.5 | ✅ | ✅ | 【待确认】 | ❌ |
| Haiku 4.5 | ✅ | ✅ | ✅ | ✅（裸 ID `anthropic.claude-haiku-4-5`） |
| Opus 4.1 / Sonnet 4 / Claude 3 Haiku | 【待确认】² | 【待确认】 | 【待确认】 | ❌ |

> ¹ 事实清单记录这些模型在 bedrock-runtime 上列有 Messages / Converse / Invoke，但未逐行确认 ✅，以模型卡为准。
> ² 这三个模型仅确认 bedrock-runtime 端点可用，API 行未记录；`legacy_models_converse.py` 用 Converse 演示，失败只报告。
>
> Claude 在 Mantle 的路径是 `anthropic/v1/messages`；Mantle 上 Converse / Invoke 均不支持。
> Mythos 两代通道不同：**Mythos 5 仅 Mantle**；**Mythos 5.1 模型卡端点支持只列 bedrock-runtime**，其 runtime 上具体支持哪些 API 【待确认】。

## Model ID 规则（重要）

三种命名风格并存，写错 ID 是最常见的报错来源：

1. **干净无日期 ID**（5.5 家族、Fable / Mythos 5.x、Opus / Sonnet 5、Opus 4.7 / 4.8、Sonnet 4.6）：`anthropic.claude-opus-5-5`、`anthropic.claude-fable-5-1`、`anthropic.claude-opus-4-8`、`anthropic.claude-sonnet-4-6`
2. **Opus 4.6**：带 `-v1` 后缀 — `anthropic.claude-opus-4-6-v1`
3. **Opus 4.5 及更早**：带日期 + `-v1:0` 后缀 — `anthropic.claude-opus-4-5-20251101-v1:0`、`anthropic.claude-sonnet-4-5-20250929-v1:0`

> Haiku 4.5 特例：runtime 裸 ID 不支持按需吞吐，必须用带日期的推理档 ID（`us.anthropic.claude-haiku-4-5-20251001-v1:0`）；Mantle 裸 ID 不带日期（`anthropic.claude-haiku-4-5`）。

### 跨区推理前缀（仅 bedrock-runtime）

在基础 ID 前加推理档前缀。本仓库示例在 bedrock-runtime 上统一使用推理档 ID；Claude 3 Haiku 模型卡另列 In-Region URL。

| 前缀 | 含义 | 示例 |
|------|------|------|
| `us.` / `eu.` / `au.` / `jp.` / `in.` / `apac.` / `us-gov.` | Geo 地理围栏 | `us.anthropic.claude-opus-5-5` |
| `global.` | 全球路由 | `global.anthropic.claude-opus-5-5` |
| 无 | In-Region（Claude 3 Haiku） | `anthropic.claude-3-haiku-20240307-v1:0` |

各模型可用前缀（摘自模型卡 Programmatic Access 表）：

| 模型 | Geo 前缀 | `global.` |
|------|----------|:---:|
| Haiku 5.5 / Opus 5.5 | `us.` `eu.` `au.` `jp.` | ✅ |
| Sonnet 5.5 | `us.` `eu.` `au.` | ✅ |
| Fable 5.1 / Mythos 5.1 / Fable 5 | `us.` | ✅ |
| Opus 5 / Sonnet 5 | `us.` `eu.` `au.` `in.` | ✅ |
| Mythos 5 | —（仅 Mantle 裸 ID） | — |
| Opus 4.8 | `us.` `eu.` `jp.` `au.` `us-gov.` | ✅ |
| Opus 4.7 / Sonnet 4.6 / Sonnet 4.5 | `us.` `eu.` `jp.` `au.` | ✅ |
| Opus 4.6 | `us.` `eu.` `au.` | ✅ |
| Opus 4.5 | `us.` `eu.` | ✅ |
| Haiku 4.5 | `us.` `eu.` `au.` `jp.` `in.` | ✅ |
| Opus 4.1 | `us.` | ❌ |
| Sonnet 4 | `us.` `eu.` `apac.` | ✅ |
| Claude 3 Haiku | `us.` `eu.`（另有 In-Region） | ❌ |

日常推荐：美国账号用 `us.` 前缀；无数据驻留要求用 `global.`；Mantle 一律用裸 ID。

## 快速开始

### 1. 安装

```bash
pip install -r requirements.txt   # boto3 + anthropic[bedrock] + aws-bedrock-token-generator
# 或 ./setup.sh
```

### 2. 认证（二选一）

```bash
# 方式 A：Bedrock API Key（控制台 → API Keys → 创建长期 Key）
export AWS_BEARER_TOKEN_BEDROCK="<你的 Bedrock API Key>"

# 方式 B：标准 AWS 凭证链（~/.aws/credentials），无需任何配置
```

bedrock-runtime 上的 Messages API 示例使用 API Key：用 `aws_bedrock_token_generator.provide_token()` 从凭证链生成短期 Key。

### 3. 数据保留模式一次性设置（按 Region）

以下模型的模型卡要求账号设置指定的数据保留模式：

| 模型 | 需要的模式 | 命令 |
|------|-----------|------|
| Fable 5 / Fable 5.1 | `aws_review` | `aws bedrock put-account-data-retention --mode aws_review` |
| Mythos 5 / Mythos 5.1 | `provider_data_share` | `aws bedrock put-account-data-retention --mode provider_data_share` |

注意 Fable 5 需要的是 `aws_review`，**不是** `provider_data_share`；`provider_data_share` 仅适用于 Mythos 5 / 5.1。Mythos 5.1 还需通过 Anthropic trusted access 获得访问资格（面向经审核的组织）。

### 4. 最小可运行示例

**Converse API（bedrock-runtime）：**

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")
response = client.converse(
    modelId="us.anthropic.claude-sonnet-5-5",
    messages=[{"role": "user", "content": [{"text": "介绍一下 Amazon Bedrock。"}]}],
    inferenceConfig={"maxTokens": 2048},
)
for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])
```

**Messages API on bedrock-runtime（Anthropic SDK，见 `fable51_messages_runtime.py`）：**

```python
from anthropic import Anthropic
from aws_bedrock_token_generator import provide_token

REGION = "us-east-1"
client = Anthropic(
    base_url=f"https://bedrock-runtime.{REGION}.amazonaws.com/anthropic",
    api_key=provide_token(region=REGION),
)
message = client.messages.create(
    model="global.anthropic.claude-fable-5-1",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
```

**Mantle + Anthropic SDK（裸 ID）：**

```python
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")
message = client.messages.create(
    model="anthropic.claude-opus-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
for block in message.content:
    if block.type == "text":
        print(block.text)
```

## 推理（Thinking）控制

这是各代模型差异最大的地方。下表只写各模型卡 Reasoning 字段明确给出的规则，其余标【待确认】：

| 模型 | thinking 模式 | 能否关闭（`disabled`） | effort 取值（默认） |
|------|--------------|:---:|------|
| Haiku 5.5 | adaptive，默认开启 | ✅（关闭时 effort 上限 high） | low/medium/high/xhigh/max（**medium**） |
| Sonnet 5.5 | adaptive，默认开启 | 【待确认】 | low/medium/high/xhigh/max（**high**） |
| Opus 5.5 | adaptive，**始终开启** | ❌ 不可关 | low/medium/high/xhigh/max（**medium**） |
| Fable 5.1 / Mythos 5.1 | adaptive，**始终开启** | ❌ 不可关 | low/medium/high/xhigh/max（**high**） |
| Opus 5 | adaptive，默认开启 | ✅（关闭时 effort 上限 high） | 可配置；取值与默认【待确认】 |
| Sonnet 5 | adaptive，默认开启（**含省略 `thinking` 的请求**） | ✅ `{"type": "disabled"}` | 可配置；取值与默认【待确认】 |
| Fable 5 / Mythos 5 | adaptive，**始终开启** | ❌ 不可关 | 可配置；取值与默认【待确认】 |
| Opus 4.8 / 4.7 | **仅** `thinking.type: "adaptive"` | 【待确认】 | 【待确认】 |
| Sonnet 4.6 / Opus 4.6 / Opus 4.5 / Haiku 4.5 / Sonnet 4.5 / Opus 4.1 | 模型卡仅写 “Reasoning: Supported”；具体写法（adaptive / enabled+budget_tokens / effort）【待确认】 | 【待确认】 | 【待确认】 |
| Sonnet 4 | “Reasoning: Supported”（extended thinking with tool use）；具体写法【待确认】 | 【待确认】 | 【待确认】 |
| Claude 3 Haiku | 模型卡未列 Reasoning（无 extended thinking） | — | — |

要点：

- **省略 `thinking` 不等于关闭**：Haiku 5.5 / Sonnet 5.5 / Opus 5 / Sonnet 5 默认开启 adaptive thinking，thinking token 计入 `max_tokens`，请预留足够额度；要关闭需显式传 `{"type": "disabled"}`（仅限上表标 ✅ 的模型）。
- **Opus 5 / Haiku 5.5 关闭 thinking 时 effort 上限为 high**：`xhigh` / `max` 只能在 thinking 开启时使用。
- `enabled` + `budget_tokens` 写法：上述模型卡**均未写明**哪些模型接受或拒绝【待确认】。本仓库只在 `opus45_converse.py` / `sonnet45_extended_thinking.py` 中把它作为**未经核实**的写法演示，新代模型示例不传。
- 示例统一把 `effort` 放在独立的 `output_config` 对象中（不放进 `thinking`）。

**新代模型（adaptive + effort），Converse API 写法：**

```python
response = client.converse(
    modelId="us.anthropic.claude-opus-5-5",
    messages=[{"role": "user", "content": [{"text": "什么是 2+2？"}]}],
    additionalModelRequestFields={
        "thinking": {"type": "adaptive"},     # Opus 5.5 / Fable / Mythos 5.x 始终开启，可省略
        "output_config": {"effort": "low"},
    },
)
```

**4.x 模型（thinking 写法【待确认】）：** 本仓库示例各演示一种写法，失败时打印错误而不抛出：

```python
# opus45_converse.py / sonnet45_extended_thinking.py（未经核实）
additionalModelRequestFields={"thinking": {"type": "enabled", "budget_tokens": 2048}}

# sonnet46_adaptive.py（未经核实；effort 为示例值，取值/默认【待确认】）
additionalModelRequestFields={"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}}

# opus46_47_converse.py 中的 Opus 4.6（未经核实）
additionalModelRequestFields={"thinking": {"type": "adaptive"}}

# Opus 4.7 / 4.8：模型卡写明仅 adaptive
additionalModelRequestFields={"thinking": {"type": "adaptive"}}
```

## 采样参数

| 模型 | temperature / top_p / top_k |
|------|------------------------------|
| Fable 5.1 / Mythos 5.1 | temperature 必须 1.0 或不传；top_p 必须 0.99 或不传；**两者不可同传**；top_k 不支持 |
| Fable 5 / Mythos 5 | temperature 必须 1.0 或不传；top_p ≥ 0.99 且 < 1.0 或不传；top_k 不支持 |
| 其他所有模型（含 Opus 4.7 / 4.8） | 模型卡未单列 Sampling parameters 段，是否有限制【待确认】 |

**建议：一律不传采样参数，用 prompt 控制行为。** 本仓库所有示例都不传 temperature / top_p / top_k（`legacy_models_converse.py` 也只传 `maxTokens`）。

## Fable / Mythos 系列特别注意

1. **refusal 是常规返回路径**：内置网络安全 / 生命科学双用途分类器，命中时返回 `stop_reason: "refusal"`，代码必须显式处理（见 `fable5_invoke_model.py`、`fable51_messages_runtime.py`；示例会打印返回的 `stop_details`）。总览页 Billing notes（针对 bedrock-mantle 上的 Anthropic 模型）：推理开始前被拒不计费；流式开始后中途拒绝按已消耗 token 计费。
2. **流式优先**：128K 输出 + 始终思考，长任务建议用 `converse_stream` / SDK `messages.stream`，避免超时。
3. **访问门槛**：Fable 5 / 5.1 需 `aws_review` 数据保留；Mythos 5 / 5.1 需 `provider_data_share`，且为 Preview / Beta Service；Mythos 5.1 访问受限（Anthropic trusted access）。

## Prompt 缓存

所有列出的模型均支持显式 Prompt 缓存：每请求最多 **4** 个检查点，TTL 为 **5 分钟 / 1 小时**，作用字段为 system / messages / tools。各模型最小检查点 token 数：

| 模型 | 最小检查点 |
|------|-----------|
| Haiku 5.5 / Sonnet 5.5 / Opus 5.5、Fable 5.1 / Mythos 5.1、Opus 5、Fable 5 / Mythos 5 | **512** tokens |
| Sonnet 5、Opus 4.8、Sonnet 4.6、Sonnet 4.5 | 1,024 tokens |
| Opus 4.7、Opus 4.6、Opus 4.5、Haiku 4.5 | 4,096 tokens |
| Opus 4.1、Sonnet 4、Claude 3 Haiku | 事实清单未记录【待确认】 |

## 示例文件

| 文件 | 模型 | 内容 |
|------|------|------|
| `claude55_family.py` | Haiku 5.5 / Sonnet 5.5 / Opus 5.5 | Converse；默认 adaptive、Haiku 关闭 thinking（effort high）、Sonnet xhigh、Opus max effort |
| `fable51_messages_runtime.py` | Fable 5.1 | bedrock-runtime 上的 Messages API（`Anthropic` + `provide_token`）流式 + refusal 处理 |
| `mythos51_converse.py` | Mythos 5.1 | 仅演示 Converse（runtime API 行【待确认】，受限访问，失败只报告） |
| `opus5_sonnet5_converse.py` | Opus 5 / Sonnet 5 | 省略 thinking 即开启 adaptive、显式 disabled、Opus 5 关闭时 effort high；Sonnet 5 的 effort low 为示例值（取值/默认【待确认】） |
| `fable5_converse.py` | Fable 5 | Converse 基础调用 |
| `fable5_effort.py` | Fable 5 | adaptive thinking（始终开启）+ effort（所传 effort 为示例值，取值/默认【待确认】） |
| `fable5_streaming.py` | Fable 5 | ConverseStream 流式 |
| `fable5_tool_calling.py` | Fable 5 | 工具调用 + 完整 agentic loop |
| `fable5_invoke_model.py` | Fable 5 | InvokeModel 原生请求体 + refusal 处理（effort 为示例值，【待确认】） |
| `fable5_mantle.py` | Fable 5 | Mantle 端点 + Anthropic SDK 流式（effort 为示例值，【待确认】） |
| `mythos5_mantle.py` | Mythos 5 | 仅 Mantle 通道（Preview；effort 为示例值，【待确认】） |
| `opus48_all_apis.py` | Opus 4.8 | Converse / Invoke / runtime Messages / Mantle Messages 四路对照（adaptive，不传采样参数） |
| `opus46_47_converse.py` | Opus 4.6 + 4.7 | Opus 4.6（thinking 写法未经核实）与 Opus 4.7（仅 adaptive）对照 |
| `opus45_converse.py` | Opus 4.5 | 旧式日期 ID + enabled / budget_tokens（未经核实的写法） |
| `sonnet46_adaptive.py` | Sonnet 4.6 | adaptive + effort（未经核实的写法） |
| `sonnet45_extended_thinking.py` | Sonnet 4.5 | enabled / budget_tokens（未经核实的写法） |
| `haiku45_converse.py` | Haiku 4.5 | 快速分类场景（runtime 推理档 ID，不传 thinking） |
| `legacy_models_converse.py` | Opus 4.1 / Sonnet 4 / Claude 3 Haiku | 更早模型 Converse 基础调用（仅 `maxTokens`，失败只报告不中断） |
| `test_all.py` | 全部 | 18 个脚本语法检查 + 27 项实测（覆盖全部 19 个模型） |

```bash
python test_all.py               # 语法 + 全模型实测（需 AWS 凭证与模型访问）
python test_all.py --syntax-only # 仅语法检查（不联网）
```

`test_all.py` 中，受限模型（Mythos 5 / 5.1；Mythos 5.1 的 runtime API 行也【待确认】）和更早模型（Opus 4.1、Sonnet 4、Claude 3 Haiku，生命周期【待确认】）调用失败记为 SKIP，不会让整体失败；其他模型若因账号访问条件失败（模型 / 路由未在该账号或 Region 开通、IAM 缺少对应 `bedrock:` 权限、AccessDenied）也记为 SKIP，其余错误记为 FAIL，但不中断后续测试。实测统一使用 `max_tokens=1024`，为默认开启的 thinking 留出额度；4.x（Opus 4.6 / 4.5、Sonnet 4.x、Haiku 4.5）实测不传 thinking；effort 只对模型卡写明取值的 5.5 家族传 `low`，Fable 5 与 Opus 4.7 的 adaptive 探测不传 effort。

## 模型怎么选？

- **新项目**：优先考虑最新的 5.5 家族（Haiku / Sonnet / Opus 5.5，1M 上下文、128K 输出、effort 全档 low–max）
- **大批量 / 低延迟**：Haiku 5.5（可关闭 thinking）；需要 4.x 时用 Haiku 4.5
- **需要 Mantle 单区推理**：选 Mantle 列为 ✅ 的模型（见支持矩阵），Haiku 4.5 用裸 ID `anthropic.claude-haiku-4-5`
- **安全研究 / 生命科学**（已获访问资格）：Mythos 5.1（bedrock-runtime）或 Mythos 5（Mantle）
- **存量兼容**：Opus 5 / Sonnet 5、Fable 5、Opus 4.x、Sonnet 4.x、Haiku 4.5 及更早模型仍在总览页列出；生命周期请以模型卡为准【待确认】

## 常见问题

**Q: 报 `ValidationException: ... model identifier is invalid`？**
A: 检查 ID 代次规则：4.5 及更早要完整日期 + `-v1:0`；Opus 4.6 要 `-v1`；Opus 4.7+ 和 5 代用干净 ID。bedrock-runtime 上加 `us.` / `global.` 等推理档前缀（Haiku 4.5 裸 ID 不支持按需吞吐）；Mantle 则必须用裸 ID。

**Q: thinking 参数被拒（400 / `ValidationException`）？**
A: Opus 4.7 / 4.8 模型卡写明只支持 `{"type": "adaptive"}`；Opus 5.5、Fable / Mythos 5.x 的 thinking 始终开启、不可关，不要传 `disabled`。4.x 其他模型的 thinking 写法【待确认】，可先不传 `thinking`。

**Q: 从 Sonnet 4.6 迁到 Sonnet 5 后，输出 token 和费用变多？**
A: Sonnet 5 省略 `thinking` 也会开启 adaptive thinking（Opus 5 同样默认开启）。显式传 `{"type": "disabled"}`，或调低 `output_config.effort`，并重新评估 `max_tokens`。

**Q: Opus 5 / Haiku 5.5 关闭 thinking 后 effort 报错？**
A: 关闭 thinking 时 effort 上限为 `high`；要用 `xhigh` / `max` 就保持 adaptive（或省略 `thinking`）。

**Q: Fable 返回了 `stop_reason: "refusal"`？**
A: 这是双用途内容分类器拦截，按正常分支处理并查看返回的 `stop_details`。

**Q: 调 Fable 5 / 5.1 报数据保留相关错误？**
A: 执行 `aws bedrock put-account-data-retention --mode aws_review`（每个 Region 一次）。Mythos 需 `--mode provider_data_share`。

**Q: Mythos 5.1 用 Mantle 调不通？**
A: Mythos 5.1 模型卡端点支持只列 bedrock-runtime（没有 Mantle），请用 `us.` / `global.` 推理档 ID；runtime 上具体支持哪些 API【待确认】，且访问受限。Mythos 5 则相反，只能走 Mantle 裸 ID。

**Q: 能用 OpenAI SDK 调 Claude 吗？**
A: 本仓库的 Claude 示例走 Anthropic Messages API（runtime 的 `/anthropic` 或 Mantle 的 `anthropic/v1/messages`），使用 `anthropic` SDK；Converse / Invoke 使用 `boto3`。

## 参考链接

- [Anthropic 模型卡总览](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-anthropic.html)
- Claude 5.5：[Haiku 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html) / [Sonnet 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5-5.html) / [Opus 5.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5-5.html)
- Fable / Mythos：[Fable 5.1](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5-1.html) / [Fable 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html) / [Mythos 5.1](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5-1.html) / [Mythos 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5.html)
- Claude 5：[Opus 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html) / [Sonnet 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html)
- Opus 4.x：[4.8](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-8.html) / [4.7](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html) / [4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-6.html) / [4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-5.html) / [4.1](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-1.html)
- Sonnet 4.x：[4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html) / [4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-5.html) / [4](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4.html)
- Haiku：[Haiku 4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html) / [Claude 3 Haiku](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-3-haiku.html)
- [Adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html) / [Extended thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-extended-thinking.html)
- [Prompt 缓存](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)
- [数据保留](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html) / [滥用检测](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html)
- [Bedrock API Key 管理](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)
- [区域可用性](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html)
- [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)
