"""
What this file does:
Demonstrates streaming responses with OCI's OpenAI-compatible API, comparing invoke vs stream methods across multiple models with performance timing. Shows real-time token streaming and finish reasons.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- LangChain Streaming: https://docs.langchain.com/oss/python/langchain/chat_models#streaming
- OpenAI Streaming API: https://platform.openai.com/docs/api-reference/streaming

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI config and Generative AI project details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/llm/openai_oci_stream.py

Important sections:
- Step 1: Load config and initialize dependencies.
- Step 2: Define supported models for testing.
- Step 3: Test invoke method for each model.
- Step 4: Test streaming method for each model.
- Step 5: Compare performance between invoke and stream.
"""

import time
import sys
import os
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Step 1: Load config and initialize dependencies
def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
        return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

MESSAGE = """
    why is the sky blue? explain in 2 sentences like I am 5
"""

# Step 2: Define supported models for testing
selected_llms = [
    "openai.gpt-5.4",
    "openai.gpt-5.2",
    "openai.gpt-oss-120b",
    "xai.grok-4-1-fast-non-reasoning",
    # "xai.grok-4.3",  # Newly documented by OCI, but not yet accepted by this endpoint/project.
    "google.gemini-2.5-pro",
]

# Step 3: Test invoke method for each model
def extract_text(content):
    """Return readable text from LangChain string or Responses API list content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return str(content)


def test_invoke_method(client, model_id, message):
    """Test the invoke method with timing."""
    print(f"\n**************************Chat Result (invoke) for {model_id} **************************")
    start = time.perf_counter()
    response = client.invoke(message)
    print(extract_text(response.content))
    print(f"\nInvoke done in {time.perf_counter() - start:.2f}s")

# Step 4: Test streaming method for each model
def test_stream_method(client, model_id, message):
    """Test the streaming method with timing."""
    print(f"\n**************************Chat Stream Result (stream) for {model_id} **************************")
    start = time.perf_counter()
    for chunk in client.stream(message):
        if hasattr(chunk, 'additional_kwargs') and 'finish_reason' in chunk.additional_kwargs:
            print(f"\nFinish Reason: {chunk.additional_kwargs['finish_reason']}")
            break
        print(extract_text(getattr(chunk, 'content', '')), end='', flush=True)
    print(f"\nStream done in {time.perf_counter() - start:.2f}s")

# Step 5: Compare performance between invoke and stream
if __name__ == "__main__":
    for model_id in selected_llms:
        client = OCIOpenAIHelper.get_langchain_openai_client(
            model_name=model_id,
            config=scfg
        )

        try:
            test_invoke_method(client, model_id, MESSAGE)
        except Exception as exc:
            print(f"\nSKIPPED {model_id}: unavailable for this project or endpoint.")
            print(f"Reason: {exc}")
            continue

        try:
            test_stream_method(client, model_id, MESSAGE)
        except Exception as exc:
            print(f"\nSKIPPED streaming for {model_id}: invoke works, but streaming is unavailable or returned an unsupported stream event.")
            print(f"Reason: {exc}")
