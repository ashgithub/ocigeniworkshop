"""What this file does:
Creates a conversation with short-term memory optimization metadata enabled.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Conversations API reference: https://platform.openai.com/docs/api-reference/conversations
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Metadata key `short_term_memory_optimization` is set to `"True"` in this sample.

How to run from repo root:
uv run openai_sdk/genai_client/memory/memory_optimization.py

Safe experiments:
1. Toggle `short_term_memory_optimization` between `"True"` and `"False"`.
2. Add one `responses.create(...)` turn to inspect practical impact.
3. Add additional metadata keys to test project conventions.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Create conversation with optimization metadata.
"""

from openai import OpenAI
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from openai_client_provider import OpenAIClientProvider


MODEL_ID = "openai.gpt-5.2"
BASIC_PROMPT = "When did the Roman Empire fall?"
STREAM_PROMPT = "Why the sky is blue?"

def main():
    # Step 1: Build a configured OpenAI client for OCI endpoint usage.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Create conversation with short-term memory optimization metadata.
    conversation1 = client.conversations.create(
                metadata={"topic": "demo", "short_term_memory_optimization": "True"},
                items=[{"type": "message", "role": "user", "content": "Hello!"}],
        )
    
    print(conversation1)

if __name__ == "__main__":
    main()
