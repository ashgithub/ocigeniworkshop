""" What this file does:
Demonstrates a focused streaming-only example using Responses API.
It prints token deltas as the model generates them.

Documentation for reference:
- Responses API: https://platform.openai.com/docs/api-reference/responses
- Streaming guide: https://platform.openai.com/docs/guides/streaming-responses
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
uv run python genai_client/streaming.py

Safe experiments:
1. Print all chunk types to understand the stream schema.
2. Change `MODEL_ID` and compare latency.
3. Replace prompt with a longer task.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create streaming response.
3. Step 3: Render text deltas in real time. """

from openai import OpenAI
from openai_sdk.openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Why the sky is blue?"


def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Request streamed output.
    stream_response = client.responses.create(
        model=MODEL_ID,
        input=USER_PROMPT,
        stream=True,
    )

    # Step 3: Print token deltas in real-time.
    for stream_chunk in stream_response:
        if stream_chunk.type == "response.output_text.delta":
            print(stream_chunk.delta, end="", flush=True)


if __name__ == "__main__":
    main()
