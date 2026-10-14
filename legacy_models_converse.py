"""
Legacy Claude models still listed on Amazon Bedrock - Converse API basics
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-1.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-4.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-3-haiku.html

All three are older models served on bedrock-runtime (no Mantle). Sampling
parameter restrictions are not stated on their model cards [待确认], so this
example sends only maxTokens. Lifecycle / EOL dates are not part of the
project's verified model facts [待确认] - check the model cards before planning
a migration.

  Opus 4.1        anthropic.claude-opus-4-1-20250805-v1:0   200K / 32K
                  profiles: us. only (no global)
  Sonnet 4        anthropic.claude-sonnet-4-20250514-v1:0   200K / 64K
                  profiles: us. / eu. / apac. / global.
  Claude 3 Haiku  anthropic.claude-3-haiku-20240307-v1:0    200K / 4K
                  in-Region, or profiles us. / eu.

Calls that fail (model unavailable in your Region, no access) are reported, not raised.
"""

import boto3

MODELS = [
    ("Opus 4.1", "us.anthropic.claude-opus-4-1-20250805-v1:0"),
    ("Sonnet 4", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
    ("Claude 3 Haiku", "us.anthropic.claude-3-haiku-20240307-v1:0"),
]

client = boto3.client("bedrock-runtime", region_name="us-east-1")

for name, model_id in MODELS:
    print(f"=== {name} ({model_id}) ===")
    try:
        response = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Name one benefit of unit tests."}]}],
            inferenceConfig={"maxTokens": 256},
        )
        for block in response["output"]["message"]["content"]:
            if "text" in block:
                print(block["text"].strip())
        print(f"[usage: {response['usage']}]\n")
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}\n")
