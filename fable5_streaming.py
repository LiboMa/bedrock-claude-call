"""
Claude Fable 5 on Amazon Bedrock - Streaming (ConverseStream API)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-fable-5.html

Streaming is strongly recommended for Fable 5: with up to 128K output tokens
and always-on thinking, non-streamed requests on long tasks risk HTTP timeouts.
"""

import boto3

MODEL_ID = "us.anthropic.claude-fable-5"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

response = client.converse_stream(
    modelId=MODEL_ID,
    messages=[
        {
            "role": "user",
            "content": [{"text": "Write a Python function that implements binary search, with tests."}],
        }
    ],
    inferenceConfig={"maxTokens": 4096},
)

for event in response["stream"]:
    if "contentBlockDelta" in event:
        delta = event["contentBlockDelta"]["delta"]
        if "text" in delta:
            print(delta["text"], end="", flush=True)
    elif "messageStop" in event:
        print(f"\n\n[stopReason: {event['messageStop']['stopReason']}]")
    elif "metadata" in event:
        print(f"[usage: {event['metadata'].get('usage')}]")
