"""
Claude 5.5 family (Haiku 5.5 / Sonnet 5.5 / Opus 5.5) on Amazon Bedrock - Converse API
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

All three: 1M context, 128K max output, bedrock-runtime (Messages / Converse /
Invoke) + bedrock-mantle (Messages), effort = low/medium/high/xhigh/max.

  Haiku 5.5   adaptive thinking ON by default, CAN be disabled;
              default effort medium; effort capped at high when thinking is
              disabled (xhigh/max + disabled -> 400). First Haiku with effort.
  Sonnet 5.5  adaptive thinking ON by default; default effort high.
  Opus 5.5    adaptive thinking ALWAYS ON, cannot be disabled; default effort medium.

Model IDs (bedrock-runtime has no in-Region option - use a profile):
  Haiku 5.5   us. / eu. / au. / jp. / global. + anthropic.claude-haiku-5-5
  Sonnet 5.5  us. / eu. / au. / global.       + anthropic.claude-sonnet-5-5
  Opus 5.5    us. / eu. / au. / jp. / global. + anthropic.claude-opus-5-5
bedrock-mantle uses the bare ID (e.g. anthropic.claude-opus-5-5).
"""

import boto3

REGION = "us-east-1"
PROMPT = "Give three concrete tips for reducing p99 latency in a Python web service."

# (name, model_id, additionalModelRequestFields)
CALLS = [
    ("Haiku 5.5 / default (adaptive, effort medium)",
     "us.anthropic.claude-haiku-5-5", {}),
    ("Haiku 5.5 / thinking disabled (effort <= high)",
     "us.anthropic.claude-haiku-5-5",
     {"thinking": {"type": "disabled"}, "output_config": {"effort": "high"}}),
    ("Sonnet 5.5 / adaptive, effort xhigh",
     "us.anthropic.claude-sonnet-5-5", {"output_config": {"effort": "xhigh"}}),
    ("Opus 5.5 / adaptive (always on), effort max",
     "us.anthropic.claude-opus-5-5", {"output_config": {"effort": "max"}}),
]

client = boto3.client("bedrock-runtime", region_name=REGION)

for name, model_id, extra in CALLS:
    print(f"=== {name} [{model_id}] ===")
    try:
        response = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": PROMPT}]}],
            # max_tokens caps thinking + answer together.
            inferenceConfig={"maxTokens": 4096},
            additionalModelRequestFields=extra,
        )
        for block in response["output"]["message"]["content"]:
            if "text" in block:
                print(block["text"].strip())
        print(f"[stopReason: {response['stopReason']}, usage: {response['usage']}]\n")
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}\n")
