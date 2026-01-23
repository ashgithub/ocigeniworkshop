"""
What this file does:
Demonstrates basic chat functionality using LangChain's ChatOCIGenAI client for OCI Generative AI models. Shows single calls, batch processing, parameter tuning, model performance comparison, and different prompt types.


Documentation to reference:
- OCI Gen AI Chat Models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
- LangChain OCI Integration: https://python.langchain.com/docs/integrations/providers/oci/
- LangChain OCI GenAI GitHub: https://github.com/oracle-devrel/langchain-oci-genai
- OCI Python SDK: https://github.com/oracle/oci-python-sdk

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment details.
- .env: Load environment variables (e.g., API keys if needed).
- Note: This file uses `langchain_oci` library which is not compatible with LangChain v1.0.0 as of November 2025. The code will not work without downgrading LangChain to 0.3.x.

How to run the file:
uv run langChain/llm/langchain_oci_chat.py

Comments to important sections of file:
- Step 1: Load config and initialize client.
- Step 2: Single LLM call demonstration.
- Step 3: Model performance comparison with timing.
- Step 4: Batch processing example.
- Step 5: Max tokens parameter demonstration.
- Step 6: System and user prompt types.
"""

import json
import time
from langchain_oci.chat_models import ChatOCIGenAI
from dotenv import load_dotenv
from envyaml import EnvYAML

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"
# Available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

LLM_SERVICE_ENDPOINT = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

PREAMBLE = """
    You always answer in a one stanza poem.
"""

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

# Step 3: Single LLM call demonstration
print(f"\n\n**************************Chat Result for {llm_client.model_id} **************************")
response = llm_client.invoke(MESSAGE)
print(response.content)

# Step 4: Model performance comparison with timing
selected_llms = [
    "openai.gpt-4.1",
    "openai.gpt-5.2",
    "cohere.command-a-03-2025",
    "cohere.command-r-08-2024",
    "meta.llama-4-maverick-17b-128e-instruct-fp8",
    "meta.llama-4-scout-17b-16e-instruct",
    "xai.grok-4",
    "xai.grok-4-fast-non-reasoning"
]

for llm_id in selected_llms:
    llm_client.model_id = llm_id
    print(f"\n\n**************************Chat Result for {llm_client.model_id} **************************")
    start_time = time.time()
    response = llm_client.invoke(MESSAGE)
    end_time = time.time()
    print(response.content)
    print(f"\n Time taken for {llm_client.model_id}: {end_time - start_time:.2f} seconds\n\n")

print(f"\n\n**************************Chat Full LangChain result for {llm_client.model_id} **************************")
print(response)

# Step 5: Batch processing example
print(f"\n\n**************************Chat Result With batch for {llm_client.model_id} **************************")
response = llm_client.batch(["why is sky blue", "why is it dark at night"])
# print(response.additional_kwargs['finish_reason']) # extra parameters contained in response
print(response) # main content parameter that has the string readable response from the model

# Step 6: Max tokens parameter demonstration
llm_client.model_kwargs['max_tokens'] = 10
print(f"\n\n**************************Chat Result With max_tokens {llm_client.model_kwargs['max_tokens']} for {llm_client.model_id}**************************")
response = llm_client.invoke(MESSAGE) # Notice this response is using the same modified seed from previous iteration
print(response.additional_kwargs['finish_reason'])
print(response.content)

# Step 7: System and user prompt types demonstration
print(f"\n\n**************************Chat Result with system & user prompts for {llm_client.model_id} **************************")
system_message = {"role": "system", "content": "You are a poetic assistant who responds in exactly four lines."}
user_message = {"role": "user", "content": "What is the meaning of life?"}
messages = [system_message, user_message]

response = llm_client.invoke(messages)
print(response.content)
