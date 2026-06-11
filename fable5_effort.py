"""
Claude Fable 5 on Amazon Bedrock - Adaptive thinking + effort control (Converse API)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

Fable 5: adaptive thinking is ALWAYS ON and cannot be disabled.
You don't need to pass `thinking` at all; what you tune is `output_config.effort`:

  low    - minimal thinking, fastest, cheapest; good for simple tasks
  medium - moderate thinking; may skip thinking on simple queries
  high   - (default) always thinks; deep reasoning
  max    - unconstrained thinking depth; hardest problems only

IMPORTANT: `effort` lives inside a separate `output_config` object,
NOT inside `thinking` (placing it in `thinking` -> ValidationException).
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
        "output_config": {"effort": "high"},  # low | medium | high | max
    },
)

for block in response["output"]["message"]["content"]:
    if "reasoningContent" in block:
        # Thinking text is omitted by default on Fable 5; the block still
        # appears (with a signature) so multi-turn passback works.
        rc = block["reasoningContent"].get("reasoningText", {})
        if rc.get("text"):
            print(f"--- thinking ---\n{rc['text']}\n----------------")
    elif "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
