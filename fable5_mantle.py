"""
Claude Fable 5 on Amazon Bedrock - Mantle endpoint via the Anthropic SDK
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

bedrock-mantle is Bedrock's Anthropic-compatible endpoint:
    https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages
It speaks the exact same Messages API as Anthropic's first-party API, so the
official `anthropic` SDK works directly via the AnthropicBedrockMantle client.

Prerequisites:
  pip install -U "anthropic[bedrock]"

Auth (either works):
  export AWS_BEARER_TOKEN_BEDROCK="<your Bedrock API key>"   # simplest
  ... or the standard AWS credential chain (SigV4) is used automatically.

NOTE: on Mantle, the model ID is the bare in-region ID (anthropic.claude-fable-5);
geo/global inference profile IDs are a bedrock-runtime concept.
"""

from anthropic import AnthropicBedrockMantle

client = AnthropicBedrockMantle(aws_region="us-east-1")

# Streaming by default: with always-on thinking and up to 128K output,
# long requests over plain HTTP risk timeouts.
with client.messages.stream(
    model="anthropic.claude-fable-5",
    max_tokens=4096,
    output_config={"effort": "high"},  # low | medium | high | max
    messages=[
        {
            "role": "user",
            "content": "Design a multi-region active-active architecture on AWS for 100k RPS.",
        }
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

message = stream.get_final_message()
print(f"\n\n[stop_reason: {message.stop_reason}]")
print(f"[usage: input={message.usage.input_tokens}, output={message.usage.output_tokens}]")
