"""What this file does:
Runs a simple `responses.create` call using the `file_search` tool.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- File search guide: https://platform.openai.com/docs/guides/tools-file-search
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Environment setup:
- Configure OCI credentials in `sandbox.yaml`.
- Set `VECTOR_STORE_ID` constant or env var `VECTOR_STORE_ID`.

How to run from repo root:
uv run openai_sdk/genai_client/vector_store/file_search.py

Safe experiments:
1. Replace `DEFAULT_PROMPT` with your own domain-specific questions.
2. Compare answers with and without `file_search` tool usage.
3. Try multiple vector stores to compare retrieval quality.

Important sections:
1. Step 1: Build configured OpenAI client.
2. Step 2: Resolve vector store id.
3. Step 3: Execute Responses API call with file search tool.
"""

import os
import sys
from openai import OpenAI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from openai_client_provider import OpenAIClientProvider

MODEL_ID = "openai.gpt-5.2"
DEFAULT_PROMPT = "What does this knowledge base say about OCI GPU shapes?"
VECTOR_STORE_ID = ""  # Set your vector store id here, or use env var VECTOR_STORE_ID.

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve required runtime values.
    vector_store_id = VECTOR_STORE_ID or os.getenv("VECTOR_STORE_ID", "").strip()
    if not vector_store_id:
        raise ValueError(
            "Missing vector store id. Set VECTOR_STORE_ID constant in this file "
            "or create env var VECTOR_STORE_ID."
        )

    # Step 3: Call Responses API with file_search.
    response = client.responses.create(
        model=MODEL_ID,
        input=DEFAULT_PROMPT,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
            }
        ],
    )
    print("Result of the file search on vector store:")
    print(response.output_text)

if __name__ == "__main__":
    main()
