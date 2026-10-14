"""
Claude Fable 5 on Amazon Bedrock - Basic Converse API call (bedrock-runtime)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

Auth: standard AWS credential chain, or a Bedrock API key via
      AWS_BEARER_TOKEN_BEDROCK.

NOTE: Fable 5 requires the account data retention mode to be `aws_review`
      in the Region:
      aws bedrock put-account-data-retention --mode aws_review
"""

import boto3

# bedrock-runtime has no in-Region option for Fable 5 - use an inference profile:
#   us.anthropic.claude-fable-5       Geo: US
#   global.anthropic.claude-fable-5   Global cross-region routing
MODEL_ID = "us.anthropic.claude-fable-5"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [{"text": "Can you explain the features of Amazon Bedrock?"}],
        }
    ],
    # Fable 5 sampling rules: temperature must be 1.0 or unset; top_p must be
    # >= 0.99 and < 1.0 or unset; top_k is not supported. Easiest: only set maxTokens.
    inferenceConfig={"maxTokens": 2048},
)

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

print(f"\n[stopReason: {response['stopReason']}]")
print(f"[usage: {response['usage']}]")
