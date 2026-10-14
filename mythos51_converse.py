"""
Claude Mythos 5.1 on Amazon Bedrock (Preview) - bedrock-runtime, Converse API
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5-1.html

Mythos 5.1 is the gated cybersecurity / life-sciences specialist. Its model
card lists bedrock-runtime under endpoint support (no Mantle row, unlike
Mythos 5 which is bedrock-mantle only - see mythos5_mantle.py).

Which runtime APIs (Messages / Converse / Invoke) Mythos 5.1 accepts is NOT
confirmed by the model card [待确认]. This example demonstrates only one of
them (Converse) and reports the error instead of raising if the call is
rejected - either because Converse is unsupported or because access is gated.

Model IDs (inference profiles):
  us.anthropic.claude-mythos-5-1       Geo: US
  global.anthropic.claude-mythos-5-1   Global cross-region routing

  - Preview / "Beta Service"; access via Anthropic trusted access for vetted
    organizations - expect AccessDeniedException until allowlisted
  - adaptive thinking always on (cannot be disabled);
    effort low / medium / high (default) / xhigh / max
  - sampling: temperature must be 1.0 or unset; top_p must be 0.99 or unset;
    temperature and top_p cannot be set together; top_k not supported
  - data retention mode must be `provider_data_share`:
      aws bedrock put-account-data-retention --mode provider_data_share
"""

import boto3

MODEL_ID = "us.anthropic.claude-mythos-5-1"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Converse support on Mythos 5.1 is unconfirmed [待确认]; gated access may also deny.
try:
    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Outline a responsible-disclosure timeline for a vendor "
                            "receiving a critical vulnerability report."
                        )
                    }
                ],
            }
        ],
        inferenceConfig={"maxTokens": 4096},
        additionalModelRequestFields={"output_config": {"effort": "high"}},
    )
except Exception as e:
    raise SystemExit(f"failed (Converse support unconfirmed / gated access): {type(e).__name__}: {e}")

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])

# Dual-use classifiers may refuse; inspect stopReason rather than assuming text.
print(f"\n[stopReason: {response['stopReason']}]")
print(f"[usage: {response['usage']}]")
