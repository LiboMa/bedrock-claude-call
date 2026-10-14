"""
Claude Opus 4.8 on Amazon Bedrock - one file, every supported call path
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-8.html

Opus 4.8 (launched 2026-05-28) supports BOTH endpoints:
  1. Converse      (bedrock-runtime, boto3)          - AWS-native, model-agnostic
  2. InvokeModel   (bedrock-runtime, boto3)          - raw Anthropic Messages body
  3. Messages      (bedrock-runtime, anthropic SDK)  - .../anthropic base URL + API key
  4. Messages      (bedrock-mantle, anthropic SDK)   - first-party API parity

Same pattern applies to Opus 4.7 - just swap MODEL_ID. Opus 4.6 has no
Mantle endpoint (bedrock-runtime Converse / InvokeModel).
Thinking: the Opus 4.7 / 4.8 model cards list only thinking.type "adaptive".
Sampling parameters (temperature/top_p/top_k): restrictions are not stated on
the cards [待确认] - this example does not send them (recommended: omit).
"""

import json

import boto3
from anthropic import Anthropic, AnthropicBedrockMantle
from aws_bedrock_token_generator import provide_token

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
            "thinking": {"type": "adaptive"},      # Opus 4.7/4.8: adaptive only (model card)
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


def via_runtime_messages() -> str:
    # Short-term Bedrock API key minted from the AWS credential chain.
    client = Anthropic(
        base_url=f"https://bedrock-runtime.{REGION}.amazonaws.com/anthropic",
        api_key=provide_token(region=REGION),
    )
    message = client.messages.create(
        model=MODEL_ID,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": PROMPT}],
    )
    return "".join(b.text for b in message.content if b.type == "text")


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
        ("Messages (bedrock-runtime)", via_runtime_messages),
        ("Messages (bedrock-mantle)", via_mantle),
    ]:
        print(f"=== {name} ===")
        try:
            print(fn().strip(), "\n")
        except Exception as e:
            print(f"failed: {type(e).__name__}: {e}\n")
