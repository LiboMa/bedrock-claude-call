"""
Claude Fable 5 on Amazon Bedrock - InvokeModel API (native Anthropic Messages body)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

Use InvokeModel when you want the raw Anthropic Messages request/response shape
over the classic bedrock-runtime endpoint (SigV4 / AWS_BEARER_TOKEN_BEDROCK).
Requires the account data retention mode `aws_review` (see fable5_converse.py).
"""

import json

import boto3

MODEL_ID = "us.anthropic.claude-fable-5"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.invoke_model(
    modelId=MODEL_ID,
    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            # Optional on Fable 5 - adaptive thinking is always on.
            # "thinking": {"type": "adaptive"},
            "output_config": {"effort": "medium"},  # 示例值，取值/默认待确认
            "messages": [
                {
                    "role": "user",
                    "content": "Explain why the sum of two even numbers is always even.",
                }
            ],
        }
    ),
)

body = json.loads(response["body"].read())

# Handle refusals as a primary response path on Fable 5: dual-use
# cyber/bio classifiers return HTTP 200 with stop_reason == "refusal".
if body.get("stop_reason") == "refusal":
    print(f"Request refused. stop_details: {body.get('stop_details')}")
else:
    for block in body["content"]:
        if block["type"] == "thinking" and block.get("thinking"):
            print(f"--- thinking ---\n{block['thinking']}\n----------------")
        elif block["type"] == "text":
            print(block["text"])

print(f"\n[stop_reason: {body.get('stop_reason')}]")
print(f"[usage: {body.get('usage')}]")
