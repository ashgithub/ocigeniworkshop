"""What this file does:
Demonstrates memory access policies across two conversations for one subject:
1) Conversation A stores memory (`store_only`)
2) Conversation B recalls memory (`recall_only`)

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Conversations API reference: https://platform.openai.com/docs/api-reference/conversations
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Keep `memory_subject_id` stable to represent the same logical end user.

How to run from repo root:
uv run openai_sdk/genai_client/memory/memory_access.py

Safe experiments:
1. Change `memory_access_policy` values to compare behavior.
2. Increase `time.sleep(...)` if recall seems incomplete.
3. Use your own preference statements and verify recall quality.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create store-only conversation and send preference.
3. Step 3: Create recall-only conversation and validate memory retrieval.
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

    # Step 2a: Create first conversation (store-only policy).
    conversation1 = client.conversations.create(
        metadata={ 
                    "memory_subject_id": "user_123456",
            "memory_access_policy": "store_only",
            },
    )
    # Step 2b: Send a turn that should be stored in memory.
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="I like Fish. I don't like Shrimp.", 
        conversation=conversation1.id
    )
    print(response.output_text)
    # Step 2c: Wait for memory processing before recall test.
    time.sleep(10)
    # Step 3a: Create second conversation (recall-only policy).
    conversation2 = client.conversations.create(
        metadata={
                "memory_subject_id": "user_123456",
                "memory_access_policy": "recall_only",
            },
    )
    # Step 3b: Ask for recalled preference.
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="What do I like",
        conversation=conversation2.id
    )
    print(response.output_text)

if __name__ == "__main__":
    main()
