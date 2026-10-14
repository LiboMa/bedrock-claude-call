"""
Claude Sonnet 4.5 on Amazon Bedrock - Converse API + reasoning (thinking request shape UNVERIFIED)
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-extended-thinking.html

Sonnet 4.5:
  - 200K context window, 64K max output
  - note the dated model ID with -v1:0 suffix
  - bedrock-runtime (Converse / InvokeModel); no Mantle
  - thinking: the model card only says "Reasoning: Supported"; the thinking
    mode details (adaptive vs "enabled"+budget_tokens, effort) are NOT stated
    on the card [待确认]. This example demonstrates one shape -
    "enabled"+budget_tokens - which has not been verified against an
    authoritative per-model rule; if Bedrock rejects it, the error is printed.

Model IDs (bedrock-runtime, inference profiles):
  us. / eu. / au. / jp. + anthropic.claude-sonnet-4-5-20250929-v1:0   geo cross-region
  global.anthropic.claude-sonnet-4-5-20250929-v1:0                    global cross-region
"""

import boto3

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

try:
    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": "Prove that sqrt(2) is irrational, step by step."}],
            }
        ],
        inferenceConfig={"maxTokens": 8192},
        additionalModelRequestFields={
            # Unverified thinking shape for Sonnet 4.5 (model card: "Reasoning: Supported" only).
            "thinking": {"type": "enabled", "budget_tokens": 4096},
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
