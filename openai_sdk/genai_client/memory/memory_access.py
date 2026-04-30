"""What this file does:
Shows memory access policies across two conversations for the same subject:
1) Conversation A stores memory (`store_only`)
2) Conversation B recalls memory (`recall_only`)

How to run:
uv run openai_sdk/genai_client/memory/memory_access.py

Setup:
- Credentials are loaded from `sandbox.yaml` through `OpenAIClientProvider`.
- `memory_subject_id` should represent the same logical user across turns.

Notes:
- The `time.sleep(10)` gives backend memory processing time before recall.
- Keep the same `memory_subject_id` to test cross-conversation memory behavior.
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
