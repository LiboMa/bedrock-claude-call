"""
Claude Sonnet 4.6 on Amazon Bedrock - Converse API + reasoning (thinking request shape UNVERIFIED)
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

Sonnet 4.6: 4.x mid-tier model with a 1M context window and 64K max output.
Thinking: the model card only says "Reasoning: Supported". The thinking mode
details (adaptive vs "enabled"+budget_tokens, effort levels, default
behaviour when `thinking` is omitted) are NOT stated on the card [待确认].
This example demonstrates one shape - adaptive + output_config.effort - which
has not been verified against an authoritative per-model rule; if Bedrock
rejects it, the error is printed instead of raised.
Endpoints: bedrock-runtime (Converse / InvokeModel); no Mantle.

Model IDs (bedrock-runtime, inference profiles):
  us. / eu. / au. / jp. + anthropic.claude-sonnet-4-6   geo cross-region
  global.anthropic.claude-sonnet-4-6                    global cross-region
"""

import boto3

MODEL_ID = "us.anthropic.claude-sonnet-4-6"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

try:
    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": "Refactor advice: when should I split a Python module into a package?"}],
            }
        ],
        inferenceConfig={"maxTokens": 2048},
        additionalModelRequestFields={
            # Unverified thinking shape for Sonnet 4.6 (model card: "Reasoning: Supported" only).
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "medium"},  # 示例值，取值/默认待确认
        },
    )
except Exception as e:
    raise SystemExit(f"failed: {type(e).__name__}: {e}")

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
