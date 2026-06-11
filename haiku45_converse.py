"""
Claude Haiku 4.5 on Amazon Bedrock - Converse API basics (fast & cheap tier)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html

Haiku 4.5: the latency/cost-optimized tier. 200K context, 64K max output,
reasoning supported (extended thinking with budget_tokens; no adaptive,
no effort parameter). Great for classification, routing, and subagents.

Model IDs (bedrock-runtime):
  anthropic.claude-haiku-4-5-20251001-v1:0           in-region
  us. / eu. / au. / jp. prefix                       geo cross-region
  global.anthropic.claude-haiku-4-5-20251001-v1:0    global cross-region
Mantle accepts the alias: anthropic.claude-haiku-4-5
"""

import boto3

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [
                {"text": "Classify this ticket as bug/feature/question: 'App crashes when I tap login twice.'"}
            ],
        }
    ],
    inferenceConfig={"maxTokens": 256},
)

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
