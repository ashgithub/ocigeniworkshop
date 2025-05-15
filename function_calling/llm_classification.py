#!/Users/ashish/anaconda3/bin/python

# Questions use #generative-ai-users  or ##igiu-innovation-lab slack channels
# if you have errors running sample code reach out for help in #igiu-ai-learning

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, EmbedTextDetails,CohereChatRequest, ChatDetails
import oci, json, os 

#####
#make sure your sandbox.json file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.json"

# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024
# meta.llama-3.1-405b-instruct
# meta.llama-3.3-70b-instruct
# meta.llama-3.2-90b-vision-instruct
# meta.llama-4-maverick-17b-128e-instruct-fp8
# meta.llama-4-scout-17b-16e-instruct

LLM_MODEL = "cohere.command-a-03-2025" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

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

def get_chat_request():
        cohere_chat_request = CohereChatRequest()
        cohere_chat_request.preamble_override = """
        
        You are a call classifier you carefully analyze teh question and classify it into one of the following categories. 
        you then return just the category in response
        
        categories: billing, outage, program, service
        
        eg: 
        question:  can i pay my bill by creditcard
        answer: billing
        question: i need to cancel my service as i am moving
        answer: service
        question: when will by power come back on?
        answer: outage
        
        """
        cohere_chat_request.is_stream = False 
        cohere_chat_request.max_tokens = 500
        cohere_chat_request.temperature = 0.75
        cohere_chat_request.top_p = 0.7
        cohere_chat_request.frequency_penalty = 1.0

        return cohere_chat_request

def get_chat_detail (llm_request,compartmentId):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail


#set up the oci gen ai client based on config 
scfg = load_config(SANDBOX_CONFIG_FILE)
config = oci.config.from_file(os.path.expanduser(scfg["oci"]["configFile"]),scfg["oci"]["profile"])

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))
chat_request = get_chat_request();
llm_payload =get_chat_detail(chat_request,scfg["oci"]["compartment"])

llm_payload.chat_request.message = "why is my bill so high"

llm_response = llm_client.chat(llm_payload)
llm_text = llm_response.data.chat_response.text
        
print (llm_text)