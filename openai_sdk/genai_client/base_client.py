""" What this file does:
Demonstrates the two foundational Responses API patterns:
1) one standard response, and 2) one streamed response.

Documentation for reference:
- Responses API: https://platform.openai.com/docs/api-reference/responses
- Streaming guide: https://platform.openai.com/docs/guides/streaming-responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution
- #genai-hosted-deployment-users: GA deployment and integration updates

Environment setup:
- Create `.env` from `.env.example`
- Ensure endpoint/project/profile values are set for OCI

How to run the file:
uv run python genai_client/base_client.py

Safe experiments:
1. Change `BASIC_PROMPT` and `STREAM_PROMPT`.
2. Swap `MODEL_ID` with another available model.
3. Print all stream chunk types to inspect event flow.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Execute standard response call.
3. Step 3: Execute streamed response call. """

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
BASIC_PROMPT = "When did the Roman Empire fall?"
STREAM_PROMPT = "Why the sky is blue?"


def main() -> None:
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Run a standard non-streaming request.
    basic_response = client.responses.create(model=MODEL_ID, input=BASIC_PROMPT)
    print(basic_response.output_text)

    # Step 3: Run a streaming request and print text deltas live.
    streaming_response = client.responses.create(
        model=MODEL_ID,
        input=STREAM_PROMPT,
        stream=True,
    )
    for stream_chunk in streaming_response:
        if stream_chunk.type == "response.output_text.delta":
            print(stream_chunk.delta, end="", flush=True)


if __name__ == "__main__":
    main()
