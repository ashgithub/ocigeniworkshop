#!/Users/ashish/anaconda3/bin/python
# Questions use #generative-ai-users  or #igiu-innovation-lab slack channel
# if you have errors running sample code reach out for help in #igiu-ai-learnin
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci

import json, os 

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

# available models with tool calling support
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024

LLM_MODEL = "cohere.command-r-16k" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



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
    

#set up the oci gen ai client based on config 
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

# Step 1, describe the tool spec

chat_request = oci.generative_ai_inference.models.CohereChatRequest()
chat_request.message = "I'd like 4 apples and a fish please"
chat_request.max_tokens = 600
chat_request.is_stream = False
chat_request.is_force_single_step = True
chat_request.tools = [ shop_tool ]

chat_detail = oci.generative_ai_inference.models.ChatDetails()
chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
chat_detail.compartment_id = scfg["oci"]["compartment"]
chat_detail.chat_request = chat_request



chat_response = llm_client.chat(chat_detail)

# Print result
print("**************************Step 1 Result**************************")
print(vars(chat_response))

# Step 2, provide the tool results and get the final response
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