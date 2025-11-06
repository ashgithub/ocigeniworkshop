from dotenv import load_dotenv
from envyaml import EnvYAML
#!/Users/ashish/anaconda3/bin/python

# HTML server send events SSE: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
# python https://medium.com/@nandagopal05/server-sent-events-with-python-fastapi-f1960e0c8e4b
# https://www.danielcorin.com/posts/2024/lm-streaming-with-sse/

# Questions use #generative-ai-users  or #igiu-innovation-lab slack channels
# if you have errors running sample code reach out for help in #igiu-ai-learning

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, CohereChatRequest, ChatDetails
import oci
import json,os

#####
#make sure your sandbox.yaml file is setup for your environment. You might have to specify the full path depending on  your `cwd` 
#####
SANDBOX_CONFIG_FILE = "sandbox.yaml"
load_dotenv()

# available models : https://docs.oracle.com/en-us/iaas/Content/generative-ai/chat-models.htm
# cohere.command-a-03-2025
# cohere.command-r-08-2024
# cohere.command-r-plus-08-2024



LLM_MODEL = "cohere.command-r-08-2024" 

llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


PREAMBLE = """
        you always answer in a one stanza poem.
"""
MESSAGE = """
        why is the skyblue
"""



def load_config(config_path):
    """Load configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
                return EnvYAML(config_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return None
def get_chat_request():
        llm_chat_request = CohereChatRequest()
        llm_chat_request.preamble_override = PREAMBLE 
        llm_chat_request.message = MESSAGE
        llm_chat_request.is_stream = True 
        llm_chat_request.max_tokens = 500 # max token to generate, can lead to incomplete responses
        llm_chat_request.temperature = 1.0 # higer value menas more randon, defaul = 0.3
        llm_chat_request.seed = 7555 # makes the best effort to make answer determininstic , not gaureented 
        llm_chat_request.top_p = 0.7  # ensures only tokens with toptal probabely of p are considered, max value = 0.99, min 0.01, default 0.75
        llm_chat_request.top_k = 0  #Ensures that only top k tokens are considered, 0 turns it off, max = 500
        llm_chat_request.frequency_penalty = 0.0 # reduces the repeatedness of tokens max value 1.9=0, min 0,0

        return llm_chat_request



def get_chat_detail (llm_request,compartmentId):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail
    
    
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


## Print with streaming result
print("**************************Generate Texts WithStreaming Result**************************")
for event in llm_response.data.events():
    res = json.loads(event.data)
    if 'finishReason' in res.keys():
        print(f"\nFinish reason: {res['finishReason']}")
        break
    if 'text' in res:
        print(res['text'], end="", flush=True)
    # Add timestamp:
    # print("{} {}".format(datetime.datetime.now(), json.loads(event.data)))
print("\n")