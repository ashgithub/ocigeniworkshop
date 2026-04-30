"""What this file does:
Shows memory recall using a shared `memory_subject_id` across conversations:
1) Conversation A stores user preference
2) Conversation B asks the model to recall that preference

How to run:
uv run openai_sdk/genai_client/memory/memory_subject.py

Setup:
- Credentials are loaded from `sandbox.yaml` through `OpenAIClientProvider`.
- Keep `memory_subject_id` consistent between conversations.

Notes for beginners:
- The pause (`time.sleep(10)`) is intentional to allow memory indexing.
- If recall is incomplete, wait longer and run again with the same subject id.
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
        metadata={ "memory_subject_id": "user_123456" },
    )
    # a turn on first conversation
    response = client.responses.create(
        model="openai.gpt-4.1",
        input="I like Fish. I don't like Shrimp.",
        conversation=conversation1.id
    )
    print(response.output_text)
    # delay for long-term memory processing
    time.sleep(10)
    # second conversation
    conversation2 = client.conversations.create(
        metadata={ "memory_subject_id": "user_123456" },
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
