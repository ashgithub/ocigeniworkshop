"""What this file does:
Creates a conversation with short-term memory optimization metadata enabled.

How to run:
uv run openai_sdk/genai_client/memory/memory_optimization.py

Setup:
- Credentials are loaded from `sandbox.yaml` through `OpenAIClientProvider`.
- Metadata key `short_term_memory_optimization` is set to `"True"` in this sample.

Notes for beginners:
- This example focuses only on conversation creation with memory-related metadata.
- Extend it with `responses.create(...)` calls if you want to inspect runtime behavior.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
BASIC_PROMPT = "When did the Roman Empire fall?"
STREAM_PROMPT = "Why the sky is blue?"

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    conversation1 = client.conversations.create(
                metadata={"topic": "demo", "short_term_memory_optimization": "True"},
                items=[{"type": "message", "role": "user", "content": "Hello!"}],
        )
    
    print(conversation1)

if __name__ == "__main__":
    main()
