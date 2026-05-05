"""
What this file does:
Demonstrates basic chat functionality using LangChain's `ChatOCIGenAI`
client for OCI Generative AI models.

Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- LangChain OCI Integration: https://python.langchain.com/docs/integrations/providers/oci/
- LangChain OCI GenAI GitHub: https://github.com/oracle-devrel/langchain-oci-genai
- OCI Python SDK: https://github.com/oracle/oci-python-sdk

Relevant Slack channels:
- #generative-ai-users: Questions about OCI Generative AI
- #igiu-innovation-lab: General project discussions
- #igiu-ai-learning: Help with the sandbox environment or with running this code

Environment setup:
- sandbox.yaml: Contains OCI config and compartment details.
- .env: Loads environment variables if needed.
- Note: This file uses `langchain_oci`, which is not compatible with LangChain v1.0.0 as of November 2025.

How to run the file:
uv run langChain/llm/langchain_oci_chat.py

Important sections:
- Step 1: Load configuration and initialize the client
- Step 2: Demonstrate a single LLM call
- Step 3: Compare model performance with timing
- Step 4: Demonstrate batch processing
- Step 5: Demonstrate token limits
- Step 6: Demonstrate system and user prompt roles
"""

import time
from langchain_oci.chat_models import ChatOCIGenAI
from dotenv import load_dotenv
from envyaml import EnvYAML

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "xai.grok-4-1-fast-non-reasoning"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

LLM_SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

PREAMBLE = """
    You always answer in a one stanza poem.
"""

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

# Step 2: Create LLM client using credentials and optional parameters
llm_client = ChatOCIGenAI(
    model_id=LLM_MODEL,
    service_endpoint=LLM_SERVICE_ENDPOINT,
    compartment_id= scfg['oci']['compartment'],
    auth_file_location= scfg["oci"]["configFile"],
    auth_profile= scfg["oci"]["profile"],
    model_kwargs={
#        "temperature":0.7, # higer value means more random, default = 0.3
#        "max_tokens": 500, # max token to generate, can lead to incomplete responses, used by cohere & llama 
#        "maxCompletionTokens": 500, # max token to generate, can lead to incomplete responses, used by openai
#        "preamble_override": PREAMBLE, # Not supported by openai / grok / meta models
        "is_stream": False,
    }
)


# Step 7: System and user prompt types demonstration
print(f"\n\n**************************Chat Result with system & user prompts for {llm_client.model_id} **************************")
system_message = {"role": "system", "content": "You are a poetic assistant who responds in exactly four lines using markdown lists. use bold & italics as needed "}
user_message = {"role": "user", "content": "What are teh best tourist spots in mexico?"}
messages = [system_message, user_message]

response = llm_client.invoke(messages)
print(response.content)
