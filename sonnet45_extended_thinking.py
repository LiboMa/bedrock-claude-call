"""
Claude Sonnet 4.5 on Amazon Bedrock - Converse API + extended thinking (budget_tokens)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4-5.html

Sonnet 4.5 is the LAST Sonnet generation using the older thinking style:
  - adaptive thinking is NOT supported (4.6+ only)
  - use thinking.type "enabled" + budget_tokens (>= 1024, < max_tokens)
  - 200K context window, 64K max output
  - note the dated model ID with -v1:0 suffix

Model IDs (bedrock-runtime):
  anthropic.claude-sonnet-4-5-20250929-v1:0          in-region
  us. / eu. / au. / jp. prefix                       geo cross-region
  global.anthropic.claude-sonnet-4-5-20250929-v1:0   global cross-region
"""

import boto3

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

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
        # Older extended-thinking shape: explicit token budget.
        "thinking": {"type": "enabled", "budget_tokens": 4096},
    },
)

for block in response["output"]["message"]["content"]:
    if "reasoningContent" in block:
        rc = block["reasoningContent"].get("reasoningText", {})
        if rc.get("text"):
            print(f"--- thinking ---\n{rc['text'][:500]}...\n----------------")
    elif "text" in block:
        print(block["text"])

print(f"\n[usage: {response['usage']}]")
