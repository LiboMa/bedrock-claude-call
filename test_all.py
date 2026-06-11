"""
Test harness for ALL Anthropic Claude models on Amazon Bedrock.

Two layers of checking:
  1. Syntax check  - py_compile every example script.
  2. Live API test - one short request per model/route using the standard
                     AWS credential chain. Gated models (Mythos 5) and models
                     missing from your account report SKIP/FAIL without
                     aborting the run.

Run:
  python test_all.py                 # syntax + live
  python test_all.py --syntax-only   # no network calls
"""

import json
import subprocess
import sys

SCRIPTS = [
    "fable5_converse.py",
    "fable5_effort.py",
    "fable5_streaming.py",
    "fable5_tool_calling.py",
    "fable5_invoke_model.py",
    "fable5_mantle.py",
    "mythos5_mantle.py",
    "opus48_all_apis.py",
    "opus46_47_converse.py",
    "opus45_converse.py",
    "sonnet46_adaptive.py",
    "sonnet45_extended_thinking.py",
    "haiku45_converse.py",
]

REGION = "us-east-1"


def syntax_check() -> bool:
    print("=== Syntax check all scripts ===\n")
    all_ok = True
    for script in SCRIPTS:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", script],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  {script}: OK")
        else:
            all_ok = False
            print(f"  {script}: FAIL\n{result.stderr.strip()}")
    return all_ok


# --- Live tests ----------------------------------------------------------------

def test_converse(model_id: str) -> tuple[bool, str]:
    import boto3

    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": "Say hello in one word."}]}],
        inferenceConfig={"maxTokens": 64},
    )
    text = "".join(
        b["text"] for b in response["output"]["message"]["content"] if "text" in b
    )
    return bool(text), text.strip()[:80]


def test_invoke(model_id: str) -> tuple[bool, str]:
    import boto3

    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 64,
                "messages": [{"role": "user", "content": "Say hello in one word."}],
            }
        ),
    )
    body = json.loads(response["body"].read())
    text = "".join(b["text"] for b in body["content"] if b["type"] == "text")
    return bool(text), text.strip()[:80]


def test_mantle(model_id: str) -> tuple[bool, str]:
    from anthropic import AnthropicBedrockMantle

    client = AnthropicBedrockMantle(aws_region=REGION)
    message = client.messages.create(
        model=model_id,
        max_tokens=64,
        messages=[{"role": "user", "content": "Say hello in one word."}],
    )
    text = "".join(b.text for b in message.content if b.type == "text")
    return bool(text), text.strip()[:80]


def test_adaptive_effort(model_id: str, effort: str = "low") -> tuple[bool, str]:
    """Adaptive thinking + output_config.effort via Converse."""
    import boto3

    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": "What is 2 + 2?"}]}],
        inferenceConfig={"maxTokens": 256},
        additionalModelRequestFields={
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": effort},
        },
    )
    text = "".join(
        b["text"] for b in response["output"]["message"]["content"] if "text" in b
    )
    return bool(text), text.strip()[:80]


def test_budget_thinking(model_id: str) -> tuple[bool, str]:
    """Older extended-thinking shape (enabled + budget_tokens) via Converse."""
    import boto3

    client = boto3.client("bedrock-runtime", region_name=REGION)
    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": "What is 17 * 23?"}]}],
        inferenceConfig={"maxTokens": 4096},
        additionalModelRequestFields={
            "thinking": {"type": "enabled", "budget_tokens": 1024},
        },
    )
    text = "".join(
        b["text"] for b in response["output"]["message"]["content"] if "text" in b
    )
    return bool(text), text.strip()[:80]


def live_tests() -> bool:
    print("\n=== Live API tests ===\n")
    targets = [
        # Claude 5 generation
        ("converse", "us.anthropic.claude-fable-5", test_converse),
        ("adaptive", "us.anthropic.claude-fable-5", test_adaptive_effort),
        ("invoke  ", "us.anthropic.claude-fable-5", test_invoke),
        ("mantle  ", "anthropic.claude-fable-5", test_mantle),
        ("mantle  ", "anthropic.claude-mythos-5", test_mantle),  # gated: may 404
        # Opus line
        ("converse", "us.anthropic.claude-opus-4-8", test_converse),
        ("mantle  ", "anthropic.claude-opus-4-8", test_mantle),
        ("converse", "us.anthropic.claude-opus-4-7", test_converse),
        ("adaptive", "us.anthropic.claude-opus-4-6-v1", test_adaptive_effort),
        ("converse", "us.anthropic.claude-opus-4-5-20251101-v1:0", test_converse),
        # Sonnet line
        ("adaptive", "us.anthropic.claude-sonnet-4-6", test_adaptive_effort),
        ("budget  ", "us.anthropic.claude-sonnet-4-5-20250929-v1:0", test_budget_thinking),
        # Haiku line
        ("converse", "us.anthropic.claude-haiku-4-5-20251001-v1:0", test_converse),
    ]

    all_ok = True
    for route, model, fn in targets:
        print(f"  [{route}] {model} ... ", end="", flush=True)
        try:
            ok, msg = fn(model)
        except Exception as e:
            ok, msg = False, f"{type(e).__name__}: {e}"
        # Mythos 5 access is allowlisted; don't fail the whole suite on it.
        if not ok and "mythos" in model:
            print(f"SKIP (gated) {msg[:100]}")
            continue
        all_ok &= ok
        print(f"{'PASS' if ok else 'FAIL'} {msg[:100]}")
    return all_ok


def main() -> int:
    syntax_ok = syntax_check()

    if "--syntax-only" in sys.argv:
        print("\nSyntax-only mode (skipping live tests).")
        return 0 if syntax_ok else 1

    try:
        live_ok = live_tests()
    except Exception as e:
        print(f"\nLive tests could not run: {type(e).__name__}: {e}")
        live_ok = False

    print("\nDone.")
    return 0 if (syntax_ok and live_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
