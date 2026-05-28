""" What this file does:
Demonstrates the simplest generation-plus-retrieval pattern:
1) Read the vector store id from the workshop configuration.
2) Ask a natural-language question.
3) Let the `file_search` tool retrieve relevant chunks for the model.
4) Print the final model answer.

Documentation for reference:
- OpenAI SDK overview: https://developers.openai.com/api/docs/quickstart
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- File search guide: https://platform.openai.com/docs/guides/tools-file-search
- GenAI platform GA docs: https://confluence.oraclecorp.com/confluence/display/OCAS/Generative+AI+Platform+Agentic+Capabilities+-+March+2026+GA+User+Guide#expand-ExpandtolearnmoreifyouaremigratingfromLABetatoGA

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with sandbox environment and execution for this repo
- #genai-hosted-deployment-users: GA deployment and integration updates with latest SDK

Environment setup:
- Configure OCI credentials, project, compartment, and profile in `sandbox.yaml`.
- Set `oci.unstructured_vector_store_id` in `sandbox.yaml` to the vector store you want to query.

How to run the file:
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
DEFAULT_PROMPT = "What does this knowledge base say about outages?"

def main():
    # Step 1: Build the OCI OpenAI client from sandbox.yaml values.
    print("Step 1 - Building OCI OpenAI client.")
    client: OpenAI = OpenAIClientProvider().oci_openai_client

    # Step 2: Resolve the vector store id that the file_search tool should query.
    print("Step 2 - Resolving vector store id from sandbox.yaml.")
    vector_store_id = OpenAIClientProvider().oci_openai_unstructured_vector_store_id

    # Step 3: Call Responses API with file_search. The model sees the user
    # prompt and can call the tool against the configured vector store.
    print(f"Step 3 - Asking model with file_search over vector store: {vector_store_id}")
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
