import json
from langchain_oci.chat_models import ChatOCIGenAI

# Library specification:
# https://python.langchain.com/docs/integrations/providers/oci/

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "C:/Users/Cristopher Hdz/Desktop/Test/ocigeniworkshop/sandbox.json"

LLM_MODEL = "cohere.command-r-08-2024"

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# openai.gpt-4.1
# openai.gpt-4o
# xai.grok-4
# xai.grok-3

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

PREAMBLE = """
    You always answer in a one stanza poem.
"""

MESSAGE = """ 
    why is the sky blue?
"""

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file '{config_path}': {e}")
        return None

# Step 1: Load the config file
scfg = load_config(SANDBOX_CONFIG_FILE)

# Step 2: create a LLM client using the credentials and optional parameters
llm_client = ChatOCIGenAI(
    model_id= LLM_MODEL,
    service_endpoint= llm_service_endpoint,
    compartment_id= scfg['oci']['compartment'],
    auth_file_location= scfg["oci"]["configFile"],
    auth_profile= scfg["oci"]["profile"],
    model_kwargs={
        "temperature":0.7, # higer value menas more randon, defaul = 0.3
        "max_tokens": 500, # max token to generate, can lead to incomplete responses
        "preamble_override": PREAMBLE, # Not supported by openai / grok / meta models
        "is_stream": False,
        "seed": 7555, # makes the best effort to make answer determininstic , not gaureented 
        "top_p": 0.7, # ensures only tokens with toptal probabely of p are considered, max value = 0.99, min 0.01, default 0.75
        "top_k": 1, # Different from 0 for meta models. Ensures that only top k tokens are considered, 0 turns it off, max = 500
        "frequency_penalty": 0.0 # Not supported by openai / grok models. Reduces the repeatedness of tokens max value 1.9=0, min 0,0
    }
)

# Step 3: Call the LLM
print(f"**************************Chat Result With seed {llm_client.model_kwargs['seed']} **************************") 
response = llm_client.invoke(MESSAGE)
print(response.content)

print(f"**************************Chat Full LangChain result **************************")
print(response)

llm_client.model_kwargs['seed'] = 6000
print(f"**************************Chat Result With seed {llm_client.model_kwargs['seed']} **************************") 
response = llm_client.invoke(MESSAGE)
print(response.additional_kwargs['finish_reason']) # extra parameters contained in response
print(response.content) # main content parameter that has the string readable response from the model

llm_client.model_kwargs['max_tokens'] = 10
print(f"**************************Chat Result With max_tokens {llm_client.model_kwargs['max_tokens']} **************************")
response = llm_client.invoke(MESSAGE) # Notice this response is using the same modified seed from previous iteration
print(response.additional_kwargs['finish_reason'])
print(response.content)
