from dotenv import load_dotenv
from envyaml import EnvYAML
#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels

# if you have errors running sample code reach out for help in #igiu-ai-learning

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import *
import oci
import json, os

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024


LLM_MODEL = "cohere.command-r-08-2024" # response schema is only supported for cohere models. Also the support is for models 08-2024 and later

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

PREAMBLE = """
       answer in JSON only 
"""
MESSAGE = """
  generate a list if 3 science fiction books 
"""

# see documentation here : https://docs.cohere.com/docs/structured-outputs-json#schema-constraints
RESPONSE_SCHEMA1 = {
            "type": "object",
            "required": ["title", "author", "publication_year"],
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
                "publication_year": {"type": "integer"},
            },
        }
RESPONSE_SCHEMA2 =  {
            "type": "object",
            "required": ["authors"],
            "properties" : {
                "authors" : {
                        "type" : "array",
                        "items" : {
                                "type" : "object",
                                "required": ["title", "author", "publication_year"],
                                "properties": {
                                        "title": {"type": "string"},
                                        "author": {
                                                "type": "object",
                                                "required" : ["fname", "lname"],
                                                "properties" : {
                                                        "fname" : {"type":"string"},       
                                                        "lname" : {"type":"string"}
                                                }
                                        },
                                        "publication_year": {"type": "integer"}
                                }
                        }        
                }
            }
        }

def get_chat_request():
        llm_chat_request = CohereChatRequest()
        llm_chat_request.preamble_override = PREAMBLE 
        llm_chat_request.message = MESSAGE
        llm_chat_request.is_stream = False 
        llm_chat_request.max_tokens = 500 # max token to generate, can lead to incomplete responses
        llm_chat_request.temperature = 1.0 # higer value menas more randon, defaul = 0.3
        llm_chat_request.seed = 7555 # makes the best effort to make answer determininstic , not gaureented 
        llm_chat_request.top_p = 0.7  # ensures only tokens with toptal probabely of p are considered, max value = 0.99, min 0.01, default 0.75
        llm_chat_request.top_k = 0  #Ensures that only top k tokens are considered, 0 turns it off, max = 500
        llm_chat_request.frequency_penalty = 0.0 # reduces the repeatedness of tokens max value 1.9=0, min 0,0
        
        llm_chat_request.response_format = CohereResponseTextFormat()

        return llm_chat_request



def get_chat_detail (llm_request,compartmentId):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail

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

chat_request = get_chat_request();
llm_payload =get_chat_detail(chat_request,scfg["oci"]["compartment"])

llm_response = llm_client.chat(llm_payload)

# Print result
print("**************************Chat Result - text format, json in prompt *************************")
llm_text = llm_response.data.chat_response.text
        
print (llm_text)

print("**************************Chat Result - JSON format, no schema *************************")

chat_request.response_format = CohereResponseJsonFormat()
llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.text
print (llm_text)

print("**************************Chat Result - JSON format with simple schema *************************")
print("* only one result, even though we asked for more. its because scheme restricted it\n\n"); 
chat_request.response_format = CohereResponseJsonFormat(schema = RESPONSE_SCHEMA1)
llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.text
print (llm_text)

print("**************************Chat Result - JSON format with nested schema *************************")
chat_request.response_format = CohereResponseJsonFormat(schema = RESPONSE_SCHEMA2)
llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.text
print (llm_text)
        