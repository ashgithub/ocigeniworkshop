"""
What this file does:
Demonstrates basic chat functionality using OCI's OpenAI-compatible API for LLM interactions. Shows single calls, batch processing, parameter tuning, model performance comparison, and different prompt types.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- OpenAI API Reference: https://platform.openai.com/docs/api-reference
- LangChain Chat Models: https://docs.langchain.com/oss/python/langchain/chat_models

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/llm/openai_oci_chat.py

Important sections:
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


LLM_MODEL = "xai.grok-4.20-multi-agent-0309"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

MESSAGE = """
    why is the sky blue? explain in 2 sentences like i am 5
"""

# Step 1: Load config and initialize client
def load_config(config_path: str) -> EnvYAML | None:
    """Load configuration from a YAML file."""
    try:
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


