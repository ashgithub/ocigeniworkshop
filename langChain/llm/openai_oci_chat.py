import json
import time
import sys
import os
from dotenv import load_dotenv
from envyaml import EnvYAML

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from openai_oci_client import OciOpenAILangChainClient

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#
#
#  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
#  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
#  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
#  if you have errors running sample code reach out for help in #igiu-ai-learning
#####

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"
# LLM_MODEL = "openai.gpt-5"
# available models: https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm

llm_service_endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



MESSAGE = """
    why is the sky blue? expalin in 2 sentenses like i am 5
"""

# Step 1: load config 

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None

scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: create the OpenAI LLM client using credentials and optional parameters

llm_client = OciOpenAILangChainClient(
    profile=scfg['oci']['profile'],
    compartment_id=scfg['oci']['compartment'],
    model=LLM_MODEL,
    service_endpoint=llm_service_endpoint,
)

# Step 3: Call Single LLM
print(f"\n\n**************************Chat Result for {LLM_MODEL} **************************")
response = llm_client.invoke(MESSAGE)
print(response)

# Timing and model loop
selected_llms = [
    "openai.gpt-4.1",
    "openai.gpt-5",
#    "cohere.command-a-03-2025",      # cohere doesnt support openAi compaitable APIs yet 
#    "cohere.command-r-08-2024",      # cohere doesnt support openAi compaitable APIs yet 
    "meta.llama-4-maverick-17b-128e-instruct-fp8",
    "meta.llama-4-scout-17b-16e-instruct",
    "xai.grok-4",
    "xai.grok-4-fast-non-reasoning"
]

# Reinitialize client for each model (since .model assignment isn't supported)
for llm_id in selected_llms:
    print(f"\n\n**************************Chat Result for {llm_id} **************************")
    temp_client = OciOpenAILangChainClient(
        profile=scfg['oci']['profile'],
        compartment_id=scfg['oci']['compartment'],
        model=llm_id,
        service_endpoint=llm_service_endpoint
    )
    start_time = time.time()
    response = temp_client.invoke(MESSAGE)
    end_time = time.time()
    print(response)
    print(f"\n Time taken for {llm_id}: {end_time - start_time:.2f} seconds\n\n")

print(f"\n\n**************************Chat Full LangChain result for {llm_id} **************************")
print(response)

# Step 4: batch
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

# Step 5: max token
print(f"\n\n**************************Chat Result With max_tokens 10 for {llm_id}**************************")
try:
    llm_client.max_tokens = 10
except AttributeError:
    # Some clients may need to be reconstructed or have a kwargs update
    llm_client = OciOpenAILangChainClient(
        profile=scfg['oci']['profile'],
        compartment_id=scfg['oci']['compartment'],
        model=llm_id,
        service_endpoint=llm_service_endpoint,
    )
    # If an initialization parameter is required, extend client code to accept it
response = llm_client.invoke(MESSAGE)
try:
    print(response.additional_kwargs['finish_reason'])
except Exception:
    pass
print(response)

# Step 6: prompt types system & human
print(f"\n\n**************************Chat Result with system & user prompts for {llm_id} **************************")
system_message = {"role": "system", "content": "You are a poetic assistant who responds in exactly four lines."}
user_message = {"role": "user", "content": "What is the meaning of life?"}
messages = [system_message, user_message]

response = llm_client.invoke(messages)
print(response)
