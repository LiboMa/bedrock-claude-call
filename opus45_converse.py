"""
Claude Opus 4.5 on Amazon Bedrock - Converse API + reasoning (thinking request shape UNVERIFIED)
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-extended-thinking.html

Opus 4.5 (launched 2025-11-24) still uses the dated -v1:0 model ID style and a
200K context window / 64K max output.

Thinking: the model card only says "Reasoning: Supported". The thinking mode
details (adaptive vs "enabled"+budget_tokens, effort) are NOT stated on the
card [待确认]. This example demonstrates one shape - "enabled"+budget_tokens -
which has not been verified against an authoritative per-model rule; if
Bedrock rejects it, the error is printed instead of raised.
Endpoints: bedrock-runtime (Converse / InvokeModel); no Mantle.

Model IDs (bedrock-runtime, inference profiles):
  us. / eu. + anthropic.claude-opus-4-5-20251101-v1:0   geo cross-region
  global.anthropic.claude-opus-4-5-20251101-v1:0        global cross-region
"""

import boto3

MODEL_ID = "us.anthropic.claude-opus-4-5-20251101-v1:0"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

try:
    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": "Can you explain the features of Amazon Bedrock?"}],
            }
        ],
        inferenceConfig={"maxTokens": 4096},
        additionalModelRequestFields={
            # Unverified thinking shape for Opus 4.5 (model card: "Reasoning: Supported" only).
            "thinking": {"type": "enabled", "budget_tokens": 2048},
        },
    )
except Exception as e:
    raise SystemExit(f"failed: {type(e).__name__}: {e}")

for block in response["output"]["message"]["content"]:
    if "reasoningContent" in block:
        rc = block["reasoningContent"].get("reasoningText", {})
        if rc.get("text"):
            print(f"--- thinking ---\n{rc['text'][:500]}...\n----------------")
    elif "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
