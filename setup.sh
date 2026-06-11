#!/bin/bash
# Quick setup for Amazon Bedrock Anthropic Claude examples

set -e

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo ""
echo "=== Setup complete ==="
echo ""
echo "Configure your environment (either works):"
echo '  export AWS_BEARER_TOKEN_BEDROCK="<your-bedrock-api-key>"'
echo "  ... or use the standard AWS credential chain (~/.aws/credentials)."
echo ""
echo "One-time opt-in required for Claude Fable 5 / Mythos 5:"
echo "  aws bedrock put-account-data-retention --mode provider_data_share"
echo ""
echo "Then run:"
echo "  python fable5_converse.py"
echo "  python test_all.py"
