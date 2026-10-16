"""
Claude Fable 5 on Amazon Bedrock - Adaptive thinking + effort control (Converse API)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

Fable 5: adaptive thinking is ALWAYS ON and cannot be disabled (per model
card; the exact error returned for "disabled" or "enabled"+budget_tokens is
not stated there [待确认]).
You don't need to pass `thinking` at all; what you tune is `output_config.effort`.

The Fable 5 model card only says "effort level is configurable"; the accepted
values and the default are NOT stated there [待确认]. The effort value below is
a demo value, not a confirmed per-model rule. (Fable 5.1 documents
low/medium/high/xhigh/max with default high - see fable51_messages_runtime.py.)

IMPORTANT: `effort` lives inside a separate `output_config` object,
NOT inside `thinking`.
"""

import boto3

MODEL_ID = "us.anthropic.claude-fable-5"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": (
                        "Three players A, B, C each draw one ball numbered 1-100. "
                        "A beats B if A's number > B's; similarly B vs C, C vs A. "
                        "Winner by majority of pairwise wins. Is drawing uniformly "
                        "a Nash equilibrium? Justify briefly."
                    )
                }
            ],
        }
    ],
    inferenceConfig={"maxTokens": 8192},
    # Claude-specific fields go through additionalModelRequestFields.
    additionalModelRequestFields={
        "thinking": {"type": "adaptive"},     # optional on Fable 5 (always on anyway)
        "output_config": {"effort": "high"},  # 示例值，取值/默认待确认
    },
)

for block in response["output"]["message"]["content"]:
    if "reasoningContent" in block:
        # Whether Fable 5 returns thinking text or only a signed block is
        # not stated on the model card [待确认] - print it only if present.
        rc = block["reasoningContent"].get("reasoningText", {})
        if rc.get("text"):
            print(f"--- thinking ---\n{rc['text']}\n----------------")
    elif "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
