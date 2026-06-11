# Amazon Bedrock Anthropic Claude 模型调用指南

在 Amazon Bedrock 上调用 Anthropic Claude 全系列模型（Claude 5 / Opus 4.x / Sonnet 4.x / Haiku 4.5）的可运行示例与说明。

姊妹仓库：[bedrock-openai-gpt](https://github.com/LiboMa/bedrock-openai-gpt)（GPT-5.5 / GPT-5.4 on Bedrock）。

## 模型总览

| 模型 | 基础 Model ID | 发布 | 上下文 | 最大输出 | 定位 |
|------|----------|------|--------|----------|------|
| **Claude Fable 5** | `anthropic.claude-fable-5` | 2026-06 | 1M | 128K | 新一代旗舰：多天自主任务、子代理编排、自我校验 |
| **Claude Mythos 5** | `anthropic.claude-mythos-5` | 2026-06 | 1M | 128K | 网络安全/生命科学专家模型；**Preview，白名单制** |
| **Claude Opus 4.8** | `anthropic.claude-opus-4-8` | 2026-05 | 1M | 128K | 生产编码与代理工作流默认选择 |
| **Claude Opus 4.7** | `anthropic.claude-opus-4-7` | 2026-04 | 1M | 128K | 编码与长程代理 |
| **Claude Opus 4.6** | `anthropic.claude-opus-4-6-v1` | 2026-02 | 1M | 128K | 注意 `-v1` 后缀 |
| **Claude Opus 4.5** | `anthropic.claude-opus-4-5-20251101-v1:0` | 2025-11 | 200K | 64K | 旧式带日期 ID；effort 参数首发 |
| **Claude Sonnet 4.6** | `anthropic.claude-sonnet-4-6` | 2026-02 | 1M | 64K | 中端主力，性价比 |
| **Claude Sonnet 4.5** | `anthropic.claude-sonnet-4-5-20250929-v1:0` | 2025-09 | 200K | 64K | 旧式 thinking（budget_tokens） |
| **Claude Haiku 4.5** | `anthropic.claude-haiku-4-5-20251001-v1:0` | 2025-10 | 200K | 64K | 低延迟低成本：分类/路由/子代理 |

## 两种端点、三种 API

| | bedrock-runtime（经典） | bedrock-mantle（新） |
|---|---|---|
| API | InvokeModel / Converse | Anthropic Messages API（与官方 API 同构） |
| SDK | `boto3` | `anthropic[bedrock]`（`AnthropicBedrockMantle`） |
| 认证 | SigV4 或 Bedrock API Key（`AWS_BEARER_TOKEN_BEDROCK`） | 同左 |
| URL | `https://bedrock-runtime.{region}.amazonaws.com` | `https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages` |

各模型支持矩阵：

| 模型 | Invoke | Converse | Messages (Mantle) |
|------|--------|----------|-------------------|
| Fable 5 | ✅ | ✅ | ✅ |
| Mythos 5 | ❌ | ❌ | ✅（唯一通道） |
| Opus 4.8 / 4.7 | ✅ | ✅ | ✅ |
| Opus 4.6 / 4.5、Sonnet 4.x、Haiku 4.5 | ✅ | ✅ | ❌（4.6 代以前未接入 Mantle*） |

> \* Haiku 4.5 在 Mantle 上有别名 `anthropic.claude-haiku-4-5` 可用。Claude 系列在 Mantle 的路径是 `anthropic/v1/messages`（GPT 系列是 `openai/v1`）；Mantle 用裸模型 ID，不带 `us.`/`global.` 前缀。

## Model ID 规则（重要）

三代命名风格并存，写错 ID 是最常见的报错来源：

1. **Claude 5 代与 Opus 4.7+/Sonnet 4.6**：干净无日期 ID — `anthropic.claude-fable-5`、`anthropic.claude-opus-4-8`、`anthropic.claude-sonnet-4-6`
2. **Opus 4.6**：带 `-v1` 后缀 — `anthropic.claude-opus-4-6-v1`
3. **Opus 4.5 / Sonnet 4.5 / Haiku 4.5**：带日期 + `-v1:0` 后缀 — `anthropic.claude-opus-4-5-20251101-v1:0`

跨区推理（仅 bedrock-runtime）在基础 ID 前加前缀：

| 前缀 | 含义 | 示例 |
|------|------|------|
| 无 | In-Region（部分区域才有） | `anthropic.claude-fable-5` |
| `us.` / `eu.` / `jp.` / `au.` | Geo 地理围栏（数据不出该地理区） | `us.anthropic.claude-fable-5` |
| `global.` | 全球路由，吞吐最大 | `global.anthropic.claude-fable-5` |

日常推荐：美国账号用 `us.` 前缀；无数据驻留要求用 `global.`。

## 快速开始

### 1. 安装

```bash
pip install -r requirements.txt   # boto3 + anthropic[bedrock]
```

### 2. 认证（二选一）

```bash
# 方式 A：Bedrock API Key（控制台 → API Keys → 创建长期 Key）
export AWS_BEARER_TOKEN_BEDROCK="<你的 Bedrock API Key>"

# 方式 B：标准 AWS 凭证链（~/.aws/credentials），无需任何配置
```

### 3. Claude 5 代一次性开通（Fable 5 / Mythos 5 必须）

```bash
aws bedrock put-account-data-retention --mode provider_data_share
```

背景：这两个模型的输入输出会保留最多 30 天用于滥用检测，且 Anthropic 要求共享被标记流量。launch 阶段无控制台 UI，只能走 CLI/API。Mythos 5 还需联系 AWS 客户团队申请白名单。

### 4. 最小可运行示例

**Converse API（任何模型通用）：**

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")
response = client.converse(
    modelId="us.anthropic.claude-fable-5",
    messages=[{"role": "user", "content": [{"text": "介绍一下 Amazon Bedrock。"}]}],
    inferenceConfig={"maxTokens": 2048},
)
print(response["output"]["message"]["content"][0]["text"])
```

**Mantle + Anthropic SDK（Fable 5 / Mythos 5 / Opus 4.7+）：**

```python
from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")
message = client.messages.create(
    model="anthropic.claude-fable-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content[0].text)
```

## 推理（Thinking）控制：三代模型三种玩法

这是各代模型差异最大的地方，**用错直接 400**：

| 模型 | thinking 模式 | budget_tokens | effort |
|------|--------------|---------------|--------|
| Fable 5 / Mythos 5 | adaptive **始终开启，不可关** | ❌ 传了报 400 | low/medium/high/max |
| Opus 4.8 / 4.7 | **仅** adaptive | ❌ 传了报 400 | low/medium/high/**xhigh**/max |
| Opus 4.6 / Sonnet 4.6 | adaptive（推荐）；enabled 已废弃 | ⚠️ 可用但勿新写 | low/medium/high/max（max 仅 Opus） |
| Opus 4.5 | enabled + budget_tokens | ✅ | ✅（首发支持） |
| Sonnet 4.5 / Haiku 4.5 | enabled + budget_tokens | ✅（≥1024 且 < max_tokens） | ❌ |

**新代模型（adaptive + effort），Converse API 写法：**

```python
response = client.converse(
    modelId="us.anthropic.claude-fable-5",
    messages=[{"role": "user", "content": [{"text": "什么是 2+2？"}]}],
    additionalModelRequestFields={
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "low"},   # effort 必须放 output_config！
    },
)
```

> ⚠️ 两个高频坑：
> ① `effort` 放进 `thinking` 对象 → `ValidationException`，必须放独立的 `output_config`；
> ② 对 Opus 4.7+/Fable 5 传 `budget_tokens` 或 `thinking: {"type": "disabled"}` → 400。

**旧代模型（Sonnet 4.5 / Haiku 4.5），extended thinking 写法：**

```python
additionalModelRequestFields={
    "thinking": {"type": "enabled", "budget_tokens": 4096},
}
```

## 采样参数变迁

| 模型 | temperature / top_p / top_k |
|------|------------------------------|
| Opus 4.5、Sonnet 4.5、Haiku 4.5 | 正常支持 |
| Opus 4.6 / Sonnet 4.6 | 支持（与 thinking 互斥规则同官方 API） |
| Opus 4.7 / 4.8 | **全部移除**，传了报 400 |
| Fable 5 / Mythos 5 | temperature 必须 1.0 或不传；top_p ≥0.99 且 <1.0 或不传；top_k 不支持 |

**最稳做法：一律不传采样参数，用 prompt 控制行为。**

## Fable 5 / Mythos 5 特别注意

1. **refusal 是常规返回路径**：内置网络安全/生物双用途分类器，命中时 HTTP 仍为 200，但 `stop_reason: "refusal"` 并附 `stop_details`。拒答率显著高于旧模型，代码必须显式处理（见 `fable5_invoke_model.py`）。推理前拦截不计费；流中拦截按已生成 token 计费。
2. **思考文本默认省略**：thinking 块默认只有签名没有正文；多轮对话/工具调用时**原样回传**即可。
3. **连接文本汇总（Fable 5）**：工具调用之间的过场叙述被服务端汇总为 thinking 块（不再是 text 块），最终答案不受影响。
4. **流式优先**：128K 输出 + 始终思考，长任务一律用 `converse_stream` / SDK `messages.stream`，避免超时。

## Prompt 缓存

| 模型 | 最小检查点 | 检查点上限 | TTL |
|------|-----------|------------|-----|
| Fable 5 / Mythos 5 | 1,024 tokens | 4 | 5 分钟 / 1 小时 |
| Opus 4.6–4.8 | 4,096 tokens | 4 | 5 分钟 / 1 小时 |

作用字段均为 system / messages / tools。

## 示例文件

| 文件 | 模型 | 内容 |
|------|------|------|
| `fable5_converse.py` | Fable 5 | Converse 基础调用 |
| `fable5_effort.py` | Fable 5 | adaptive thinking + effort |
| `fable5_streaming.py` | Fable 5 | ConverseStream 流式 |
| `fable5_tool_calling.py` | Fable 5 | 工具调用 + 完整 agentic loop |
| `fable5_invoke_model.py` | Fable 5 | InvokeModel 原生请求体 + refusal 处理 |
| `fable5_mantle.py` | Fable 5 | Mantle 端点 + Anthropic SDK 流式 |
| `mythos5_mantle.py` | Mythos 5 | 仅 Mantle 通道（白名单制） |
| `opus48_all_apis.py` | Opus 4.8 | Converse / Invoke / Mantle 三路对照 |
| `opus46_47_converse.py` | Opus 4.6+4.7 | 两代对照（4.7 xhigh effort） |
| `opus45_converse.py` | Opus 4.5 | 旧式日期 ID + effort 首发 |
| `sonnet46_adaptive.py` | Sonnet 4.6 | adaptive + effort（无 max） |
| `sonnet45_extended_thinking.py` | Sonnet 4.5 | 旧式 budget_tokens thinking |
| `haiku45_converse.py` | Haiku 4.5 | 快速分类场景 |
| `test_all.py` | 全部 | 语法检查 + 13 项实测 |

```bash
python test_all.py               # 语法 + 全模型实测
python test_all.py --syntax-only # 仅语法检查
```

## 模型怎么选？

- **要最强**：Fable 5（长程自主代理、超大代码库、多阶段任务）
- **日常生产编码/代理**：Opus 4.8（`effort: "xhigh"` 是甜点位）
- **性价比主力**：Sonnet 4.6（1M 上下文的中端）
- **大批量/低延迟**：Haiku 4.5（分类、路由、子代理）
- **安全研究/生科**（已获白名单）：Mythos 5
- **存量兼容**：Opus 4.5–4.7 / Sonnet 4.5；新项目不建议起步

## 常见问题

**Q: 报 `ValidationException: ... model identifier is invalid`？**
A: 检查 ID 代次规则——4.5 代要完整日期 + `-v1:0`；Opus 4.6 要 `-v1`；4.7+ 用干净 ID。In-region ID 在没有该模型 in-region 部署的区域不可用，换 `us.`/`global.` 前缀。

**Q: 报 400 `thinking.type: enabled is not supported`？**
A: 你在对 Opus 4.7+/Fable 5 用旧式 budget_tokens。改 `{"type": "adaptive"}` + `output_config.effort`。

**Q: Fable 5 返回了 `stop_reason: "refusal"`？**
A: 这不是错误（HTTP 200），是双用途内容分类器拦截，按正常分支处理并查看 `stop_details`。

**Q: 调 Fable 5 报数据保留相关错误？**
A: 执行 `aws bedrock put-account-data-retention --mode provider_data_share`（一次性）。

**Q: 能用 OpenAI SDK 调 Claude 吗？**
A: 不能。Claude 在 Mantle 上走 Anthropic Messages API（`anthropic/v1/messages`），用 `anthropic` SDK；GPT 系列才走 `openai/v1`。

## 参考链接

- [Claude Fable 5 模型卡](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html)
- [Claude Mythos 5 模型卡](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5.html)
- [Claude Opus 4.8](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-8.html) / [4.7](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html) / [4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-6.html) / [4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-5.html)
- [Claude Sonnet 4.6](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html) / [4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-5.html)
- [Claude Haiku 4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html)
- [Adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)
- [滥用检测与数据保留](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html)
- [Bedrock API Key 管理](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)
- [区域可用性](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html)
- [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)
