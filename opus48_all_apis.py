"""
Claude Opus 4.8 on Amazon Bedrock - one file, all three call paths
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-8.html

Opus 4.8 (launched 2026-05-28) supports BOTH endpoints and all three APIs:
  1. Converse      (bedrock-runtime, boto3)  - AWS-native, model-agnostic
  2. InvokeModel   (bedrock-runtime, boto3)  - raw Anthropic Messages body
  3. Messages      (bedrock-mantle, anthropic SDK) - first-party API parity

Same pattern applies to Opus 4.6 / 4.7 - just swap MODEL_ID (see README).
Opus 4.7+ removed temperature/top_p/top_k - omit them entirely.
"""

import json

import boto3
from anthropic import AnthropicBedrockMantle

REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-opus-4-8"          # bedrock-runtime (geo US profile)
MANTLE_MODEL_ID = "anthropic.claude-opus-4-8"      # bedrock-mantle (in-region ID)
PROMPT = "Explain the CAP theorem in two sentences."


def via_converse() -> str:
    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": PROMPT}]}],
        inferenceConfig={"maxTokens": 1024},
        additionalModelRequestFields={
            "thinking": {"type": "adaptive"},      # Opus 4.7/4.8: adaptive only
            "output_config": {"effort": "high"},   # 4.7+ also supports "xhigh"
        },
    )
    return "".join(
        b["text"] for b in response["output"]["message"]["content"] if "text" in b
    )


def via_invoke_model() -> str:
    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "thinking": {"type": "adaptive"},
                "messages": [{"role": "user", "content": PROMPT}],
            }
        ),
    )
    body = json.loads(response["body"].read())
    return "".join(b["text"] for b in body["content"] if b["type"] == "text")


def via_mantle() -> str:
    client = AnthropicBedrockMantle(aws_region=REGION)
    message = client.messages.create(
        model=MANTLE_MODEL_ID,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": PROMPT}],
    )
    return "".join(b.text for b in message.content if b.type == "text")


if __name__ == "__main__":
    for name, fn in [
        ("Converse (bedrock-runtime)", via_converse),
        ("InvokeModel (bedrock-runtime)", via_invoke_model),
        ("Messages (bedrock-mantle)", via_mantle),
    ]:
        print(f"=== {name} ===")
        try:
            print(fn().strip(), "\n")
        except Exception as e:
            print(f"failed: {type(e).__name__}: {e}\n")
