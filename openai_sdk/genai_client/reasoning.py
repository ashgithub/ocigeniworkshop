""" What this file does:
Demonstrates reasoning configuration in Responses API and shows how to
inspect raw structured output blocks.

Documentation for reference:
- Responses API: https://platform.openai.com/docs/api-reference/responses
- Reasoning models guide: https://platform.openai.com/docs/guides/reasoning
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users
- #igiu-innovation-lab
- #igiu-ai-learning
- #genai-hosted-deployment-users

Environment setup:
- Create `.env` from `.env.example`
- Ensure endpoint/project/profile values are set for OCI

How to run the file:
uv run python genai_client/reasoning.py

Safe experiments:
1. Change reasoning effort: `low`, `medium`, `high`.
2. Disable summary and compare output shape.
3. Try `store=True` to compare behavior.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create response with reasoning controls.
3. Step 3: Inspect serialized output blocks. """

import json

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.4"
USER_PROMPT = "What is the answer to 12 * (3 + 9)?"
REASONING_SETTINGS = {"effort": "high", "summary": "auto"}


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create response with reasoning controls.
    response = client.responses.create(
        model=MODEL_ID,
        input=USER_PROMPT,
        reasoning=REASONING_SETTINGS,
        store=False,
    )

    # Step 3: Pretty-print output items for inspection.
    pretty_output = json.dumps(response.to_dict()["output"], indent=4)
    print(pretty_output)


if __name__ == "__main__":
    main()
