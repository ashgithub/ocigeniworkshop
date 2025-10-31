import json
from pydantic import BaseModel,Field
from typing import List
from openai_oci_client import OciOpenAILangChainClient

# SOURCE: https://python.langchain.com/docs/how_to/structured_output/#the-with_structured_output-method

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

LLM_MODEL = "openai.gpt-5" # cohere / meta-llama models does not support structured output
# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# openai.gpt-4.1
# openai.gpt-4ouv 
# xai.grok-4
# xai.grok-3
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

# In the following section, different output schemas are declared to be used with the models


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

reasoning = {
    "effort": "medium",  # 'low', 'medium', or 'high'
    "summary": "auto",  # 'detailed', 'auto', or None
}


# Step 2: Use the OciOpenAILangGraphClient from openai_oci_client.py to use output models
llm_client = OciOpenAILangChainClient(
    profile=scfg['oci']['profile'],
    compartment_id=scfg['oci']['compartment'],
    model=LLM_MODEL,
    service_endpoint= llm_service_endpoint,
    use_responses_api= True,
    reasoning=reasoning
)



MESSAGE = """
  Give me the information about the current science fiction books.
"""

# Call the LLM client using the output format
print(f"**************************Chat Response with JSON output **************************") 
# Method to bind the output
response = llm_client.invoke("my friend said he saw orange sky. what could be the reason? think and double check your answer for all possibilies, tell me top three")
# Calling the model
print(response)
