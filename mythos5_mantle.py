"""
Claude Mythos 5 on Amazon Bedrock (Preview) - Mantle endpoint ONLY
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-5.html

Mythos 5 is Anthropic's specialist model for cybersecurity and life sciences
(vulnerability discovery, drug design, biodefense screening). Access is gated
due to the dual-use nature of these domains - expect AccessDeniedException
until your account is allowlisted.

Key differences vs Fable 5:
  - bedrock-mantle endpoint ONLY (no bedrock-runtime: no Invoke, no Converse)
  - us-east-1 in-region only (no geo/global inference profiles)
  - Preview / "Beta Service" under AWS Service Terms
  - data retention mode must be `provider_data_share` (Fable 5 needs `aws_review`)

Its successor Claude Mythos 5.1 lists bedrock-runtime (no Mantle row) on its
model card; its runtime API rows are unconfirmed (see mythos51_converse.py).

Prerequisites:
  pip install -U "anthropic[bedrock]"
  export AWS_BEARER_TOKEN_BEDROCK="<your Bedrock API key>"   # or AWS cred chain
  aws bedrock put-account-data-retention --mode provider_data_share
"""

from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")

message = client.messages.create(
    model="anthropic.claude-mythos-5",
    max_tokens=2048,
    output_config={"effort": "high"},  # adaptive always on; 示例值，取值/默认待确认
    messages=[
        {
            "role": "user",
            "content": (
                "Summarize current best practices for triaging a suspected "
                "memory-corruption vulnerability report in an open-source C library."
            ),
        }
    ],
)

# Like Fable 5, dual-use classifiers can return stop_reason == "refusal"
# inside an HTTP 200 - treat it as a normal response path.
if message.stop_reason == "refusal":
    print("Request refused by content classifier.")
else:
    for block in message.content:
        if block.type == "text":
            print(block.text)

print(f"\n[stop_reason: {message.stop_reason}]")
