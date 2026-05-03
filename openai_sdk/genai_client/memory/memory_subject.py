"""What this file does:
Shows memory recall using a shared `memory_subject_id` across conversations:
1) Conversation A stores user preferences
2) Conversation B asks to recall those preferences

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Conversations API reference: https://platform.openai.com/docs/api-reference/conversations
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Keep `memory_subject_id` consistent between conversations.

How to run from repo root:
uv run openai_sdk/genai_client/memory/memory_subject.py

Safe experiments:
1. Try different memory statements and ask targeted recall questions.
2. Increase `time.sleep(...)` when memory indexing requires longer delay.
3. Re-run with a new `memory_subject_id` to isolate test sessions.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Store memory in first conversation.
3. Step 3: Recall memory in second conversation.
"""

from openai import OpenAI
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
BASIC_PROMPT = "When did the Roman Empire fall?"
STREAM_PROMPT = "Why the sky is blue?"

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2a: Create first conversation.
    conversation1 = client.conversations.create(
        metadata={ "memory_subject_id": "user_123456" },
    )
    # Step 2b: Send preference turn to store memory.
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="I like Fish. I don't like Shrimp.",
        conversation=conversation1.id
    )
    print(response.output_text)
    # Step 2c: Wait for memory indexing.
    time.sleep(10)
    # Step 3a: Create second conversation with same subject id.
    conversation2 = client.conversations.create(
        metadata={ "memory_subject_id": "user_123456" },
    )
    # Step 3b: Ask a recall question.
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="What do I like",
        conversation=conversation2.id
    )
    print(response.output_text)

if __name__ == "__main__":
    main()
