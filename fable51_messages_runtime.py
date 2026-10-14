"""
Claude Fable 5.1 on Amazon Bedrock - Messages API on bedrock-runtime (anthropic SDK)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5-1.html

bedrock-runtime also exposes the Anthropic Messages API at
    https://bedrock-runtime.{region}.amazonaws.com/anthropic
so the plain `Anthropic` client works with a Bedrock API key and the
geo/global inference profile ID (Fable 5.1 has no in-Region runtime option).

Fable 5.1 vs Fable 5:
  - adaptive thinking always on (cannot be disabled), effort documented as
    low / medium / high (default) / xhigh / max
  - sampling: temperature must be 1.0 or unset; top_p must be 0.99 or unset;
    temperature and top_p cannot be set together; top_k not supported
  - dual-use classifiers (cyber / life sciences): HTTP 200 with
    stop_reason == "refusal" + stop_details -> handle as a primary path
  - data retention mode must be `aws_review`

Prerequisites:
  pip install -U anthropic aws-bedrock-token-generator
  (provide_token() mints a short-term Bedrock API key from the AWS credential chain)
"""

from anthropic import Anthropic
from aws_bedrock_token_generator import provide_token

REGION = "us-east-1"
MODEL_ID = "global.anthropic.claude-fable-5-1"   # or us.anthropic.claude-fable-5-1

client = Anthropic(
    base_url=f"https://bedrock-runtime.{REGION}.amazonaws.com/anthropic",
    api_key=provide_token(region=REGION),
)

with client.messages.stream(
    model=MODEL_ID,
    max_tokens=8192,
    output_config={"effort": "xhigh"},
    messages=[
        {
            "role": "user",
            "content": "Find the bug: def mean(xs): return sum(xs) / len(xs) - 1",
        }
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

message = stream.get_final_message()
if message.stop_reason == "refusal":
    print(f"\nRequest refused. stop_details: {getattr(message, 'stop_details', None)}")

print(f"\n\n[stop_reason: {message.stop_reason}]")
print(f"[usage: input={message.usage.input_tokens}, output={message.usage.output_tokens}]")
