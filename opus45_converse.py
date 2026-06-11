"""
Claude Opus 4.5 on Amazon Bedrock - Converse API basics
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-5.html

Opus 4.5 (launched 2025-11-24) is the first Opus supporting the `effort`
parameter, while still using the dated -v1:0 model ID style and a 200K
context window (1M arrived with Opus 4.6).

Thinking: extended thinking via budget_tokens, or effort-based control.
Sampling: temperature/top_p still accepted on this generation.

Model IDs (bedrock-runtime):
  anthropic.claude-opus-4-5-20251101-v1:0            in-region
  us. / eu. prefix                                   geo cross-region
  global.anthropic.claude-opus-4-5-20251101-v1:0     global cross-region
"""

import boto3

MODEL_ID = "us.anthropic.claude-opus-4-5-20251101-v1:0"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [{"text": "Can you explain the features of Amazon Bedrock?"}],
        }
    ],
    inferenceConfig={"maxTokens": 2048},
    additionalModelRequestFields={
        "output_config": {"effort": "high"},  # effort debuted on Opus 4.5
    },
)

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
