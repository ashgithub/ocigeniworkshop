""" What this file does:
Demonstrates structured output parsing using a Pydantic schema.
The model output is validated and returned as a typed Python object.

Documentation for reference:
- Structured Outputs guide: https://developers.openai.com/api/docs/guides/structured-outputs
- Responses API migration and features: https://developers.openai.com/api/docs/guides/migrate-to-responses
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
uv run openai_sdk/genai_client/structured_response.py

Safe experiments:
1. Add optional fields to `CalendarEvent`.
2. Change user message to include multiple events.
3. Compare this parse flow vs regular text flow.

Important sections:
1. Step 1: Define target schema.
2. Step 2: Run `responses.parse` with schema.
3. Step 3: Inspect parsed object. """

from openai import OpenAI
from pydantic import BaseModel
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-4.1"
INPUT_MESSAGES = [
    {"role": "system", "content": "Extract the event information."},
    {
        "role": "user",
        "content": "Alice and Bob are going to a science fair on Friday.",
    },
]

class CalendarEvent(BaseModel):
    # Step 1: Schema used for typed output parsing.
    name: str
    date: str
    participants: list[str]

def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Parse output directly into CalendarEvent.
    response = client.responses.parse(
        model=MODEL_ID,
        input=INPUT_MESSAGES,
        store=False,
        text_format=CalendarEvent,
    )

    # Step 3: Print parsed object.
    print("Parsed typed output:")
    event = response.output_parsed
    print(event)


if __name__ == "__main__":
    main()
