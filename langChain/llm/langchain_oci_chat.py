import json
from langchain_oci.chat_models import ChatOCIGenAI

from dotenv import load_dotenv
from envyaml import EnvYAML
# Library specification:
# https://python.langchain.com/docs/integrations/providers/oci/
# https://github.com/oracle-devrel/langchain-oci-genai

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#
#
#  OCI's langchain client supports all oci models, but it doesnt support all the features requires for robust agents (output schema, function calling etc)
#  OCI's Openai compatible api supports all the features frm OpenAI's generate API (responsys support will come in dec), but doesnt support cohere yet 
#  Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
#  if you have errors running sample code reach out for help in #igiu-ai-learning
#   note this will require to downgrade the langchain to 0.3.27 as this is not compatible with langchain 1.0.0
#####
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

LLM_MODEL = "openai.gpt-4.1"
#LLM_MODEL = "cohere.command-r-08-2024"

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm


llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

PREAMBLE = """
    You always answer in a one stanza poem.
"""

MESSAGE = """ 
    why is the sky blue? expalin in 2 sentenses like i am 5
"""

def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: create a LLM client using the credentials and optional parameters
llm_client = ChatOCIGenAI(
    model_id= LLM_MODEL,
    service_endpoint= llm_service_endpoint,
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

# Step 3: Call Single LLM
print(f"\n\n**************************Chat Result for {llm_client.model_id} **************************") 
response = llm_client.invoke(MESSAGE)
print(response.content)

import time  # Added for timing

# Run through selected LLMs and print results
selected_llms = [
    "openai.gpt-4.1",
    "openai.gpt-5",
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


#step4:  batch
print(f"\n\n**************************Chat Result With batch for {llm_client.model_id} **************************") 
response = llm_client.batch(["why is sky blue","why is it dark at night"])
#print(response.additional_kwargs['finish_reason']) # extra parameters contained in response
print(response) # main content parameter that has the string readable response from the model

#step6:  max token
llm_client.model_kwargs['max_tokens'] = 10
print(f"\n\n**************************Chat Result With max_tokens {llm_client.model_kwargs['max_tokens']} for {llm_client.model_id}**************************")
response = llm_client.invoke(MESSAGE) # Notice this response is using the same modified seed from previous iteration
print(response.additional_kwargs['finish_reason'])
print(response.content)

#step7: prompt types sytem & human 
# Demonstrate system (preamble) and human (user content) prompt types
print(f"\n\n**************************Chat Result with system & user prompts for {llm_client.model_id} **************************")
system_message = {"role": "system", "content": "You are a poetic assistant who responds in exactly four lines."}
user_message = {"role": "user", "content": "What is the meaning of life?"}
messages = [system_message, user_message]

response = llm_client.invoke(messages)
print(response.content)
