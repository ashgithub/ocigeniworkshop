"""
What this file does:
Demonstrates single-step function calling using OCI Generative AI Cohere models. Shows how to define tools, make tool calls, and provide tool results to get a final response.

Documentation to reference:
- OCI Gen AI: https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm
- Cohere Command Models: https://docs.cohere.com/docs/command-r
- OCI Python SDK: https://github.com/oracle/oci-python-sdk/tree/master/src/oci/generative_ai_inference

Relevant slack channels:
- #generative-ai-users: for questions on OCI Gen AI
- #igiu-innovation-lab: general discussions on your project
- #igiu-ai-learning: help with sandbox environment or help with running this code

Env setup:
- sandbox.yaml: Contains OCI config, compartment, and other details.
- .env: Load environment variables (e.g., API keys if needed).

How to run the file:
uv run function_calling/single_step_demo.py

Comments to important sections of file:
- Step 1: Define tool specifications and make initial chat request with tools.
- Step 2: Provide tool results and get the final response.
- Experiment: Try changing tool outputs (e.g., "out of stock") and observe model behavior.
"""

from dotenv import load_dotenv
from envyaml import EnvYAML

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import CohereChatRequest, ChatDetails
import oci

import json
import os

SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# available models with tool calling support
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# cohere.command-a-03-2025

#LLM_MODEL = "cohere.command-r-16k" 
LLM_MODEL = "cohere.command-a-03-2025" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])    

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))

item_param = oci.generative_ai_inference.models.CohereParameterDefinition()
item_param.description = "the item requested to be purchased, in all caps eg. Bananas should be BANANAS"
item_param.type = "str"
item_param.is_required = True

quantity_param = oci.generative_ai_inference.models.CohereParameterDefinition()
quantity_param.description = "how many of the items should be purchased"
quantity_param.type = "int"
quantity_param.is_required = True

shop_tool = oci.generative_ai_inference.models.CohereTool()
shop_tool.name = "personal_shopper"
shop_tool.description = "Returns items and requested volumes to purchase"
shop_tool.parameter_definitions = {
    "item": item_param,
    "quantity": quantity_param
}

# Step 1: Define tool specifications and make initial chat request with tools
chat_request = oci.generative_ai_inference.models.CohereChatRequest()
chat_request.message = "I'd like 4 apples and a fish please"
chat_request.max_tokens = 600
chat_request.is_stream = False
chat_request.is_force_single_step = True
chat_request.tools = [shop_tool]

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
chat_detail.compartment_id = scfg["oci"]["compartment"]
chat_detail.chat_request = chat_request

chat_response = llm_client.chat(chat_detail)

# Print result
print("**************************Step 1 Result**************************")
print(vars(chat_response))

# Step 2: Provide tool results and get the final response
chat_request.tool_results = []
i=0
for call in chat_response.data.chat_response.tool_calls:
    tool_result = oci.generative_ai_inference.models.CohereToolResult()
    tool_result.call = call
    # try to change response to out of stock etc for one or both items and see
    if  i == 0 : 
        tool_result.outputs = [ { "response": "Completed, in stock" } ] 
        i= i+1
    else :
       tool_result.outputs = [ { "response": "Sorry , out of  stock" } ]  
    chat_request.tool_results.append(tool_result)

chat_response = llm_client.chat(chat_detail)

# Print result
print("**************************Step 2 Result**************************")
print(vars(chat_response))
