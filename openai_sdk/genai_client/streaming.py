""" What this file does:
Demonstrates a focused streaming-only example using Responses API.
It prints token deltas as the model generates them.

Documentation for reference:
- Responses API migration and features: https://developers.openai.com/api/docs/guides/migrate-to-responses
- Streaming guide: https://developers.openai.com/api/docs/guides/streaming-responses
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
uv run openai_sdk/genai_client/streaming.py

Safe experiments:
1. Print all chunk types to understand the stream schema.
2. Change `MODEL_ID` and compare latency.
3. Replace prompt with a longer task.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create streaming response.
3. Step 3: Render text deltas in real time. """

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
USER_PROMPT = "Why the sky is blue?"

def main() -> None:
    # Step 1: Build configured client.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Request streamed output.
    print("Starting streamed response. Tokens will appear live below:")
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
