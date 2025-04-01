#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
# if you have errors running sample code reach out for help in #igiu-ai-learning
# sdk code : https://github.com/oracle/oci-python-sdk/blob/22fd62c8dbbd1aaed6b75754ec1ba8a3c16a4e5a/src/oci/generative_ai_inference/models/


import oci

import json, os 

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"
#LLM_MODEL = "meta.llama-3.1-70b-instruct" 
LLM_MODEL = "meta.llama-3.2-90b-vision-instruct" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


PREAMBLE = None
MESSAGE = "what is the capital of France?"


llm_client = None
llm_payload = None


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



def get_message(prompt):
        content = oci.generative_ai_inference.models.TextContent()
        content.text = prompt
        message = oci.generative_ai_inference.models.UserMessage()
        message.content = [content] 

        return [message]

def get_chat_request():
        chat_request = oci.generative_ai_inference.models.GenericChatRequest()
        chat_request.preamble_override = PREAMBLE
        chat_request.messages = get_message(MESSAGE) 
        chat_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
        chat_request.num_generations = 1
        chat_request.is_stream = False 
        chat_request.max_tokens = 500
        chat_request.temperature = 0.75
        chat_request.top_p = 0.7
        chat_request.top_k = -1 
        chat_request.frequency_penalty = 1.0

        return chat_request

def get_chat_detail (llm_request,compartmentId):
        chat_detail = oci.generative_ai_inference.models.ChatDetails()
        chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail



#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])


llm_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
llm_payload =get_chat_detail(get_chat_request(),scfg["oci"]["compartment"])

llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.choices[0].message.content[0].text
print (llm_text)
