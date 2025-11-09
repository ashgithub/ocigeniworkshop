"""
What this file does:
Demonstrates conversation history management in chat interactions using OCI's OpenAI-compatible API. Shows the difference between stateless conversations and conversations with maintained history.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- OCI OpenAI Compatible SDK: https://github.com/oracle-samples/oci-openai
- LangChain Messages: https://docs.langchain.com/oss/python/langchain_core/messages
- Conversation Memory: https://docs.langchain.com/oss/python/langchain/memory

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run langChain/llm/openai_oci_history.py

Comments to important sections of file:
- Step 1: Load config and initialize client.
- Step 2: Define conversation questions.
- Step 3: Demonstrate stateless conversation.
- Step 4: Demonstrate conversation with history.
"""

import os
import sys
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper
from langchain_core.messages import HumanMessage

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
LLM_MODEL = "xai.grok-4-fast-non-reasoning"

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

# Step 2: Define conversation questions
questions = [
    "Tell me something about Oracle",
    "What are some key insights of the actual products?",
    "Which is the company we are talking about?"
]

# Step 3: Demonstrate stateless conversation
def demonstrate_stateless_conversation(client, questions):
    """Demonstrate conversation without maintaining history."""
    print("\n====== WITHOUT History (Stateless each turn) ======")
    for idx, q in enumerate(questions):
        user_msg = HumanMessage(q)
        response = client.invoke([user_msg])
        print(f"\nUSER {idx+1}: {q}")
        print(f"RESPONSE {idx+1}: {getattr(response, 'content', response)}")

# Step 4: Demonstrate conversation with history
def demonstrate_conversation_with_history(client, questions):
    """Demonstrate conversation while maintaining and growing history."""
    print("\n====== WITH History (Growing Conversation) ======")
    msgs = []
    for idx, q in enumerate(questions):
        user_msg = HumanMessage(q)
        msgs.append(user_msg)
        response = client.invoke(msgs)
        msgs.append(response)
        print(f"\nUSER {idx+1}: {q}")
        print(f"RESPONSE {idx+1}: {getattr(response, 'content', response)}")

if __name__ == "__main__":
    client = OCIOpenAIHelper.get_client(
        model_name=LLM_MODEL,
        config=scfg
    )

    demonstrate_stateless_conversation(client, questions)
    demonstrate_conversation_with_history(client, questions)
