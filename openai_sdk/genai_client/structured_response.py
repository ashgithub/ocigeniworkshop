""" What this file does:
Demonstrates structured output parsing using a Pydantic schema.
The model output is validated and returned as a typed Python object.

Documentation for reference:
- Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs
- Responses API parse: https://platform.openai.com/docs/api-reference/responses/parse
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
uv run python genai_client/structured_response.py

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
from openai_sdk.openai_client_provider import OpenAIClientProvider


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
    event = response.output_parsed
    print(event)


if __name__ == "__main__":
    main()
