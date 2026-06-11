"""
Claude Fable 5 on Amazon Bedrock - Tool calling (Converse API toolConfig)
Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html

Converse uses the toolSpec/toolUse/toolResult shape (NOT Anthropic's native
input_schema shape, and NOT the OpenAI flat Responses shape).
"""

import json

import boto3

MODEL_ID = "us.anthropic.claude-fable-5"

client = boto3.client("bedrock-runtime", region_name="us-east-1")

tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get the current weather for a location.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "City name"},
                        },
                        "required": ["location"],
                    }
                },
            }
        }
    ]
}


def get_weather(location: str) -> dict:
    return {"location": location, "temperature_c": 22, "condition": "sunny"}


messages = [
    {"role": "user", "content": [{"text": "What's the weather like in Seattle?"}]}
]

response = client.converse(
    modelId=MODEL_ID,
    messages=messages,
    toolConfig=tool_config,
    inferenceConfig={"maxTokens": 2048},
)

# Agentic loop: keep going while the model asks for tools.
while response["stopReason"] == "tool_use":
    assistant_msg = response["output"]["message"]
    # Pass the assistant message back UNCHANGED (including any
    # reasoningContent blocks - Fable 5 emits these between tool calls).
    messages.append(assistant_msg)

    tool_results = []
    for block in assistant_msg["content"]:
        if "toolUse" in block:
            tu = block["toolUse"]
            print(f">> model called {tu['name']}({json.dumps(tu['input'])})")
            result = get_weather(**tu["input"])
            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId": tu["toolUseId"],
                        "content": [{"json": result}],
                    }
                }
            )

    messages.append({"role": "user", "content": tool_results})
    response = client.converse(
        modelId=MODEL_ID,
        messages=messages,
        toolConfig=tool_config,
        inferenceConfig={"maxTokens": 2048},
    )

for block in response["output"]["message"]["content"]:
    if "text" in block:
        print(block["text"])
