"""
Claude Sonnet 4.6 on Amazon Bedrock - Converse API + adaptive thinking + effort
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-6.html

Sonnet 4.6: mid-tier workhorse with a 1M context window and 64K max output.
Adaptive thinking is supported (recommended); budget_tokens is deprecated.
Effort levels: low / medium / high (NO "max" - that is Opus-tier only).

Model IDs (bedrock-runtime):
  anthropic.claude-sonnet-4-6            in-region
  us. / eu. / au. / jp. prefix           geo cross-region
  global.anthropic.claude-sonnet-4-6     global cross-region
"""

import boto3

MODEL_ID = "us.anthropic.claude-sonnet-4-6"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

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
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "medium"},  # low | medium | high (no "max" on Sonnet)
    },
)

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
