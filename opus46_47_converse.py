"""
Claude Opus 4.6 / 4.7 on Amazon Bedrock - Converse API + adaptive thinking
Refs:
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-6.html
  https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-7.html

Generation notes:
  Opus 4.6  (anthropic.claude-opus-4-6-v1)  - note the -v1 suffix.
            1M context. Adaptive thinking recommended (budget_tokens deprecated).
            effort: low/medium/high/max. bedrock-runtime only (no Mantle).
  Opus 4.7  (anthropic.claude-opus-4-7)     - clean un-dated ID.
            Adaptive thinking ONLY ("enabled"+budget_tokens -> 400 error).
            temperature/top_p/top_k REMOVED. effort adds "xhigh".
            Both bedrock-runtime and bedrock-mantle.
"""

import boto3

MODELS = [
    ("Opus 4.6", "us.anthropic.claude-opus-4-6-v1", "high"),
    ("Opus 4.7", "us.anthropic.claude-opus-4-7", "xhigh"),  # xhigh debuted on 4.7
]

client = boto3.client("bedrock-runtime", region_name="us-east-1")

for name, model_id, effort in MODELS:
    print(f"=== {name} ({model_id}, effort={effort}) ===")
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
            additionalModelRequestFields={
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": effort},
            },
        )
        for block in response["output"]["message"]["content"]:
            if "text" in block:
                print(block["text"].strip())
        print(f"[usage: {response['usage']}]\n")
    except Exception as e:
        print(f"failed: {type(e).__name__}: {e}\n")
