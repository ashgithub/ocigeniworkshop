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
uv run langChain/llm/openai_oci_responses_stateful.py

rember to note the conversation id ans use it in subsequent conversations

Comments to important sections of file:
- Step 1: Load config and initialize client.
- Step 2: Define conversation questions.
- Step 3: Demonstrate stateful conversation using previous response ID.
- Step 4: Interactive demo of conversation store using OCI APIs.
"""

import os
import sys
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oci_openai_helper import OCIOpenAIHelper
from langchain_core.messages import HumanMessage
import openai

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
LLM_MODEL = "xai.grok-4-1-fast-non-reasoning"
#LLM_MODEL = "openai.gpt-4.1"
# Step 1: Load config and initialize client
def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

def find_conversation_by_id(client, conv_id):
    """Find an existing conversation by ID."""
    try:
        conv = client.conversations.retrieve(conv_id)
        print(f"Found conversation: {conv_id}")
        # Optional: Peek history
        items = client.conversations.items.list(conv_id, limit=2)
        if items.data:
            print("Recent history:")
            for item in reversed(items.data):
                role = item.role
                content = str(item.content)[:100] + "..." if item.content else str(item)[:100] + "..."
                print(f"  {role}: {content}")
        return conv
    except openai.NotFoundError:
        print(f"Conversation {conv_id} not found.")
        return None

def create_conversation(client, topic):
    """Create a new conversation with metadata."""
    conv = client.conversations.create(metadata={"topic": topic})
    print(f"Created new conversation: {conv.id} (topic: {topic}). Use this ID next time.")
    return conv

scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: Define conversation questions
questions = [
    "Tell me something about Oracle",
    "What are some key insights of the actual products?",
    "Which is the company we are talking about?"
]

# Step 3: Demonstrate stateful conversation
def demonstrate_stateful_conversation(client, questions):
    """Demonstrate conversation state with previous message using responses api."""
    print("\n====== responses with (previous message id) ======")
    previous_response_id=None
    for idx, q in enumerate(questions):
        response = client.responses.create(model=LLM_MODEL,input=q,store=True, previous_response_id=previous_response_id)
        previous_response_id=response.id
        print(f"\nUSER {idx+1}: {q}")
        print(f"RESPONSE {idx+1}: {response.output_text}")

# Step 4: Interactive demo of conversation store using OCI APIs.
def demonstrate_conversation_store(client, questions):
    """Demonstrate persistent conversation store with user-provided ID."""
    print("\n====== WITH Conversation Store (Persistent Across Runs) ======")
    topic = "workshop demo"
    
    # Ask user for ID
    user_input = input("Enter conversation ID (or press Enter to create new): ").strip()
    conv_id = user_input if user_input else None
    
    conv = None
    if conv_id:
        conv = find_conversation_by_id(client, conv_id)
        if not conv:
            print("Creating new since ID invalid.")
    
    if not conv:
        conv = create_conversation(client, topic)
    
    conv_id = conv.id
    
    # Ask questions
    previous_response_id = None
    for idx, q in enumerate(questions):
        response = client.responses.create(
            model=LLM_MODEL,
            input=q,
            conversation=conv_id,
            store=True,
 #           previous_response_id=previous_response_id
        )
        previous_response_id = response.id
        print(f"\nUSER {idx+1}: {q}")
        print(f"RESPONSE {idx+1}: {response.output_text}")
    
    print(f"\nConversation {conv_id} updated in OCI store.")
    

        
if __name__ == "__main__":
    client = OCIOpenAIHelper.get_sync_openai_client(
        model_name=LLM_MODEL,
        config=scfg
    )

    demonstrate_stateful_conversation(client, questions)
    #demonstrate_conversation_store(client, questions)
