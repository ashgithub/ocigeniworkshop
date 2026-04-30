""" What this file does:
Demonstrates the two foundational Responses API patterns:
1) one standard response from responses API

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Responses API: https://platform.openai.com/docs/api-reference/responses
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Set up the credentials for OCI over the `sandbox.yaml file`
- Make sure to set up a project ID from the console, consult the GenAI platform GA docs for guidance
- Set up the right compartment ID and profile name over the config file

How to run the file:
uv run openai_sdk/genai_client/base_client.py

Safe experiments:
1. Change `BASIC_PROMPT` and `STREAM_PROMPT`.
2. Swap `MODEL_ID` with another available model.
3. Print all stream chunk types to inspect event flow.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Execute standard response call.
"""

from openai import OpenAI
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
BASIC_PROMPT = "When did the Roman Empire fall?"
STREAM_PROMPT = "Why the sky is blue?"

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # first conversation
    conversation1 = client.conversations.create(
        metadata={ 
                    "memory_subject_id": "user_123456",
            "memory_access_policy": "store_only",
            },
    )
    # a turn on first conversation, this conversation can store memory, but cannot recall memory
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="I like Fish. I don't like Shrimp.", 
        conversation=conversation1.id
    )
    print(response.output_text)
    # delay for long-term memory processing
    time.sleep(10)
    # second conversation, this conversation can recall memory, but cannot store new memory
    conversation2 = client.conversations.create(
        metadata={
                "memory_subject_id": "user_123456",
                "memory_access_policy": "recall_only",
            },
    )
    # a turn on second conversation
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="What do I like",
        conversation=conversation2.id
    )
    print(response.output_text)

if __name__ == "__main__":
    main()
