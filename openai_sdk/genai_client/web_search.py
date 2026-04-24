""" What this file does:
Demonstrates the built-in `web_search` tool in a Responses API call.
Useful when answer quality depends on current events or fresh web data.

Documentation for reference:
- Tools guide: https://platform.openai.com/docs/guides/tools
- Web search guide: https://platform.openai.com/docs/guides/tools-web-search
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
uv run python genai_client/web_search.py

Safe experiments:
1. Ask for news from a specific country.
2. Compare answers with and without `web_search`.
3. Add a follow-up call with `previous_response_id`.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Send tool-enabled prompt.
3. Step 3: Print final text output.
"""

from openai import OpenAI
from dotenv import load_dotenv
from openai_sdk.openai_client_provider import OpenAIClientProvider

load_dotenv()

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "What was a positive news story from today?"


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Send a tool-enabled request.
    response = client.responses.create(
        model=MODEL_ID,
        tools=[{"type": "web_search"}],
        input=USER_PROMPT,
    )

    # Step 3: Print final answer text.
    print(response.output_text)


if __name__ == "__main__":
    main()
