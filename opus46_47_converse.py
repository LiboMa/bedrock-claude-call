"""
Claude Opus 4.6 / 4.7 on Amazon Bedrock - Converse API + adaptive thinking
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-6.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html

Generation notes:
  Opus 4.6  (anthropic.claude-opus-4-6-v1)  - note the -v1 suffix.
            1M context, 128K output. bedrock-runtime (Converse / InvokeModel);
            no Mantle. Thinking: the model card only says "Reasoning:
            Supported"; thinking mode / effort / budget_tokens rules are NOT
            stated on the card [待确认]. The adaptive call below is an
            unverified demonstration.
  Opus 4.7  (anthropic.claude-opus-4-7)     - clean un-dated ID.
            Thinking: only thinking.type "adaptive" (per model card).
            Sampling parameters (temperature/top_p/top_k): restrictions are
            not stated on the card [待确认] - this example does not send them.
            bedrock-runtime (Messages / Converse / Invoke) + bedrock-mantle.

Calls that fail (no access, unsupported request shape) are reported, not raised.
"""

import boto3

# (name, model_id, additionalModelRequestFields)
MODELS = [
    # Unverified thinking shape for Opus 4.6 (model card: "Reasoning: Supported" only).
    ("Opus 4.6", "us.anthropic.claude-opus-4-6-v1", {"thinking": {"type": "adaptive"}}),
    # Opus 4.7: adaptive is the only thinking type listed on the model card.
    ("Opus 4.7", "us.anthropic.claude-opus-4-7", {"thinking": {"type": "adaptive"}}),
]

client = boto3.client("bedrock-runtime", region_name="us-east-1")

for name, model_id, extra in MODELS:
    print(f"=== {name} ({model_id}) ===")
    try:
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "In one paragraph: what makes a good code review?"}],
                }
            ],
            inferenceConfig={"maxTokens": 1024},
            additionalModelRequestFields=extra,
        )
        for block in response["output"]["message"]["content"]:
            if "text" in block:
                print(block["text"].strip())
        print(f"[usage: {response['usage']}]\n")
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}\n")
