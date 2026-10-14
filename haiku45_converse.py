"""
Claude Haiku 4.5 on Amazon Bedrock - Converse API basics (fast & cheap tier)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html

Haiku 4.5: the latency/cost-optimized 4.x tier. 200K context, 64K max output.
The model card says "Reasoning: Supported" but does not state the thinking
mode details (adaptive vs "enabled"+budget_tokens, effort) [待确认], so this
example sends no `thinking` field. Great for classification, routing, and
subagents. For the newer Haiku with adaptive thinking + effort, see
claude55_family.py (Claude Haiku 5.5).

Model IDs:
  bedrock-runtime: the bare ID is NOT supported for on-demand throughput -
    use a geo or global inference profile:
      us. / eu. / au. / jp. / in. + anthropic.claude-haiku-4-5-20251001-v1:0
      global.anthropic.claude-haiku-4-5-20251001-v1:0
  bedrock-mantle (In-Region, Messages API only): anthropic.claude-haiku-4-5
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
