"""
What this file does:
Demonstrates basic chat functionality using OCI's OpenAI-compatible API for LLM interactions. Shows single calls, batch processing, parameter tuning, model performance comparison, and different prompt types.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- OpenAI API Reference: https://platform.openai.com/docs/api-reference
- LangChain Chat Models: https://docs.langchain.com/oss/python/langchain/chat_models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/llm/openai_oci_chat.py

Comments to important sections of file:
- Step 1: Load config and initialize client.
- Step 2: Create OpenAI LLM client.
- Step 3: Single LLM call demonstration.
- Step 4: Model performance comparison with timing.
- Step 5: Batch processing example.
- Step 6: Max tokens parameter demonstration.
- Step 7: System and user prompt types.
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

LLM_MODEL = "openai.gpt-4.1"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

MESSAGE = """
    why is the sky blue? explain in 2 sentences like i am 5
"""

# Step 1: Load config and initialize client
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: Create OpenAI LLM client using credentials and optional parameters
llm_client = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=scfg
)

# Step 3: Single LLM call demonstration
print(f"\n\n**************************Chat Result for {LLM_MODEL} **************************")
response = llm_client.invoke(MESSAGE)
print(response)

# Step 4: Model performance comparison with timing
selected_llms = [
    "openai.gpt-oss-20b",
    "openai.gpt-4.1",
    "openai.gpt-5.2",
    # "cohere.command-a-03-2025",      # Cohere doesn't support OpenAI compatible APIs yet
    # "cohere.command-r-08-2024",      # Cohere doesn't support OpenAI compatible APIs yet
    "meta.llama-4-maverick-17b-128e-instruct-fp8",
    "meta.llama-4-scout-17b-16e-instruct",
    "xai.grok-4",
    "xai.grok-4-fast-non-reasoning"
]

# Test each model with timing
for llm_id in selected_llms:
    print(f"\n\n**************************Chat Result for {llm_id} **************************")
    llm_client.model_name = llm_id
    start_time = time.time()
    response = llm_client.invoke(MESSAGE)
    end_time = time.time()
    print(response)
    print(f"\n Time taken for {llm_id}: {end_time - start_time:.2f} seconds\n\n")

print(f"\n\n**************************Chat Full LangChain result for {llm_id} **************************")
print(response)

# Step 5: Batch processing example
print(f"\n\n**************************Chat Result With batch for {llm_id} **************************")
try:
    # If batch method supported
    responses = llm_client.batch(["why is sky blue", "why is it dark at night"])
    print(responses)
except AttributeError:
    # Fallback to sequential batch
    questions = ["why is sky blue", "why is it dark at night"]
    batch_responses = [llm_client.invoke(q) for q in questions]
    for q, r in zip(questions, batch_responses):
        print(f"Q: {q}\nA: {r}")

# Step 6: Max tokens parameter demonstration
print(f"\n\n**************************Chat Result With max_tokens 10 for {llm_id}**************************")
llm_client.max_tokens = 10
response = llm_client.invoke(MESSAGE)
try:
    print(response.additional_kwargs['finish_reason'])
except Exception:
    pass
print(response)

# Step 7: System and user prompt types demonstration
print(f"\n\n**************************Chat Result with system & user prompts for {llm_id} **************************")
system_message = {"role": "system", "content": "You are a poetic assistant who responds in exactly four lines."}
user_message = {"role": "user", "content": "What is the meaning of life?"}
messages = [system_message, user_message]

response = llm_client.invoke(messages)
print(response)
