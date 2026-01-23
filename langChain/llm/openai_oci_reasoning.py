"""
What this file does:
Demonstrates reasoning capabilities with advanced models like GPT-5 using OCI's OpenAI-compatible API. Shows how to enable reasoning features, capture reasoning summaries, and monitor token usage.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- OpenAI Reasoning API: https://platform.openai.com/docs/guides/reasoning
- LangChain Chat Models: https://docs.langchain.com/oss/python/langchain/chat_models

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/llm/openai_oci_reasoning.py

Comments to important sections of file:
- Step 1: Load config and import dependencies.
- Step 2: Define reasoning-focused messages.
- Step 3: Initialize client with reasoning parameters.
- Step 4: Invoke model and extract response components.
- Step 5: Display answer, reasoning summary, and token usage.
"""

import os
import sys
from dotenv import load_dotenv
from envyaml import EnvYAML

# Step 1: Load config and import dependencies
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper

load_dotenv()
config = EnvYAML("sandbox.yaml")

# Step 2: Define reasoning-focused messages
LLM_MODEL = "openai.gpt-5"

messages = [
    (
        "system",
        "You are an expert reasoning assistant. Explain your steps clearly, then provide a brief summary."
    ),
    (
        "human",
        "If there are 21 apples and they are split equally among 3 friends, how many apples does each friend receive?"
    ),
]

# Step 3: Initialize client with reasoning parameters
llm = OCIOpenAIHelper.get_langchain_openai_client(
    model_name=LLM_MODEL,
    config=config,
    use_responses_api=True,
    reasoning={"effort": "low", "summary": "auto"},
)

# Step 4: Invoke model and extract response components
res = llm.invoke(messages)

# Step 5: Display answer, reasoning summary, and token usage
print("\n=== Answer ===")
print(getattr(res, "content", res))

# Reasoning summary (if available)
ak = getattr(res, "additional_kwargs", {}) or {}
summary = ak.get("reasoning_summary") or ak.get("summary") or (ak.get("reasoning") or {}).get("summary")
print("\n=== Reasoning Summary ===")
print(summary if summary else "N/A")

# Token counts (if available)
usage = getattr(res, "usage_metadata") or {}
input_tokens = usage.get("input_tokens") or usage.get("input_tokens")
output_tokens = usage.get("output_tokens") or usage.get("output_tokens")
reasoning = usage.get("output_token_details", {}).get("reasoning") if usage.get("output_token_details") else None
print("\n=== Token Usage ===")
print(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}, reasoning: {reasoning}")
