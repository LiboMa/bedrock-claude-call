"""
Claude Opus 5 / Sonnet 5 on Amazon Bedrock - Converse API, default-on adaptive thinking
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

Migration gotcha: on Opus 5 and Sonnet 5, adaptive thinking is ON BY DEFAULT
and can be turned off - budget max_tokens accordingly.

  Opus 5    1M / 128K. Adaptive thinking on by default, can be disabled;
            when thinking is disabled, effort is capped at high.
  Sonnet 5  1M / 128K. Adaptive thinking on by default, including requests
            that omit `thinking`; turn it off with {"type": "disabled"};
            effort configurable.

The model cards do not state how either model handles the older
"enabled"+budget_tokens shape [待确认] - this example does not send it.

Both: bedrock-runtime (Messages / Converse / Invoke) + bedrock-mantle (Messages).
Model IDs (bedrock-runtime profiles): us. / eu. / au. / in. / global. +
  anthropic.claude-opus-5 | anthropic.claude-sonnet-5
"""

import boto3

REGION = "us-east-1"
PROMPT = "What is the time complexity of building a binary heap from n items? One line."

# (name, model_id, additionalModelRequestFields)
CALLS = [
    ("Opus 5 / thinking omitted -> adaptive", "us.anthropic.claude-opus-5", {}),
    ("Opus 5 / thinking disabled, effort high (cap)",
     "us.anthropic.claude-opus-5",
     {"thinking": {"type": "disabled"}, "output_config": {"effort": "high"}}),
    # Sonnet 5 card only says "effort configurable": "low" is a demo value,
    # accepted values / default are 待确认.
    ("Sonnet 5 / thinking omitted -> adaptive, effort low (demo value)",
     "us.anthropic.claude-sonnet-5", {"output_config": {"effort": "low"}}),
    ("Sonnet 5 / thinking disabled",
     "us.anthropic.claude-sonnet-5", {"thinking": {"type": "disabled"}}),
]

client = boto3.client("bedrock-runtime", region_name=REGION)

for name, model_id, extra in CALLS:
    print(f"=== {name} [{model_id}] ===")
    try:
        response = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": PROMPT}]}],
            inferenceConfig={"maxTokens": 2048},
            additionalModelRequestFields=extra,
        )
        content = response["output"]["message"]["content"]
        thought = any("reasoningContent" in b for b in content)
        for block in content:
            if "text" in block:
                print(block["text"].strip())
        print(f"[thinking block present: {thought}, usage: {response['usage']}]\n")
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}\n")
