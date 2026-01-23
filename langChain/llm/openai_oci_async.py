"""
What this file does:
Demonstrates asynchronous operations using OCI's OpenAI-compatible API for concurrent LLM calls. Shows async invoke and streaming with model performance comparisons between sequential and concurrent execution.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- OpenAI API Reference: https://platform.openai.com/docs/api-reference
- Python Asyncio: https://docs.python.org/3/library/asyncio.html

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).
- Note: Uses OpenAI native client for async operations as LangChain async is not fully compatible with OCI clients.

How to run the file:
uv run langChain/llm/openai_oci_async.py

Comments to important sections of file:
- Step 1: Load config and initialize clients.
- Step 2: Define async invoke function.
- Step 3: Define async streaming function.
- Step 4: Sequential execution demo.
- Step 5: Concurrent execution with gather.
- Step 6: Performance comparison.
"""

import asyncio
import time
import sys
import os
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"

MESSAGE = """
    why is the sky blue? explain in 2 sentences like I am 5
"""

# Step 1: Load config and initialize clients
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Supported models for async operations (OpenAI-compatible models only)
selected_llms = [
    "openai.gpt-4.1",
    "openai.gpt-5",
    # "cohere.command-a-03-2025",      # Cohere doesn't support OpenAI compatible APIs yet
    # "cohere.command-r-08-2024",      # Cohere doesn't support OpenAI compatible APIs yet
    # "meta.llama-4-maverick-17b-128e-instruct-fp8",
    # "meta.llama-4-scout-17b-16e-instruct",
    "xai.grok-4",
    "xai.grok-4-fast-non-reasoning"
]

# Step 2: Define async invoke function
async def call_ainvoke(client, model_id, message):
    """Perform async non-streaming LLM call."""
    start = time.perf_counter()
    response = await client.responses.create(model=model_id, input=message, store=False)
    print(f"\n**************************Async Chat Result (ainvoke) for {model_id} **************************")
    print(response.output_text)
    print(f"ainvoke done in {time.perf_counter() - start:.2f}s")
    return response.output_text

# Step 3: Define async streaming function
async def call_astream(client, model_id, message):
    """Perform async streaming LLM call."""
    start = time.perf_counter()
    print(f"\n**************************Async Chat Stream (astream) for {model_id} **************************")
    async for event in await client.responses.create(model=model_id, input=message, stream=True,store=False):
        if event.type == "response.output_text.delta":
            print(f"{event.delta}", end="", flush=True)
        elif event.type == "response.error":
            print(f"\nError occurred: {event.error}")

    print(f"\nastream done in {time.perf_counter() - start:.2f}s")

# Step 4: Sequential execution demo
async def sequential_run():
    """Execute async calls sequentially for each model."""
    print(f"\n\n*************** Sequential Run ***************\n")
    for llm_id in selected_llms:
        client = OCIOpenAIHelper.get_async_openai_client(config=scfg)
        await call_ainvoke(client, llm_id, MESSAGE)
        await call_astream(client, llm_id, MESSAGE)

# Step 5: Concurrent execution with gather
async def gather_run():
    """Execute async calls concurrently using asyncio.gather."""
    print(f"\n\n*************** Gather Run (Concurrent) ***************\n")
    tasks = []
    for llm_id in selected_llms:
        client = OCIOpenAIHelper.get_async_openai_client(config=scfg)
        tasks.append(call_ainvoke(client, llm_id, MESSAGE))
        tasks.append(call_astream(client, llm_id, MESSAGE))
    await asyncio.gather(*tasks)

# Step 6: Performance comparison
async def main():
    """Main function demonstrating sequential vs concurrent execution."""
    total_start = time.perf_counter()
    await sequential_run()
    seq_time = time.perf_counter()
    print(f"\nTotal time sequential: {seq_time - total_start:.2f}s")
    await gather_run()
    print(f"\nTotal time gather: {time.perf_counter() - seq_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
