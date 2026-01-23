"""
What this file does:
Demonstrates streaming responses with OCI's OpenAI-compatible API, comparing invoke vs stream methods across multiple models with performance timing. Shows real-time token streaming and finish reasons.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- LangChain Streaming: https://docs.langchain.com/oss/python/langchain/chat_models#streaming
- OpenAI Streaming API: https://platform.openai.com/docs/api-reference/streaming

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/llm/openai_oci_stream.py

Comments to important sections of file:
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
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
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
    "openai.gpt-4.1",
    "openai.gpt-5.2",
    # "cohere.command-a-03-2025",      # Cohere doesn't support OpenAI compatible APIs yet
    # "cohere.command-r-08-2024",      # Cohere doesn't support OpenAI compatible APIs yet
    "meta.llama-4-maverick-17b-128e-instruct-fp8",
    "meta.llama-4-scout-17b-16e-instruct",
    "xai.grok-4",
    "xai.grok-4-fast-non-reasoning"
]

# Step 3: Test invoke method for each model
def test_invoke_method(client, model_id, message):
    """Test the invoke method with timing."""
    print(f"\n**************************Chat Result (invoke) for {model_id} **************************")
    start = time.perf_counter()
    response = client.invoke(message)
    print(response.content)
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
        print(getattr(chunk, 'content', ''), end='', flush=True)
    print(f"\nStream done in {time.perf_counter() - start:.2f}s")

# Step 5: Compare performance between invoke and stream
if __name__ == "__main__":
    for model_id in selected_llms:
        client = OCIOpenAIHelper.get_langchain_openai_client(
            model_name=model_id,
            config=scfg
        )

        test_invoke_method(client, model_id, MESSAGE)
        test_stream_method(client, model_id, MESSAGE)
