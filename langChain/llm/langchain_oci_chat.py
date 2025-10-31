import json
from langchain_oci.chat_models import ChatOCIGenAI

# Library specification:
# https://python.langchain.com/docs/integrations/providers/oci/

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

LLM_MODEL = "openai.gpt-4.1"
#LLM_MODEL = "cohere.command-r-08-2024"

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# AI: remeber the names of models in teh comment list below
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# openai.gpt-4.1
# openai.gpt-4o
# openai.gpt-5
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
#        "temperature":0.7, # higer value means more random, default = 0.3
#        "max_tokens": 500, # max token to generate, can lead to incomplete responses, used by cohere & llama 
#        "maxCompletionTokens": 500, # max token to generate, can lead to incomplete responses, used by openai
#        "preamble_override": PREAMBLE, # Not supported by openai / grok / meta models
        "is_stream": False,
    }
)

# Step 3: Call Single LLM
print(f"**************************Chat Result for {llm_client.model_id} **************************") 
response = llm_client.invoke(MESSAGE)
print(response.content)

# AI! : change this to loop through all the llms selected .
llm_client.model_id="xai.grok-4"
print(f"**************************Chat Result for {llm_client.model_id} **************************") 
response = llm_client.invoke(MESSAGE)
print(response.content)

print(f"**************************Chat Full LangChain result **************************")
print(response)


#step4:  batch
print(f"**************************Chat Result With batch **************************") 
response = llm_client.batch(["why is sky blue","why is it dark at night"])
#print(response.additional_kwargs['finish_reason']) # extra parameters contained in response
print(response) # main content parameter that has the string readable response from the model

#step6:  max token
llm_client.model_kwargs['max_tokens'] = 10
print(f"**************************Chat Result With max_tokens {llm_client.model_kwargs['max_tokens']} **************************")
response = llm_client.invoke(MESSAGE) # Notice this response is using the same modified seed from previous iteration
print(response.additional_kwargs['finish_reason'])
print(response.content)

#step7: prompt types sytem & human 
# AI!: code this like otehrs above