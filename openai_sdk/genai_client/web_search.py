""" What this file does:
Demonstrates the built-in `web_search` tool in a Responses API call.
Useful when answer quality depends on current events or fresh web data.

Documentation for reference:
- Tools guide: https://developers.openai.com/api/docs/guides/tools
- Web search guide: https://developers.openai.com/api/docs/guides/tools-web-search
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution
- #genai-hosted-deployment-users: GA deployment and integration updates

Environment setup:
- Set up the credentials for OCI over the `sandbox.yaml file`
- Make sure to set up a project ID from the console, consult the GenAI platform GA docs for guidance
- Set up the right compartment ID and profile name over the config file

How to run the file:
uv run openai_sdk/genai_client/web_search.py

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
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

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
    print("Final grounded response:")
    print(response.output_text)

if __name__ == "__main__":
    main()
